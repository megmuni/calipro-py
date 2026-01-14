# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 14:23:49 2026

@author: mmunip

This file makes all the necessary matrices

"""
import numpy as np
from lhs_unif import lhs_unif


def define_run_matrices(modelSettings):
    """
    

    Parameters
    ----------
    modelSettings : object
        contains the settings for a model run.

    Returns
    -------
    None.

    """
    
    paramMatrix = defineMatrix(modelSettings.params, modelSettings.NR, 'parameter')
    
    # Update parameter and initial condition matrices for any computed params
    # or computed initial conditions
    ### NOT USED ###
    
    # construct LHS matrix for PRCC analysis
    LHSmatrix = [];
    PRCC_var = {};
    [LHSmatrix, PRCC_var] = define_lhs_matrix(modelSettings.params, paramMatrix, LHSmatrix, PRCC_var)
    
    return paramMatrix, LHSmatrix, PRCC_var


def defineMatrix(items, nsamples, item_type):
    """
    

    Parameters
    ----------
    items : ndarray
        numpy array of parameters
    nsamples : number of samples/model runs (modelSettings.NR)
        DESCRIPTION.
    itemType : string
        defines what item is being used to make the matrix.

    Returns
    -------
    matrix : Numpy array

    """
    
    item_count = len(items)
    matrix = np.zeros((nsamples, item_count))
    
    for i in range(item_count):
        item = items[i]
        matrix[:, i] = get_sample_values(item, nsamples, item_type, i)
    
    return matrix

def get_sample_values(item, nsamples, item_type, item_index):
    """
    
    Get a vector of nsamples values for an item based on its distribution
    
    Parameters:
    -----------
    item : numpy.ndarray
        Array with 4 elements: [name, distribution_string, param1, param2]
    nsamples : int
        Number of samples to generate
    item_type : str
        Type identifier for error messages
    item_ordinal : int
        Item index/ordinal for error messages
    
    Returns:
    --------
    numpy.ndarray
        Vector of sample values with length nsamples
    
    Raises:
    -------
    ValueError
        If the distribution code is invalid
        
    """
    # Check if distribution string is empty or None
    if not item[1] or item[1] == '':
        # No distribution - use constant value
        sample_values = np.ones(nsamples) * item[2]
    
    elif item[1] == 'Logarithmic' or item[1] == 'Discrete' or item[1] == 'Linear':
        # available distribution option
        sample_values = lhs_unif(item[2], item[3], nsamples, False)
    
    else:
        # Invalid distribution code
        msg = f"{item_type} {item_index} {item[0]} has invalid distribution '{item[1]}'"
        raise ValueError(msg)
    
    return sample_values


def define_lhs_matrix(items, item_matrix, lhs_matrix, prcc_var):
    """
    Update lhs_matrix and prcc_var with information for the varied items.
    
    Parameters:
    -----------
    items : list
        List where each element is a numpy array with 4 elements:
        [name, distribution_string, param1, param2]
    item_matrix : numpy.ndarray
        Matrix with shape (nsamples, len(items))
    lhs_matrix : numpy.ndarray
        Existing LHS matrix to append columns to
    prcc_var : list
        List of variable names for PRCC analysis
    
    Returns:
    --------
    tuple
        (lhs_matrix, prcc_var) - updated matrix and variable list
    """
    for i in range(len(items)):
        name = items[i][0]
        distribution = items[i][1]
        
        if distribution and distribution != '':
            # Item has a distribution, so it is varied
            # Append column from item_matrix to lhs_matrix
            lhs_matrix = np.column_stack([lhs_matrix, item_matrix[:, i]])
            prcc_var.append(name)
    
    return lhs_matrix, prcc_var

# pulse and initial condition-related functions (that make pulse or IC matrices) are not included
# in this python ABM version