# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 14:27:15 2026

@author: mm07

Driver file for CaliPro

"""

import pandas as pd
import numpy as np
from model_settings import *
from model_run import model_run
from find_ads import find_ads
from find_hdr import find_hdr


m = model()
modelSettings = model_settings(m)

# flag to allow finding the param ranges using ADS. if False, just finds HDR
hdr = True

# how long the calibration should run for by default
max_iter = 10
# percentage of runs that need to satisfy criteria for termination 
terminate = 0.90
# portion of parameters that we should be selecting within the param range 
# at the end of each iteration 
portion_params = 0.85
# pass criteria flexibility
pass_criteria_initial = 2.0
pass_criteria_non_initial = 1.25



runIteration = 1
# Loop through until condition is satisfied
terminateCalib = False
while not terminateCalib:
    #############################################################
    #   2. Perform sampling according to LHS.
    #############################################################
    #   3. Run the model.
    #############################################################
    # for this framework, both LHS sampling and model run happen through
    # calling the model_run function
    
    model_runs, paramMatrix, error_runs = model_run(modelSettings, runIteration)
    
    #############################################################
    #   4. Evaluate the performance of the model against exp data
    #############################################################
    
    # make fit criteria stricter after initial run
    if runIteration == 1:
        pass_criteria = pass_criteria_initial
    elif runIteration > 2:
        pass_criteria = pass_criteria_non_initial
        
    # compare model output against exp data
    
    
    
    