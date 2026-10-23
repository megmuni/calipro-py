# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:12:09 2025

@author: mm07

From CaliPro MATLAB implementation 
(http://malthus.micro.med.umich.edu/CaliPro/):

"ks_density_twice.m is a function that calls the ksdensity function twice 
with a slight change in bandwidth the second time.  We found, through
empirical research of comparing distribution histograms against the
built-in matlab ks density estimator, that  we needed to run the function
twice, but with the bandwidth prespecified to be 1/2 of what the embedded
selection process of the bandwidth is for the unedited version."

In Python, we use the default SciPy Gaussian KDE and halve the bandwidth to 
have the same effect as the original MATLAB method.

Kernel-based density estimation (KDE) of the underlying data distribution.

"""

import numpy as np
from scipy import stats

def ks_density(values, x=None, n_points=100):
    """

    Parameters
    ----------
    values : array
        array of parameter values to correspond to either the pass or fail
        set of runs. (number of runs x 1, for a single parameter)
        
    x : array, optional
        x values (params) at which to evaluate the density. if not given,
        uses a grid of n_points spanning the observed values
    
    n_points : int, optional, default 100 
        number of grid points when x is not given

    Returns
    -------
    p, x : arrays
        p -- 1x100 array of density values for the underlying distribution
        x -- 1x100 array of datapoints to correspond to the density values

    """
    
    # flatten input to a 1D float array
    values = np.asarray(values, dtype=float).ravel()
    
    # SciPy's default bandwidth factor, used only to compute the halved one
    factor = stats.gaussian_kde(values).factor
    # KDE with the bandwidth halved
    kde = stats.gaussian_kde(values, bw_method=factor / 2)
    
    # default grid spans the observed values
    if x is None:
        x = np.linspace(values.min(), values.max(), n_points)
    
    # density evaluated on the grid
    p = kde(x)
    
    return p, x