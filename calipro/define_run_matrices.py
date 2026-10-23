# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 14:23:49 2026

@author: mmunip

TThis file makes the param matrix for one CaliPro iteration.

"""
import numpy as np
from calipro.lhs_unif import lhs_unif


def define_run_matrices(modelSettings, rng=None):
    """
    Samples every varied parameter with LHS and builds the parameter matrix.

    Parameters
    ----------
    modelSettings : object
        contains the settings for a model run. Uses:
            modelSettings.params -- dict of varied params from read_params
            modelSettings.NR -- number of model runs (samples)
            modelSettings.reps -- replicate runs per parameter set
    rng : np.random.Generator, optional, default None
    one shared generator, so every parameter gets its own random stratum
    order and runs are reproducible.


    Returns
    -------
    paramMatrix : ndarray
        (NR * reps) x number of varied params. Row i is the parameter set
        for run i; each sampled set is repeated reps times in a row, so
        runs i*reps .. i*reps + reps-1 are the replicates of set i.

    names : list
        varied parameter names, in the same order as the columns of paramMatrix


    """
    
    # column order of the matrix
    names = list(modelSettings.params)
    if not names:
        raise ValueError("no varied parameters (check the Vary? column)")

    # one LHS column per varied parameter, all from the same generator
    paramMatrix = np.column_stack([lhs_unif(modelSettings.NR, modelSettings.params,
                                            p, seed=rng) for p in names])
    
    # one row per run: each parameter set repeated for its replicates
    paramMatrix = np.repeat(paramMatrix, modelSettings.reps, axis=0)

    return paramMatrix, names

# pulse and initial condition-related functions (that make pulse or IC matrices) and
# PRCC analysis-related functions are not included
# in this python-ABM CaliPro version