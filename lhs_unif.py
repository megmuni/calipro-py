# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 14:53:22 2025

@author: mm07

Latin Hypercube Sampling (LHS) from uniform distribution

"""
import pandas as pd
import numpy as np
from scipy.stats import qmc
#from read_params import read_params

def lhs_unif(nsample, params, p):
    """
    Samples parameter values using Latin Hypercube Sampling

    Parameters
    ----------
    nsample : int
        sample size.
    params : ndarray
        ndarray that comes from read_params.
    p : string
        which parameter (e.g., m1) to run sampling on.

    Returns
    -------
    sample_scaled : vector
        a vector of size nsample with random values selected,
        using the LHS algorithm.

    """
    nparams = params.shape[0]
    
    sampler = qmc.LatinHypercube(d = nparams) #run LHS on nsample parameters
    sample = sampler.random(n = nsample) #how many sample sets to create (n model runs)
    
    for line in params:
        if line[0] == p:
            d = line[1] # gets distribution type
            l_b = line[2] # gets lower bound
            u_b = line[3] # gets upper bound
    
    if d == 'Logarithmic':
        l_b = np.log(l_b)
        u_b = np.log(u_b)
        sample_scaled = np.exp(l_b + sample * (u_b - l_b))
        #sample_scaled = qmc.scale(sample, l_b, u_b)
        #sample_scaled[:, 0] = np.exp(sample_scaled[:, 0])
    elif d == 'Linear' or d == 'Discrete':
        sample_scaled = qmc.scale(sample, l_b, u_b)
    
    return sample_scaled

#params = read_params("parameter_list.xlsx")
#s = lhs_unif(50, params, 'p8')


    
    
    
    
