# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 10:55:06 2025

@author: mmunip

File to evaluate model performance

"""

import numpy as np

def eval_model_performance(criteria, model_out, days, paramMatrix):
    """
    This function evaluates model performance by comparing model run outcomes
    against experimental data/pass criteria provided by the user. A run passes only
    if its run under each condition satisfies every criterion for that condition.
    Each replicate is a separate run and passes or fails on its own.

    Parameters
    ----------
    criteria : dict
        the pass set definition. Each criterion is either
        - a bound: {'output': column name, 'day': day, 'min': lower, 'max': upper}.
          Leave out 'min' or 'max' (or set to None) for a one-sided criterion,
          e.g. {'output': 'Total Cells', 'day': 21, 'max': 2000}.
        - a function f(model_out, days) returning a boolean per run, for
          trends and comparisons between outputs.

    model_out : dict
        {output name: timepoints x runs array}, from read_outputs.
        
    days : ndarray
        day of each timepoint (row), from read_outputs.
        
    paramMatrix : ndarray
        runs x varied params, from define_run_matrices (replicates repeated).


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

    # start with every run passing, then require each criterion
    passed = np.ones(paramMatrix.shape[0], dtype=bool)
    for cond, cond_criteria in criteria.items():
            out = model_out[cond]
            for criterion in cond_criteria:
                # function criteria (trends, comparisons) decide pass/fail themselves
                if callable(criterion):
                    ok = np.asarray(criterion(out, days), dtype=bool)
                    if ok.shape != passed.shape:
                        raise ValueError(f"{cond}: criterion {criterion} must return one "
                                         "True/False per sample")
                # bound criteria: one output on one day within min/max
                else:
                    ok = check_criterion(criterion, out, days)
                passed &= ok

    # split parameters and outputs into passed and failed samples
    passed_params = paramMatrix[passed]
    failed_params = paramMatrix[~passed]
    passed_runs = {cond: {name: o[:, passed] for name, o in out.items()}
                   for cond, out in model_out.items()}
    failed_runs = {cond: {name: o[:, ~passed] for name, o in out.items()}
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