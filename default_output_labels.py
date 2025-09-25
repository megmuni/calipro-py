# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 15:09:54 2025

@author: mmunip
"""

def default_output_labels(outputCount):
    """
    This function creates the default output labels (O1, O2) based on the
    number of desired output variables

    Parameters
    ----------
    outputCount : int
        number of output variables.

    Returns
    -------
    outputLabels : list

    """
    
    outputLabels = []
    
    for i in range(outputCount):
        outputLabels.append(f"O{i+1}")
        
    return outputLabels

