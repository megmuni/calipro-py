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
                          each parameter.
            

    """

