# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:49:03 2025

@author: mm07

Settings file for CaliPro model run.

This file defines all items needed for the model. A separate file
contains the model to be run (e.g., equations for an ODE, or function calls
                              for an ABM).

"""

def model_settings():
    """
    This is a settings file for the model being calibrated using CaliPro.
    
    You can edit the the number of runs, time points to analyze, add or
    change ranges for the parameters, initial conditions and pulse items, as
    described in the comments below.
    
    This settings file does not vary the initial conditions. You can
    experiment with varying initial conditions by specifying a distribution
    to use (ex. 'u' instead of '') and values that specify a range (uniform
    'u' or log uniform 'lu' distribution) or that specify a mean and standard
    deviation (normal distribution, 'n').
    
    This settings file does not define pulse time points. Those are commented
    out.  You can experiment with pulse time points by uncommenting them and
    specify pulse time points and pulse values or ranges.
    

    Returns
    -------
    model : dict.
        equivalent of MATLAB 'structure' named model with the following
        attributes/members:
            NR -- number of times to run the model
            tspan -- vector of time points / number of ticks to run model
            analysisTimePoints -- vector of time points / number of ticks to
                                  perform analysis for
            modelHandle -- name of the file/function that contains the model
            computeParamsInitCondHandle -- name of a function for computing some
                                           params based on other params/init conds
            solverTimeLimit -- amount of time to allot for solving one set of
                               params. if it takes longer than this amount, the
                               solve is stopped and noted in an error variable.
                               in seconds; can be fractional
            saveOnError -- whether to save solution results when an error occurs
                           during a call to the MATLAB solver. 1=yes, 0=no
            parameters -- an array for specifying the parameters. one dict entry for
                          each parameter. contains the parameter's name, distribution,
                          and range.
                          
                          probability distribution is one of the following:
                              ''   No distribution, use the first value in the range.
                              both values must be the same.
                              'u'  Use a uniform dist with the 2 range values as min
                              and max. min < max
                              'lu' Use a log uniform dist with the 2 range values 
                              as min and max. min < max
                              'n' Use the 2 values as the mean and std for a 
                              normal distribution. stdev != 0
            initialConditions -- a dict for specifying the initial conditions.
                                 same format as the parameter array
            outputLabels -- array with string labels for each model output.
                            usually use the default of O1, O2,
            
            

    """
    
    #sample size
    

