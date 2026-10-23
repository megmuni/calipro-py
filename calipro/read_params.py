# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:27:50 2025

@author: mm07

Get parameters (name, value, range, distribution) from file.

"""

import pandas as pd

# sheet's Type codes -> lhs_unif distribution names
TYPE_TO_DIST = {
    1: 'Logarithmic',  # lognormal distribution
    2: 'Discrete',     # discrete lognormal distribution
    3: 'Linear',       # normal distribution (typically used for half-lives)
    4: 'Linear',       # uniform distribution
}

def read_params(file):
    """
    Take the parameter list excel sheet as input and 
    output params and params ranges as an array.

    Parameters
    ----------
    file : str
        path to the parameter excel sheet. Needs columns 'Parameter Name',
        'Mean', 'Lower', 'Upper', 'Type' and 'Vary?'.

    Returns
    -------
    params: dict
        {name: {'distribution': ..., 'lower': ..., 'upper': ...}} for every
        varied parameter (Vary? = blank or Y). Used by lhs_unif.
        
    fixed : dict
        {name: value} for every parameter not varied, using its Mean.

    """
    
    #Reading the list of parameter bounds from the file
    # read only the needed columns (ignores the Types legend beside the table)
    df = pd.read_excel(file, usecols=['Parameter Name', 'Mean', 'Lower',
                                  'Upper', 'Type', 'Vary?'])
    
    # catch any unknown Type codes that would otherwise fail later in lhs_unif
    unknown = set(df['Type']) - set(TYPE_TO_DIST)
    if unknown:
        raise ValueError(f"unknown Type code(s) {unknown}; expected {set(TYPE_TO_DIST)}")
        
    # varied params are marked Y or blank (N means fixed)
    vary = df['Vary?'].fillna('Y').astype(str).str.strip().str.upper().isin(['Y', ''])
    
    # varied params: name -> distribution and bounds
    v = df[vary]
    params = {name: {'distribution': TYPE_TO_DIST[t],
                     'lower': float(lb), 'upper': float(ub)}
              for name, t, lb, ub in zip(v['Parameter Name'], v['Type'],
                                         v['Lower'], v['Upper'])}
   
    # fixed params: name -> Mean value
    f = df[~vary]
    fixed = dict(zip(f['Parameter Name'], f['Mean'].astype(float)))

    return params, fixed

#p = read_params("parameter_list.xlsx")
