# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:27:50 2025

@author: mm07

Get parameters (name, value, range, distribution) from file.

"""

import pandas as pd
import numpy as np

def read_params(file):
    """
    Take the parameter list excel sheet as input and 
    output params and params ranges as an array.

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.

    Returns
    -------
    params: dict
        dictionary of parameters, default values, distribution, and
        lower and upper bounds.

    """
    
    #Reading the list of parameter bounds from the file
    df = pd.read_excel(file)
    short = df[['Parameter', 'Default value', 'Distribution', 'Lower bound', 'Upper bound']]
    params = short.to_dict('records')

    return params

#p = read_params("parameter_list.xlsx")
