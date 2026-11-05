# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 10:55:06 2025

@author: mmunip

File to evaluate model performance

"""

import numpy as np

def eval_model_performance(criteria, model_out, days, paramMatrix, reps, rep_pass_fraction):
    """
    This function evaluates model performance by comparing model run outcomes
    against experimental data/pass criteria provided by the user. A run passes only
    if its run under each condition satisfies every criterion for that condition.
    Each replicate is a separate run and passes or fails on its own

    Parameters
    ----------
    criteria : dict
        the pass set definition. Each criterion is either
        - a bound: {'output': column name, 'day': day, 'min': lower, 'max': upper}.
          Leave out 'min' or 'max' (or set to None) for a one-sided criterion,
          e.g. {'output': 'Total Cells', 'day': 21, 'max': 2000}
        - a function f(model_out, days) returning a boolean per run, for
          trends and comparisons between outputs

    model_out : dict
        {output name: timepoints x runs array}, from read_outputs

    days : ndarray
        day of each timepoint (row), from read_outputs

    paramMatrix : ndarray
        runs x varied params, from define_run_matrices (replicates repeated)

    reps : int
        replicates per parameter set

    rep_pass_fraction : float
        fraction of a parameter set's replicates that must pass a condition
        for the set to pass it (e.g. 2/3)

    Returns
    -------
    passed_params : ndarray
        parameter values (rows of paramMatrix) for the runs that passed.

    passed_runs : dict
        {output name: timepoints x passed runs} model output of passed runs.

    failed_params : ndarray
        parameter values (rows of paramMatrix) for the runs that failed.

    failed_runs : dict
        {output name: timepoints x failed runs} model output of failed runs.

    """
    # every condition run must have criteria, and every criteria set a run
    if set(criteria) != set(model_out):
        raise ValueError(f"criteria are for conditions {sorted(criteria)}, but runs are "
                         f"for {sorted(model_out)}; they must match")

    nruns = paramMatrix.shape[0]
    if nruns % reps != 0:
        raise ValueError(f"{nruns} runs is not a whole number of sets of {reps} replicates")
    nsets = nruns // reps

    # replicates needed per set for a set to pass, e.g. 2 of 3 for 2/3
    needed = int(np.ceil(rep_pass_fraction * reps - 1e-9))

    # start with every parameter set passing, then require each condition
    set_passed = np.ones(nsets, dtype=bool)
    for cond, cond_criteria in criteria.items():
        out = model_out[cond]

        # which runs (replicates) pass every criterion of this condition
        run_passed = np.ones(nruns, dtype=bool)
        for criterion in cond_criteria:
            # function criteria (trends, comparisons) decide pass/fail themselves
            if callable(criterion):
                ok = np.asarray(criterion(out, days), dtype=bool)
                if ok.shape != run_passed.shape:
                    raise ValueError(f"{cond}: criterion {criterion} must return one "
                                     "True/False per run")
            # bound criteria: one output on one day within min/max
            else:
                ok = check_criterion(criterion, out, days)
            run_passed &= ok

        # a set passes this condition if enough of its replicates (consecutive runs) pass
        set_passed &= run_passed.reshape(nsets, reps).sum(axis=1) >= needed

    # one row per parameter set, for the densities and termination check
    set_params = paramMatrix[::reps]
    passed_params = set_params[set_passed]
    failed_params = set_params[~set_passed]

    # model output of every replicate, split by whether its set passed
    run_mask = np.repeat(set_passed, reps)
    passed_runs = {cond: {name: o[:, run_mask] for name, o in out.items()}
                   for cond, out in model_out.items()}
    failed_runs = {cond: {name: o[:, ~run_mask] for name, o in out.items()}
                   for cond, out in model_out.items()}

    return passed_params, passed_runs, failed_params, failed_runs

def at_day(model_out, days, output, day):
    """
    Value of one output on one day, for every run. Helper for writing
    function criteria, e.g. at_day(out, days, 'NP Cells', 21)

    Parameters
    ----------
    model_out : dict
        {output name: timepoints x runs array}
    days : ndarray
        day of each timepoint (row)
    output : str
        output column name
    day : float
        a recorded day

    Returns
    -------
    values : ndarray
        one value per run

    """
    # the output must exist in the model output files
    if output not in model_out:
        raise ValueError(f"output '{output}' not in model output")

    # the day must be a recorded timepoint
    row = np.flatnonzero(np.isclose(days, day))
    if row.size == 0:
        raise ValueError(f"day {day} not in model output")

    return model_out[output][row[0]]

def check_criterion(criterion, model_out, days):
    """
    Checks one criterion of the pass set definition for every run.

    Parameters
    ----------
    criterion : dict
        {'output', 'day', 'min' (optional), 'max' (optional)}
    model_out : dict
        {output name: timepoints x runs array}
    days : ndarray
        day of each timepoint (row)

    Returns
    -------
    ok : ndarray
        boolean, one per run: True if the run satisfies the criterion

    """
    # value of this output on that day, for every run
    values = at_day(model_out, days, criterion['output'], criterion['day'])

    # within the lower and/or upper bound
    ok = np.ones(values.size, dtype=bool)
    if criterion.get('min') is not None:
        ok &= values >= criterion['min']
    if criterion.get('max') is not None:
        ok &= values <= criterion['max']

    return ok
