# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:48:52 2025

@author: mmunip

Samples parameters, runs the ABM for each run and collects the output

"""
import os
from pathlib import Path
from ABM import create_sample_file, get_template_parameter_paths, prepare_workdir
from ABM import run_ABM as abm_run_ABM
from define_run_matrices import define_run_matrices
from read_outputs import read_outputs


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
        {output name: timepoints x runs array}. NaN for failed runs
    days : ndarray
        day of each timepoint (row)
    paramMatrix : ndarray
        runs x varied params (replicates repeated), from define_run_matrices
    names : list
        varied parameter names, in the column order of paramMatrix
    error_runs : list of dict
        {'run', 'message', 'id'} for each run that failed

    """
    print('\n=====================================')
    print(f'   ABM LHS Run {runIteration}')
    print('=======================================\n')

    # sample parameter sets (rows repeated for replicates)
    paramMatrix, names = define_run_matrices(modelSettings, rng)

    # folder for this iteration's configs, logs and outputs
    iter_dir = os.path.join(out_dir, f"iteration_{runIteration}")
    os.makedirs(iter_dir, exist_ok=True)

    # run the ABM once per row of paramMatrix
    files, error_runs = [], []
    for run in range(len(paramMatrix)):
        # progress display, 25 runs per line
        print(f'{run} ', end='', flush=True)
        if (run + 1) % 25 == 0:
            print()

        # full parameter set for this run: fixed values plus sampled values
        values = {**modelSettings.fixed, **dict(zip(names, paramMatrix[run]))}

        # run the ABM; a failed run is recorded and treated as a failed run
        try:
            files.append(run_ABM(modelSettings, values, run, iter_dir))
        except Exception as err:
            files.append(None)
            error_runs.append({'run': run, 'message': str(err), 'id': type(err).__name__})
    print()

    if error_runs:
        print(f'{len(error_runs)} of {len(paramMatrix)} runs failed (see logs in {iter_dir})')

    # collect every run's output into timepoints x runs arrays
    model_out, days = read_outputs(files)

    # runs must cover the time span set in model_settings
    if len(days) != len(modelSettings.tspan):
        raise ValueError(f"model output has {len(days)} timepoints, expected "
                         f"{len(modelSettings.tspan)} (check t_end and the ABM's run length)")

    return model_out, days, paramMatrix, names, error_runs


def run_ABM(modelSettings, values, run, iter_dir):
    """
    Run the external ABM once with the given parameter values, using the
    config writer and ABM call from ABM.py (ABM-NM-optimization repo).

    Parameters
    ----------
    modelSettings : SimpleNamespace
        settings from model_settings (base_config, condition, tspan).
    values : dict
        {parameter name: value} for every parameter (fixed and varied).
    run : int
        run index (row of paramMatrix).
    iter_dir : str
        folder for this iteration's runs.

    Returns
    -------
    biomarkers : str
        path to this run's Output_Biomarkers.csv.

    """
    template = Path(modelSettings.base_config)

    # private working directory, so runs never share an output file
    workdir = prepare_workdir(Path(iter_dir) / f"run{run}")
    config_file = workdir / "configFiles" / "simulation_config.json"

    # template parameters, in template order; every one needs a value
    names = get_template_parameter_paths(template)
    missing = [n for n in names if n not in values]
    if missing:
        raise KeyError(f"no value for template parameter(s) {missing}; check parameters.xlsx")

    # this run's config: the template with this run's values and scaffold condition
    create_sample_file([values[n] for n in names], template, config_file,
                       parameter_names=names, condition=modelSettings.condition)

    # run the ABM; raises if it exits with an error or writes no output
    # numticks = number of rows written (ticks 0..numticks-1), so it equals len(tspan)
    biomarkers = abm_run_ABM(config_file, numticks=len(modelSettings.tspan), workdir=workdir)

    return str(biomarkers)