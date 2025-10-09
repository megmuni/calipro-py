# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 10:55:06 2025

@author: mmunip

File to evaluate model performance

"""

def eval_model_performance(calibrationInput, modelRuns, passCriteria):
    """
    This function evaluates model performance by comparing model run outcomes
    against experimental data provided by the user.

    Parameters
    ----------
    calibrationInput : TYPE
        holds user input to calibration program.
    modelRuns : TYPE
        structure that holds modelRuns output from the 'run' function
        as well as other information such as paramMatrix.
    passCriteria : TYPE
        DESCRIPTION.

    Returns
    -------
    passedTotalModelRuns : a mastric that holds the runs that passed following
    comparison to user-provided data.
    passedTotalParams : a matrix holding the parameter values for the
    runs that passed following comparison to user-provided data.
    failedTotalModelRuns : a matrix that holds the runs that failed
    following comparison to user-provided data. 
    failedTotalParams : a matrix that holds the parameter values for the
    runs that failed following comparison to user-provided data. 


    """
    
    # temp vars for model output
    
    
    # temp vars for calibration input
    
    
    # how does the output perform against dataset?
    