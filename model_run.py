# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:48:52 2025

@author: mmunip

Setup & running main routine

"""
import subprocess
import sys
import csv
import os
import numpy as np
from define_run_matrices import define_run_matrices


def model_run(modelSettings, runIteration):
    """
    Setup and run of an LHS analysis of a model - main routine

    Parameters
    ----------
    odeSettings : string
        file name that contains the definitions of the LHS settings needed by 
        this script.
    runIteration : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    # Declare variables
    odeOut = {}
    totalPrcc = []
    totalSign = [] #assignin('base', 'totalSign', totalSign);
    totalPrccSignEval = [] #assignin('base', 'totalPrccSignEval',totalPrccSignEval);
    paramMatrix = [] #assignin('base', 'paramMatrix', paramMatrix);
    #icMatrix = [] #assignin('base', 'icMatrix', icMatrix);
    #pulseMatrix = [] #assignin('base', 'pulseMatrix', pulseMatrix);
    LHSmatrix = [] #assignin('base', 'LHSmatrix', LHSmatrix);
    PRCC_var = [] #assignin('base', 'PRCC_var', PRCC_var);
    
    CalibrationOutput = {}
    
    error_runs = {};
    
    print('\n=====================================\n');
    print('   ABM LHS Run %d', runIteration);
    print('\n=====================================\n');
    
    # Build parameter matrix
    
    paramMatrix, LHSmatrix, PRCC_var = define_run_matrices(modelSettings)
    
    # perform the NR model runs
    for run in range(1, modelSettings.NR):
        print(f'{run} ', end='', flush=True)
        
        if run % 25 == 0:
            print()
        
        run_parameters = paramMatrix[run, :]
       # y0 = icMatrix[run, :] would be used if there were initial conditions to be varied
       
        try:
             if not hasattr(modelSettings, 'pulseTimePoints'):
                 # Not pulsing ODE conditions, just run the model
                 t, y, saved_warn_msg, saved_warn_id = run_ABM(
                     run, modelSettings, run_parameters, modelSettings.tspan
                 )
             # else:
             #     # Pulsing ODE conditions. Update the initial conditions at the
             #     # pulse time step.
                 
             #     # For getting pulse amounts. y0 is updated after each solver
             #     # call, so we need to save the initial conditions
             #     y0_initial = y0.copy()
                 
             #     # Solve for the time steps up to just before the first pulse
             #     pre_tspan = ode_settings['tspan'][:ode_settings['pulseTimePointIdx'][0]]
             #     t, y, saved_warn_msg, saved_warn_id = run_ABM(
             #         ode_settings, run_parameters, y0, pre_tspan
             #     )
                 
             #     # Only do the pulses if the initial model call succeeded
             #     if len(t) == len(pre_tspan):
                     
             #         # Initial conditions for first pulse call
             #         y0 = y[-1, :]
                     
             #         for i in range(len(ode_settings['pulseTimePointIdx'])):
                         
             #             # ptpidx and ptpidx_next are indices into tspan
             #             ptpidx = ode_settings['pulseTimePointIdx'][i]
             #             if i < len(ode_settings['pulseTimePointIdx']) - 1:
             #                 # About to do the next pulse. Solve to the time point
             #                 # just before the time point of the next pulse
             #                 ptpidx_next = ode_settings['pulseTimePointIdx'][i + 1] - 1
             #             else:
             #                 # About to do the last pulse. Solve to the end
             #                 ptpidx_next = len(ode_settings['tspan']) - 1
                         
             #             # Pulse
             #             # pulse_matrix is 3D, so pulse_matrix[run, i, :] gives pulse vector
             #             pulse_vector = pulse_matrix[run, i, :].reshape(y0.shape)
             #             y0 = y0 + pulse_vector
                         
             #             # Solve the model from the end of the last solution to
             #             # the time of the next pulse
             #             curr_tspan = ode_settings['tspan'][ptpidx - 1:ptpidx_next + 1]
                         
             #             t_curr, y_curr, saved_warn_msg, saved_warn_id = run_ABM(
             #                 ode_settings, run_parameters, y0, curr_tspan
             #             )
                         
             #             # Append the current result vectors into final result vectors
             #             # Skip the first time point and first model output
             #             t = np.concatenate([t, t_curr[1:]])
             #             y = np.vstack([y, y_curr[1:, :]])
                         
             #             # Check if the model stopped early
             #             if len(t_curr) != len(curr_tspan):
             #                 break
                         
             #             # The initial conditions for the next call are the
             #             # model state at the last time step
             #             y0 = y_curr[-1, :]
                     
        except Exception as err:
            # Save the error info so it can be included in error_runs later
            saved_warn_msg = str(err)
            saved_warn_id = type(err).__name__
            t = []
        
        if len(t) == len(modelSettings.tspan):
            # Store model outputs in the model_out dictionary
            model_out = store_model_run_output(model_out, run, y)
        else:
            # The model stopped early
            error_runs.append({
                'run': run,
                'message': saved_warn_msg,
                'id': saved_warn_id
            })
        
        if modelSettings.saveOnError == 1:
            # Pad with last value and record
            model_out = save_error(model_out, run, y, modelSettings.tspan)

        print()  # Final newline after progress display
        return model_out, error_runs

