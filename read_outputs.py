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
    tables = [pd.read_csv(f) for f in files]
 
    # all runs must record the same timepoints to be compared
    days = tables[0]['Day'].to_numpy()
    for f, t in zip(files, tables):
        if len(t) != len(days) or not np.allclose(t['Day'], days):
            raise ValueError(f"{f}: timepoints differ from {files[0]}")
 
    # one timepoints x runs array per output column
    model_out = {col: np.column_stack([t[col].to_numpy(dtype=float) for t in tables])
                 for col in tables[0].columns}
 
    return model_out, days
