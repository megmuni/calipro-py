# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 10:49:03 2025

@author: mm07

Settings file for CaliPro model run.

This file defines all items needed for the model. A separate file
contains the model to be run (e.g., equations for an ODE, or function calls
                              for an ABM).


"""
from types import SimpleNamespace
from read_params import read_params
#from default_output_labels import default_output_labels


def model_settings(param_file="parameters.xlsx"):
    """
    This is a settings file for the model being calibrated using CaliPro.

    You can edit the the number of runs, time points to analyze, add or
    Parameter ranges, distributions and which params vary are set in the
    parameter sheet (see read_params).
    
    Parameters
    ----------
    param_file : str, optional, default "parameters.xlsx"
        path to the parameter excel sheet


    Returns
    -------
    m : SimpleNamespace.
        equivalent of MATLAB 'structure' with the following
        attributes/members:
            NR -- number of times to run the model
            tspan -- vector of time points / number of ticks to run model
            analysisTimePoints -- vector of time points / number of ticks to
                                  perform analysis for
            parameters -- dict of varied params from read_params:
                      {name: {'distribution', 'lower', 'upper'}}.
                      CaliPro updates the bounds each iteration.
            fixed -- dict of fixed params from read_params {name: value}
            outputLabels -- array with string labels for each model output.
                            usually use the default of O1, O2,
            
            

    """
    m = SimpleNamespace()
    
    #sample size / number of times to run the model per iteration
    m.NR = 10
    
    #time span of the simulation
    t_end = 7 # length of simulation in days (21 for full runs)
    t_ticks = t_end * 48 # each tick is 30 mins
    m.tspan = range(0, t_ticks + 1) #time points where output is calculated
    m.analysisTimePoints = range(0, t_ticks + 1)#time points of interest for uncertainty/SA

    # Get the model parameters: name, default value, distribution, upper bound, lower bound
    m.params, m.fixed = read_params(param_file)
    
    # at least 2 runs, or there is nothing to compare between pass and fail
    if m.NR < 2:
        raise ValueError(f"NR must be at least 2, got {m.NR}")
    # analysis ticks must be ticks the model records
    if not set(m.analysisTimePoints) <= set(m.tspan):
        raise ValueError("analysisTimePoints must all be in tspan")
    
    return m