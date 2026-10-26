# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:48:52 2025

@author: mmunip

Samples parameters, runs the ABM for each run and collects the output

"""

import json
import os
import subprocess
from pathlib import Path
from ABM import create_sample_file, get_template_parameter_paths, prepare_workdir
from calipro.define_run_matrices import define_run_matrices
from calipro.read_outputs import read_outputs
from calipro.run_task import run_task

# output file each run's ABM writes, inside its workdir
BIOMARKERS = Path("output") / "Output_Biomarkers.csv"
# file listing each array task's workdir, one per line (see run_task)
TASK_LIST = "tasks.txt"

def model_run(modelSettings, runIteration, rng, out_dir="output/Calibration"):
    """
    Setup and run of one CaliPro iteration: LHS sampling, ABM runs, output

    Parameters
    ----------
    modelSettings : SimpleNamespace
        settings from model_settings
    runIteration : int
        CaliPro iteration number (used for output folder names)
    rng : np.random.Generator
        one shared generator for the whole calibration
    out_dir : str, optional
        folder where each iteration's run directories (config, logs, output) are kept

    Returns
    -------
    model_out : dict
        {condition: {output name: timepoints x samples array}}. NaN for failed runs
    days : ndarray
        day of each timepoint (row)
    paramMatrix : ndarray
        runs x varied params (replicates repeated), from define_run_matrices
    names : list
        varied parameter names, in the column order of paramMatrix
    error_runs : list of dict
        {'run', 'condition', 'message'} for each run that failed

    """
    print('\n=====================================')
    print(f'   ABM LHS Run {runIteration}')
    print('=======================================\n')

    # sample parameter sets (rows repeated for replicates)
    paramMatrix, names = define_run_matrices(modelSettings, rng)
    nruns = len(paramMatrix)
    conditions = modelSettings.conditions

    # folder for this iteration's configs, logs and outputs
    iter_dir = Path(out_dir) / f"iteration_{runIteration}"
    iter_dir.mkdir(parents=True, exist_ok=True)
    
    # every ABM run of this iteration: one per sample and condition
    tasks = [(run, cond) for run in range(nruns) for cond in conditions]
    
    # 1. prepare: one workdir and config per row of paramMatrix
    template_names = get_template_parameter_paths(Path(modelSettings.base_config))
    for run, cond in tasks:
        values = {**modelSettings.fixed, **dict(zip(names, paramMatrix[run]))}
        prepare_run(modelSettings, values, template_names, cond,
                    iter_dir / run_name(run, cond))

    # 2. execute
    if modelSettings.executor == "local":
       # one after another in this process (needs a GPU in this job)
        for t, (run, cond) in enumerate(tasks):
            print(f'{t} ', end='', flush=True)
            if (t + 1) % 25 == 0:
                print()
            try:
                run_task(iter_dir / run_name(run, cond))
            except Exception:
                pass  # recorded in the run's error.txt; collected below
        print()
    elif modelSettings.executor == "slurm":
        # one array task per run, each with its own GPU slice
        submit_array(modelSettings, iter_dir, len(tasks))
    else:
        raise ValueError(f"unknown executor '{modelSettings.executor}'; use 'local' or 'slurm'")
 
    # 3. collect: output file per run, or None (failed run) with the reason
    model_out, days, error_runs = {}, None, []
    for cond in conditions:
        files = []
        for run in range(nruns):
            workdir = iter_dir / run_name(run, cond)
            if (workdir / BIOMARKERS).exists():
                files.append(str(workdir / BIOMARKERS))
            else:
                files.append(None)
                t = tasks.index((run, cond))
                error_runs.append({'run': run, 'condition': cond,
                                   'message': failure_reason(workdir, iter_dir, t)})
 
        # this condition's outputs as timepoints x samples arrays
        model_out[cond], cond_days = read_outputs(files)
 
        # runs must cover the time span set in model_settings
        if len(cond_days) != len(modelSettings.tspan):
            raise ValueError(f"{cond}: model output has {len(cond_days)} timepoints, expected "
                             f"{len(modelSettings.tspan)} (check t_end and the ABM's run length)")
        days = cond_days
 
    if error_runs:
        print(f'{len(error_runs)} of {len(tasks)} ABM runs failed (see {iter_dir})')
 
    return model_out, days, paramMatrix, names, error_runs

def run_name(run, cond):
    """Workdir name of one ABM run: sample index and condition, e.g. run3_high."""
    return f"run{run}_{cond}"

def prepare_run(modelSettings, values, template_names, condition, workdir):
    """
    Set up one run's workdir: its config and a task.json describing how to
    run it (read by run_task, locally or in a Slurm array task).
 
    Parameters
    ----------
    modelSettings : SimpleNamespace
        settings from model_settings (base_config, tspan, world)
    values : dict
        {parameter name: value} for every parameter (fixed and varied)
    template_names : list
        tagged parameter names, in template order
    condition : str
        scaffold condition for this run ('high' or 'low')
    workdir : Path
        this run's folder
 
    Returns
    -------
    None.
 
    """
    # every template parameter needs a value
    missing = [n for n in template_names if n not in values]
    if missing:
        raise KeyError(f"no value for template parameter(s) {missing}; check parameters.xlsx")
 
    # private working directory, so runs never share an output file
    workdir = prepare_workdir(workdir)
    config_file = workdir / "configFiles" / "simulation_config.json"
 
    # remove anything left from an earlier attempt at this run
    for old in [workdir / BIOMARKERS, workdir / "error.txt"]:
        if old.exists():
            old.unlink()
 
    # this run's config: the template with this run's values and scaffold condition
    create_sample_file([values[n] for n in template_names], Path(modelSettings.base_config),
                       config_file, parameter_names=template_names,
                       condition=condition)
 
    # how to run it: numticks = number of rows written (ticks 0..numticks-1)
    task = {'config': str(config_file.resolve()), 'numticks': modelSettings.tspan[-1]}
    if getattr(modelSettings, 'world', None) is not None:
        task['world'] = list(modelSettings.world)
    with open(workdir / "task.json", "w") as f:
        json.dump(task, f, indent=2)
 
 
def submit_array(modelSettings, iter_dir, nruns):
    """
    Submit one Slurm array task per run and wait until all have finished.
 
    Parameters
    ----------
    modelSettings : SimpleNamespace
        settings from model_settings (job_script, array_cap).
    iter_dir : Path
        this iteration's folder (each task runs iter_dir/run{task id}).
    nruns : int
        number of runs (array tasks).
 
    Returns
    -------
    None.
 
    """
    # tasks 0..nruns-1, at most array_cap running at once; one log per task
    cmd = ["sbatch", "--wait", f"--array=0-{nruns - 1}%{modelSettings.array_cap}",
           f"--output={iter_dir}/slurm_%a.out", modelSettings.job_script, str(iter_dir)]
    print(f'Submitting {nruns} runs as a job array (at most {modelSettings.array_cap} at once)...')
    result = subprocess.run(cmd, capture_output=True, text=True)
 
    # submission itself failed (e.g. bad account or script): nothing ran
    if "Submitted batch job" not in result.stdout:
        raise RuntimeError(f"sbatch failed to submit the array:\n{result.stderr}")
 
    # --wait returns non-zero if any task failed; those runs are collected as failed
    print(f'Job array finished ({result.stdout.strip()})')
 
 
def failure_reason(workdir, iter_dir, run):
    """
    Why a run has no output: its error.txt if it got that far, otherwise
    point to its Slurm log (e.g. timed out, out of memory, never started).
    """
    err = workdir / "error.txt"
    if err.exists():
        return err.read_text().strip()
    return f"no output and no error.txt (see {iter_dir}/slurm_{run}.out)"