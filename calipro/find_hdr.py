# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 12:48:36 2025

@author: mm07

Calculates the Highest Density Region (HDR) according to the algorithm set forth
by Rob Hyndman in 1996. https://doi.org/10.1080/00031305.1996.10474359

"""
import numpy as np
from calipro.ks_density import ks_density

def find_hdr(passed, failed, coverage):
    """
    
    For a given set of parameter values, calculates the density distribution of
    those param values and calculates the HDR according to the Hyndman algorithm
    (1996).

    Parameters
    ----------
    passed : array
        array of number of passed runs x 1 (param that is being calculated to 
                                            find HDR)
    failed : array
        array of number of failed runs x 1 (same param as passedParamsVec that 
                                            is being calculated for HDR).
    coverage : float
        value that determines the region we are searching for. Value from 0-1,
        equal to value calibrationInput.portionParams

    Returns
    -------
    hdi -- 1x2 array, the HD interval. min and max param values that correspond
    to the HDR. used as min and max for this param for the next iteration of 
    sampling.
    
    x -- 1x100 array, x values (param values) shared by all density arrays,
    spanning the observed passed values.

    densPass -- 1x100 array, set of density values that describe the underlying
    pass dataset distribution

    densFail -- 1x100 array, set of density values that describe the underlying
    fail dataset distribution, zero outside the observed failed values (all
    zeros if there are no failed runs)

    densSub -- None. Returned so the outputs match find_ads.

    """
    # convert inputs (lists or column vectors) to flat float arrays
    passed = np.asarray(passed, dtype=float).ravel()
    failed = np.asarray(failed, dtype=float).ravel()
    
    # shared grid over the observed pass values
    x = np.linspace(passed.min(), passed.max(), 100)
    
    # kernel density of the passed parameter values
    densPass, _ = ks_density(passed, x)
    
    # no failed runs: fail density is zero everywhere
    if failed.size == 0:
        densFail = np.zeros_like(densPass)
    else:
        # kernel density of the failed parameter values on the same grid (for plotting)
        densFail, _ = ks_density(failed, x)
        # zero density outside the observed fail values
        densFail[(x < failed.min()) | (x > failed.max())] = 0
    
    # if all passed values identical, the range is that single value
    if passed.min() == passed.max():
        return np.array([passed.min(), passed.max()]), x, densPass, densFail, None
    
    # cumulative mass along the grid (same sum as the MATLAB loop), normalized to 1
    cuml = np.concatenate(([0.0], np.cumsum(np.diff(x) * densPass[1:])))
    cuml /= cuml[-1]
    
    # mass and width of every interval [x[i], x[j]]
    mass = cuml[None, :] - cuml[:, None]
    width = x[None, :] - x[:, None]
    
    # average density of intervals that reach the coverage; others excluded
    with np.errstate(divide="ignore", invalid="ignore"):
        score = np.where((width > 0) & (mass >= coverage), mass / width, -np.inf)
        
    # densest qualifying interval
    i, j = np.unravel_index(np.argmax(score), score.shape)
    hdi = np.array([x[i], x[j]])
    
    return hdi, x, densPass, densFail, None