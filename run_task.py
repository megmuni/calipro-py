# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 14:43:48 2026

@author: mm07

Runs one ABM execution from a workdir prepared by model_run

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
    # array task: run iteration_dir/run{task id}
    iter_dir, task_id = sys.argv[1], int(sys.argv[2])
    run_task(Path(iter_dir) / f"run{task_id}")