# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 14:53:22 2025

@author: mm07

Latin Hypercube Sampling (LHS) from uniform distribution

"""
import numpy as np
from scipy.stats import qmc

def lhs_unif(nsample, params, p, seed=None):
    """
    Samples parameter values using Latin Hypercube Sampling

    Parameters
    ----------
    nsample : int
        sample size
    params : ndarray
        dict that comes from read_params:
        {name: {'distribution': ..., 'lower': ..., 'upper': ...}}
    p : string
        which parameter (e.g., 'stem:apoptosis_chance') to run sampling on
    seed : int or np.random.Generator, optional, default None
        seed or generator, for reproducible samples

    Returns
    -------
    sample_scaled : vector
        a vector of size nsample with random values selected,
        using the LHS algorithm.

    """
    # find this parameter's distribution type and bounds
    if p not in params:
        raise ValueError(f"parameter '{p}' not found in params")
    d = params[p]['distribution']
    l_b, u_b = float(params[p]['lower']), float(params[p]['upper'])
    
    # bounds must define a range - check
    if l_b >= u_b:
        raise ValueError(f"{p}: lower bound {l_b} must be < upper bound {u_b}")
    
    # LHS for one parameter
    sampler = qmc.LatinHypercube(d=1, seed=seed)
    sample = sampler.random(n=nsample)[:, 0]
    
    # uniform in log space: equal weight to each order of magnitude
    if d == 'Logarithmic':
        if l_b <= 0:
            raise ValueError(f"{p}: log sampling needs positive bounds")
        sample_scaled = np.exp(np.log(l_b) + sample * (np.log(u_b) - np.log(l_b)))
    # uniform between lower and upper bound
    elif d == 'Linear':
        sample_scaled = l_b + sample * (u_b - l_b)
    # integers l_b..u_b inclusive, each equally likely
    elif d == 'Discrete':
        sample_scaled = np.floor(l_b + sample * (u_b - l_b + 1))
    else:
        raise ValueError(f"{p}: unknown distribution '{d}'")
    
    return sample_scaled


    
    
    
    
