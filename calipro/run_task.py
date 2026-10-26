# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 14:43:48 2026

@author: mm07

Runs one ABM execution from a workdir prepared by model_run.

Used by model_run directly if local job, by calipro_array_job.sh
if slurm job.
    python -m calipro.run_task <iteration dir> <task id>

"""

import json
import sys
from pathlib import Path
from ABM import run_ABM

def run_task(workdir):
    """
    Run the ABM for one prepared run. On failure, the error is written to
    workdir/error.txt (so the driver can report it) and re-raised.
 
    Parameters
    ----------
    workdir : Path
        the run's folder, containing task.json and its config.
 
    Returns
    -------
    None.
 
    """
    workdir = Path(workdir)
    with open(workdir / "task.json") as f:
        task = json.load(f)
 
    # optional world size, only passed if set in model_settings
    kwargs = {'numticks': task['numticks'], 'workdir': workdir}
    if 'world' in task:
        kwargs['world'] = tuple(task['world'])
 
    try:
        run_ABM(Path(task['config']), **kwargs)
    except Exception as err:
        (workdir / "error.txt").write_text(f"{type(err).__name__}: {err}")
        raise
 
 
if __name__ == "__main__":
    # array task t: run the workdir on line t of the iteration's task list
    iter_dir, task_id = Path(sys.argv[1]), int(sys.argv[2])
    workdirs = (iter_dir / "tasks.txt").read_text().split()
    run_task(iter_dir / workdirs[task_id])
