# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 14:51:14 2025

@author: mmunip

Get settings from model settings file.

"""

def get_run_settings(settingsFileName):
    """
    Get the model settings from a settings file.
    
    The called will perform checks on some of the settings, since different
    callers will have different settings requirements in some cases.

    Parameters
    ----------
    settingsFileName : file
        file containing model settings (default model_settings.py).

    Returns
    -------
    None.

    """
    
    # Load the settings
    

