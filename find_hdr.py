# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 12:48:36 2025

@author: mm07

Calculates the Highest Density Region (HDR) according to the algorithm set forth
by Rob Hyndman in 1996. https://doi.org/10.1080/00031305.1996.10474359

"""
import numpy as np
from ks_density import ks_density

def find_hdr(passedParamsVec, failedParamsVec, coverage):
    """
    
    For a given set of parameter values, calculates the density distribution of
    those param values and calculates the HDR according to the Hyndman algorithm
    (1996).

    Parameters
    ----------
    passedParamsVec : array
        array of number of passed runs x 1 (param that is being calculated to 
                                            find HDR)
    failedParamsVec : array
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
    xdensityPass -- 1x100 array, set of density values that describe the underlying
    pass dataset distribution
    xPass -- 1x100 array, x values that correspond to xdensityPass values.
    xdensityFail -- 1x100 array, set of density values that describe the underlying
    fail dataset distribution
    xFail -- 1x100 array, x values that correspond to xdensityFail values.

    """
    
    #find the density estimation
    xdensityPass, xPass = ks_density(passedParamsVec)
    
    #find the HDR (returned as the HDI, interval)
    best = 0 #counter to hold the best value as you iterate through
    for i in range(len(xPass) - 1):
        for j in range(i + 1, len(xPass)):
            mass = np.sum(np.diff(xPass[i:j]) * xdensityPass[i+1:j])
            if mass >= coverage and mass / (xPass[j] - xPass[i]) > best:
                best = mass / (xPass[j] - xPass[i])
                i_best = i
                j_best = j
    
    #return the x ranges for where the best i_ and j_ are found
    hdi = [xPass[i], xPass[j]]
    
    #if there are no failedParamsVec
    if len(failedParamsVec) == 0:
        xdensityFail = []  #make the density empty
        xFail = []  #make the x-values that go with the density empty too
    else:  #find the densities for the failed parameters as well
        xdensityFail, xFail = ks_density(failedParamsVec)
    
    return hdi, xdensityPass, xPass, xdensityFail, xFail