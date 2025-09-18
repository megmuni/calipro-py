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
    params : dict
        dictionary that comes from read_params.
    p : string
        which parameter (e.g., m1) to run sampling one.

    Returns
    -------
    sample_scaled : vector
        a vector of size nsample with random values selected,
        using the LHS algorithm.

    """
    sampler = qmc.LatinHypercube(d = nsample) #run LHS on nsample parameters
    sample = sampler.random(n = 50) #how many sample sets to create (n model runs)
    
    for line in params:
        if line['Parameter'] == p:
            d = line['Distribution']
            l_b = line['Lower bound']
            u_b = line['Upper bound']
    
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


    
    
    
    
