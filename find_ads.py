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

def find_ads(passedParamsVec, failedParamsVec, coverage):
    """
    
    For a given set of parameter values, calculates the density distribution of
    those param values and calculates the ADS according to the Joslyn ADS algorithm
    (2020).

    Parameters
    ----------
    passedParamsVec : array
        array of number of passed runs x 1 (param that is being calculated to 
                                            find ADS)
    failedParamsVec : array
        array of number of failed runs x 1 (same param as passedParamsVec that 
                                            is being calculated for ADS).
    coverage : float
        value that determines the region we are searching for. Value from 0-1,
        equal to value calibrationInput.portionParams

    Returns
    -------
    hdi -- 1x2 array, the HD interval. min and max param values that correspond
    to the ADS identified region of param space where more pass runs exist than
    failed runs. used as min and max for this param for the next iteration of 
    sampling.
    
    xdensityPass -- 1x100 array, set of density values that describe the underlying
    pass dataset distribution
    
    xPass -- 1x100 array, x values that correspond to xdensityPass values.
    
    xdensityFail -- 1x100 array, set of density values that describe the underlying
    fail dataset distribution
    
    xFail -- 1x100 array, x values that correspond to xdensityFail values.

    """
    
    #find the density estimation of passed params
    xdensityPass, xPass = ks_density(passedParamsVec)
    
    #find density of the failed params
    if len(failedParamsVec) == 0:
        xdensityFail = []  #make the density empty
        xFail = []  #make the x-values that go with the density empty too
    else:  #find the densities for the failed parameters
        xdensityFail, xFail = ks_density(failedParamsVec)
    
    #only keep values from density that are included in the bounds of original
    #parameter ranges:
    indicesPass = np.where(xPass < min(passedParamsVec) | xPass > max(passedParamsVec))
    xdensityPass[indicesPass] = 0
    
    indicesFail = np.where(xFail < min(failedParamsVec) | xFail > max(failedParamsVec))
    xdensityFail[indicesFail] = 0
    
    #subtract the failed from the passed:
    xdensitySub = xdensityPass - xdensityFail
    
    #find all points along range where passed runs are greater than failed
    #runs, so that we know the ranges where the runs (on the majority)
    #performed well:
    
    hdiRange = xPass[xdensitySub > 0]
    
    #put the min and max into the highest density interval output
    hdi = [min(hdiRange), max(hdiRange)]
    
    return hdi, xdensityPass, xPass, xdensityFail, xFail