# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:49:03 2025

@author: mm07

Settings file for CaliPro model run.

This file defines all items needed for the model. A separate file
contains the model to be run (e.g., equations for an ODE, or function calls
                              for an ABM).


"""

from read_params import read_params
from default_output_labels import default_output_labels

def model_settings(m):
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
    model : object.
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
    
    class model:
        pass
    
    m = model()
    
    #sample size / number of times to run the model
    m.NR = 10
    
    #time span of the simulation
    t_end = 5 # length of simulation in days
    t_ticks = t_end * 48 # each tick is 30 mins
    m.tspan = range(1, t_ticks) #time points where output is calculated
    m.analysisTimePoints = range(1, t_ticks)#time points of interest for uncertainty/SA
    
    # The alpha value to use for PRCC.
    # Undefine this (comment out) if no PRCC is to be performed.
    
    # Doing PRCC is generally used for production runs.
    # Not doing PRCC can be useful for testing and debugging the code which
    # reads a settings file like this one and runs the model.
    # model_alpha = 0.01;
    
    # Set saveOnError to define how to handle the case where the ODE solver
    # fails. saveOnError = 1 means to pad the output matrix for the solution
    # time steps that were not defined. saveOnError = 0 means dont' pad the
    # output matrix.
    m.saveOnError = 0;
    
    # A function handle for the Matlab ODE model to analyze.
    # For example: odeModelHandle = @ODEmodel;
    #
    # Be sure to spell this correctly, and that the file containing this
    # function exists and is on the Matlab path.
    #
    # Don't put it in quotes, ex. odeModelHandle = '@ODEmodel';
    # is not correct.
    #
    #m.modelHandle = @lhs_ode_predator_prey_ode_c;
    
    # Get the model parameters: name, default value, distribution, upper bound, lower bound
    m.params = read_params("parameter_list.xlsx")
    
    # Labels to use for model outputs.
    #
    # The default labels are 'O1', 'O2', ..., 'On' where n is the number of
    # model outputs
    m.outputLabels = default_output_labels(9);
    
    return m;
    
    
    
    
    
    
    
    
    

