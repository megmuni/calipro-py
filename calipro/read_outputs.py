# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 15:36:52 2026

@author: mmunip

This file reads the ABM output file (Output_Biomarkers.csv)
into the format used by eval_model_performance.


"""

import numpy as np
import pandas as pd

def read_outputs(files):
    """
 
    Parameters
    ----------
    files : list of str
        paths to the output csv of each run, in the same order as the rows
        of paramMatrix (file i is run i)
 
    Returns
    -------
    model_out : dict
        {output column name: timepoints x runs array}, one entry for every
        column in the output files (e.g. 'Total Cells')
    days : ndarray
        day of each timepoint (row), from the 'Day' column
 
    """
    # read every run's output table
    tables = [pd.read_csv(f) if f is not None else None for f in files]
    # strip stray spaces from column names (e.g. ' Total Cells')
    for t in tables:
        if t is not None:
            t.columns = [c.strip() for c in t.columns]
    ok = [t for t in tables if t is not None]
    if not ok:
        raise ValueError("no model output to read: every run failed")


    # all runs must record the same timepoints to be compared
    first = files[tables.index(ok[0])]
    days = ok[0]['Day'].to_numpy()
    for f, t in zip(files, tables):
        if t is not None and (len(t) != len(days) or not np.allclose(t['Day'], days)):
            raise ValueError(f"{f}: timepoints differ from {first}")

    # one timepoints x runs array per output column
    missing = np.full(len(days), np.nan)
    model_out = {col: np.column_stack([t[col].to_numpy(dtype=float) if t is not None else missing
                                   for t in tables])
             for col in ok[0].columns}

    return model_out, days
