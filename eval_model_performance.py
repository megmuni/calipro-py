# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 10:55:06 2025

@author: mmunip

File to evaluate model performance

"""
import pandas as pd
import numpy as np

def eval_model_performance(calibration_input, model_runs, pass_criteria):
    """
    This function evaluates model performance by comparing model run outcomes
    against experimental data provided by the user.

    Parameters
    ----------
    calibrationInput : Pandas dataframe?
        holds user input to calibration program.
    modelRuns : TYPE
        structure that holds modelRuns output from the 'run' function
        as well as other information such as paramMatrix.
    passCriteria : TYPE
        DESCRIPTION.

    Returns
    -------
    passedTotalModelRuns : a matrix that holds the runs that passed following
    comparison to user-provided data.
    passedTotalParams : a matrix holding the parameter values for the
    runs that passed following comparison to user-provided data.
    failedTotalModelRuns : a matrix that holds the runs that failed
    following comparison to user-provided data. 
    failedTotalParams : a matrix that holds the parameter values for the
    runs that failed following comparison to user-provided data. 


    """
    
    # temp vars for model output
    # model_out is a list where model_out[0] is output 1, model_out[1] is output 2, etc.
    # Each has shape (timesteps, number_of_runs)
    tnf_out = model_runs[0]
    il1b_out = model_runs[1]
    tgf_out = model_runs[2]
    coll_out = model_runs[3]
    agg_out = model_runs[4]
    totcells_out = model_runs[5]
    viable_out = model_runs[6]
    diff_out = model_runs[7]
    
    # temp vars for calibration input
    tnf_ds = calibration_input[0]
    il1b_ds = calibration_input[1]
    tgf_ds = calibration_input[2]
    coll_ds = calibration_input[3]
    agg_ds = calibration_input[4]
    totcells_ds = calibration_input[5]
    viable_ds = calibration_input[6]
    diff_ds = calibration_input[7]
    
    # how does the output perform against dataset?
    passed_agg_out, run_ix_agg_passed, run_ix_agg_failed = find_passed(agg_out, agg_ds, pass_criteria)
    passed_tgf_out, run_ix_tgf_passed, run_ix_tgf_failed = find_passed(tgf_out, tgf_ds, pass_criteria)
    passed_viable_out, run_ix_viable_passed, run_ix_viable_failed = find_passed(viable_out, viable_ds, pass_criteria)
    passed_diff_out, run_ix_diff_passed, run_ix_diff_failed = find_passed(diff_out, diff_ds, pass_criteria)
    
    # find the columns that are in common between the conditions
    common_ix_passed = [x for x in run_ix_agg_passed if x in run_ix_viable_passed and x in run_ix_diff_passed]
    common_ix_failed = run_ix_agg_failed + run_ix_viable_failed + run_ix_diff_failed
    
    # subset runs, LHS matrix, param matrix to include only the ones that passed
    passed_total_params = 
    
    
    
    
    
    
def find_passed(model_out, exp_data, pass_criteria):
    """
    Finds passed runs and collects pass/fail indices

    Parameters
    ----------
    model_out : 
        DESCRIPTION.
    exp_data : 
        DESCRIPTION.
    pass_criteria : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    run_ix_passed = [];
    run_ix_failed = [];
    
    # logical indexing to check if runs pass through the criteria
    logical_array_cond1 = model_out >= exp_data[:,0] / pass_criteria
    logical_array_cond2 = model_out <= exp_data[:,1] * pass_criteria
    logical_array_tot = logical_array_cond1 & logical_array_cond2
    
    for i in logical_array_tot:
        if i == 1:
            # cols with all ones -- passed the criteria
            run_ix_passed.append(logical_array_tot.index(i))
        elif i == 0:
            # cols with all zeroes -- failed the criteria
            run_ix_failed.append(logical_array_tot.index(i))
    
    # use run_ix_passed to pull those columns from the total runs matrix
    passed_runs = model_out[:, run_ix_passed]
    
    return passed_runs, run_ix_passed, run_ix_failed
        