def run_ABM(run, modelSettings, run_parameters, tspan):
    """
    Run the external ABM (testRun) with the given params.

    Parameters
    ----------
    modelSettings : TYPE
        DESCRIPTION.
    run_parameters : TYPE
        DESCRIPTION.
    tspan : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    stdout_file_name = "output/Calibration/stdout.txt"
    stderr_file_name = "output/Calibration/stderr.txt"
    open(stdout_file_name, 'w').close()
    open(stderr_file_name, 'w').close()
    
    # Put sampled parameters into text file
    np.savetxt("Sample.txt", run_parameters, delimiter='\t')
    
    nticks = modelSettings.tspan
    
    try:
        # Run model
        with open(stdout_file_name, 'a') as stdout_file:
            with open(stderr_file_name, 'a') as stderr_file:
                stdout_file.write("\n\n******************************\n*** MODEL EXECUTION #" + str(run) + " ***\n******************************\n")
                stderr_file.write("\n\n******************************\n*** MODEL EXECUTION #" + str(run) + " ***\n******************************\n")
                result = subprocess.run(["./bin/testRun", "--numticks", nticks , "--inputfile" , "config_scaffold.txt", "--wxw", "0.5", "--wyw", "0.4", "--wzw", "0.3"], stdout = stdout_file, stderr = stderr_file)
        
        # Error handling
        if result.returncode != 0:
            saved_warn_msg = result.stderr if result.stderr else 'Model execution failed'
            saved_warn_id = f'ExecutableError_{result.returncode}'
        elif result.stderr:
            saved_warn_msg = result.stderr
            saved_warn_id = 'ExecutableWarning'
        
        output_file_name = 'output/Output_Biomarkers.csv'
        
        # Save output
        if os.path.exists(output_file_name):
            output_data = np.loadtxt(output_file_name)
            
            # first column is time, rest are output variables
            if output_data.ndim == 1:
                # Single time point
                t = np.array([output_data[0]])
                y = output_data[2, 3, 4, 5, 6, 7, 19, 20].reshape(1, -1)
            else:
                t = output_data[:, 0]
                y = output_data[:, [2, 3, 4, 5, 6, 7, 19, 20]]
        else:
            # Output file not created - model failed
            t = np.array([])
            y = np.array([])
            if not saved_warn_msg:
                saved_warn_msg = 'Output file not created by executable'
                saved_warn_id = 'NoOutputError'

    except Exception as e:
        saved_warn_msg = str(e)
        saved_warn_id = type(e).__name__
        t = np.array([])
        y = np.array([])
    
    # file cleanup
    finally:
        temp_files = [stderr_file_name, stdout_file_name, "Sample.txt"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    return t, y, saved_warn_msg, saved_warn_id
        


def store_model_run_output(model_out, run, y):
    """
    Store model run output in a results dict

    Parameters
    ----------
    model_out : dict
        stores all model outputs.
    run : int
        run index.
    y : numpy array
        model output for this run.

    Returns
    -------
    dict
        Updated model_out dictionary

    """
    
    model_out[run] = y
    return model_out
    
    
    

