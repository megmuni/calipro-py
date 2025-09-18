# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:12:09 2025

@author: mm07

From CaliPro MATLAB implementation 
(http://malthus.micro.med.umich.edu/CaliPro/):

ks_density_twice.m is a function that calls the ksdensity function twice 
with a slight change in bandwidth the second time.  We found, through
empirical research of comparing distribution histograms against the
built-in matlab ks density estimator, that  we needed to run the function
twice, but with the bandwidth prespecified to be 1/2 of what the embedded
selection process of the bandwidth is for the unedited version. 

Python's scipy uses a robust estimation of bandwith, not a default for normal
distributions like MATLAB, so for the Python implementation, we just run it once.

Kernel-based density estimation of the underlying data distribution.

"""

import numpy as np
from scipy import stats

def ks_density(paramVec):
    """

    Parameters
    ----------
    paramVec : array
        array of parameter values to correspond to either the pass or fail
        set of runs. (number of varied parameters by number of runs that satisfied
                      the criteria).

    Returns
    -------
    p, x : arrays
        p -- 1x100 array of density values for the underlying distribution
        x -- 1x100 array of datapoints to correspond to the density values

    """
    kde = stats.gaussian_kde(paramVec)
    x = np.linspace(paramVec.min(), paramVec.max(), 100)
    p = kde(x)
    
    return p, x