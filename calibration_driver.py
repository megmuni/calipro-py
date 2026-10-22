# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 14:27:15 2026

@author: mm07

Driver file for CaliPro.

Steps (Joslyn et al. 2020, Fig. 2):
    1. Inputs: model settings, parameter ranges, pass set definition
    2. Sample parameter space (LHS)
    3. Run the model and evaluate runs against the pass set definition
    4. Refine each parameter's range using HDR or ADS
Steps 2-4 repeat until enough runs pass (termination criterion) or the
maximum number of iterations is reached.

"""

import copy
import os
import pickle
import numpy as np
from model_settings import model_settings
from model_run import model_run
from eval_model_performance import eval_model_performance, at_day
from find_ads import find_ads
from find_hdr import find_hdr


#############################################################
#   1. Inputs
#############################################################

# model settings: runs, time span, parameters, how the ABM is run
m = model_settings()

# seed for the whole calibration (one shared generator, for reproducibility)
seed = 42
rng = np.random.default_rng(seed)

# True: refine ranges with HDR. False: refine ranges with ADS
hdr = True
# maximum number of iterations
max_iter = 10
# fraction of runs that must pass for calibration to be complete
terminate = 0.90
# HDR coverage: portion of the pass density kept in each new range
portion_params = 0.85
# how much the pass window is loosened around experimental data
# (iterations 1-2, then later iterations)
pass_criteria_initial = 2.0
pass_criteria_non_initial = 1.25

# where configs, logs, outputs and results are saved
out_dir = "output/Calibration"


def make_criteria(c):
    """
    Pass set definition for one iteration. c loosens windows built from
    experimental data: [min / c, max * c]. EDIT for your data and checks.

    Parameters
    ----------
    c : float
        pass criteria flexibility for this iteration.

    Returns
    -------
    criteria : list
        criteria for eval_model_performance (bounds or functions).

    """
    # EXAMPLE criteria for 7-day test runs; replace with your own
    cells_day7 = [1100, 1200, 1150]   # experimental values on day 7
    return [
        # window around experimental data
        {'output': 'Total Cells', 'day': 7,
         'min': min(cells_day7) / c, 'max': max(cells_day7) * c},
        # threshold
        {'output': 'Viability Rate(%)', 'day': 7, 'min': 20},
        # trend
        lambda out, days: at_day(out, days, 'Collagen (ug)', 7) > at_day(out, days, 'Collagen (ug)', 1),
    ]


#############################################################
#   Calibration loop
#############################################################
os.makedirs(out_dir, exist_ok=True)
results = []

for runIteration in range(1, max_iter + 1):

    #   2-3. Sample parameters and run the model
    model_out, days, paramMatrix, names, error_runs = model_run(m, runIteration, rng, out_dir)

    #   3. Evaluate runs against the pass set definition
    # pass criteria are stricter after the first two iterations
    c = pass_criteria_initial if runIteration <= 2 else pass_criteria_non_initial
    passed_params, passed_runs, failed_params, failed_runs = \
        eval_model_performance(make_criteria(c), model_out, days, paramMatrix)

    frac_passed = len(passed_params) / len(paramMatrix)
    print(f'Iteration {runIteration}: {len(passed_params)} of {len(paramMatrix)} runs '
          f'passed ({frac_passed:.0%})')

    # record this iteration (ranges sampled, runs, pass/fail split)
    record = {'iteration': runIteration, 'names': names,
              'params': copy.deepcopy(m.params), 'paramMatrix': paramMatrix,
              'passed_params': passed_params, 'failed_params': failed_params,
              'frac_passed': frac_passed, 'pass_criteria': c,
              'error_runs': error_runs, 'densities': {}}
    results.append(record)

    # termination criterion met: calibration complete
    if frac_passed >= terminate:
        print('Calibration complete according to user specifications')
        break

    # no passed runs: nothing to refine from
    if len(passed_params) == 0:
        print('No runs passed. Check initial parameter ranges, the pass set '
              'definition, or the model.')
        break

    #   4. Refine each parameter's range from the pass (and fail) densities
    for k, name in enumerate(names):
        passed_k, failed_k = passed_params[:, k], failed_params[:, k]

        # density needs at least 2 distinct passed values; otherwise keep the range
        if np.unique(passed_k).size < 2:
            print(f'  {name}: too few distinct passed values, range kept')
            continue

        if hdr:
            new_range, x, dens_pass, dens_fail, dens_sub = find_hdr(passed_k, failed_k, portion_params)
        else:
            new_range, x, dens_pass, dens_fail, dens_sub = find_ads(passed_k, failed_k)

        # save densities for the parameter density plots
        record['densities'][name] = {'x': x, 'pass': dens_pass, 'fail': dens_fail,
                                     'sub': dens_sub, 'new_range': new_range}

        # new range must still be a range; otherwise keep the current one
        if new_range[0] < new_range[1]:
            m.params[name]['lower'], m.params[name]['upper'] = float(new_range[0]), float(new_range[1])
        else:
            print(f'  {name}: refined range collapsed to one value, range kept')

    # save after every iteration, so results survive a crash
    with open(os.path.join(out_dir, 'calibration_results.pkl'), 'wb') as f:
        pickle.dump(results, f)

else:
    print('Calibration met max iteration count. Evaluate initial parameter '
          'ranges or model construction')

# final save, including the last iteration
with open(os.path.join(out_dir, 'calibration_results.pkl'), 'wb') as f:
    pickle.dump(results, f)

# calibrated ranges
for name, p in m.params.items():
    print(f"{name}: [{p['lower']:.4g}, {p['upper']:.4g}]")