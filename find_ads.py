# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 12:48:36 2025

@author: mm07

Narrows down the parameter range using Alternative Density Subtraction (ADS) 
according to the algorithm set forth by Louis Joslyn in 2020. 
https://doi.org/10.1007/s12195-020-00650-z

"""
import numpy as np
from ks_density import ks_density

def find_ads(passed, failed, coverage=None):
    """
    
    For a given set of parameter values, calculates the density distribution of
    those param values and calculates the ADS according to the Joslyn ADS algorithm
    (2020).

    Parameters
    ----------
    passed : array
        array of number of passed runs x 1 (param that is being calculated to 
                                            find ADS)
    failed : array
        array of number of failed runs x 1 (same param as passedParamsVec that 
                                            is being calculated for ADS).
    coverage : float, default None
        value that determines the region we are searching for. Value from 0-1,
        equal to value calibrationInput.portionParams

    Returns
    -------
    hdi -- 1x2 array, the HD interval. min and max param values that correspond
    to the ADS identified region of param space where more pass runs exist than
    failed runs. used as min and max for this param for the next iteration of 
    sampling.
    
    x -- 1x100 array, x values (param values) shared by all density arrays,
    spanning the observed passed values.
    
    densPass -- 1x100 array, set of density values that describe the underlying
    pass dataset distribution

    densFail -- 1x100 array, set of density values that describe the underlying
    fail dataset distribution, zero outside the observed failed values (all
    zeros if there are no failed runs)

    densSub -- 1x100 array, densPass minus densFail. positive where passed runs
    are denser than failed runs.

    """
    # convert inputs (lists or column vectors) to float arrays
    passed = np.asarray(passed, dtype=float).ravel()
    failed = np.asarray(failed, dtype=float).ravel()
    
    #find the density estimation of passed params
    densPass, x = ks_density(passed)
    # zero density outside the observed pass values (KDE grid extends past the data)
    densPass[(x < passed.min()) | (x > passed.max())] = 0
    
    #find density of the failed params
    if failed.size == 0:
        densFail = np.zeros_like(densPass)
    else:  #find the densities for the failed parameters
        # kernel density of the failed parameter values, on its own grid
        densFail_raw, xFail = ks_density(failed)
        # zero density outside the observed fail values
        densFail_raw[(xFail < failed.min()) | (xFail > failed.max())] = 0
        # put fail density on the pass grid so the subtraction compares like with like
        densFail = np.interp(x, xFail, densFail_raw, left=0, right=0)
    
    # positive where passed runs are denser than failed runs
    densSub = densPass - densFail
    # parameter values where passes dominate
    keep = x[densSub > 0]
    
    # fail density dominates everywhere: keep the current pass range
    if keep.size == 0:
        hdi = np.array([passed.min(), passed.max()])
    #put the min and max into the highest density interval output
    else:
        hdi = np.array([keep.min(), keep.max()])
    
    return hdi, x, densPass, densFail, densSub