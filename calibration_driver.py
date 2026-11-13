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
from datetime import datetime
import numpy as np
from ABM import WORLD_VOLUME_MM3, GEL_VOLUME_MM3
from model_settings import model_settings
from calipro.model_run import model_run
from calipro.eval_model_performance import eval_model_performance, at_day
from calipro.find_ads import find_ads
from calipro.find_hdr import find_hdr


#############################################################
#   1. Inputs
#############################################################

# model settings: runs, time span, parameters, how the ABM is run
m = model_settings()

# seed for the whole calibration (one shared generator, for reproducibility)
seed = 42
rng = np.random.default_rng(seed)

# True: refine ranges with HDR. False: refine ranges with ADS
hdr = False
# maximum number of iterations
max_iter = 12
# fraction of runs that must pass for calibration to be complete
terminate = 0.90
# fraction of a parameter set's replicates that must pass each condition for
# the set to pass (with 3 replicates, 2/3 means 2 of 3)
rep_pass_fraction = 2 / 3
if not 0 < rep_pass_fraction <= 1:
    raise ValueError(f"rep_pass_fraction must be in (0, 1], got {rep_pass_fraction}")
# HDR coverage: portion of the pass density kept in each new range
portion_params = 0.85
# how much the pass window is loosened around experimental data
# (iterations 1-2, then later iterations)
pass_criteria_schedule = [3.0, 3.0, 2.0, 2.0, 1.5]
if not pass_criteria_schedule or min(pass_criteria_schedule) <= 0:
    raise ValueError("pass_criteria_schedule must be a non-empty list of positive values")

# refine ranges only when at least this many parameter sets pass; with fewer,
# the densities rest on too few points, so the same ranges are sampled again
min_pass_sets = 5
# iterations in a row without enough passing sets before giving up
max_resample = 3
if min_pass_sets < 1 or max_resample < 0:
    raise ValueError("min_pass_sets must be at least 1 and max_resample at least 0")

if max_iter < len(pass_criteria_schedule):
    raise ValueError(f"max_iter ({max_iter}) must be at least the schedule's length "
                f"({len(pass_criteria_schedule)}) to reach its strictest c")

# where configs, logs, outputs and results are saved
# each calipro attempt has its own folder
out_dir = os.environ.get("CALIPRO_OUT_DIR",
                         f"output/Calibration_{datetime.now():%Y-%m-%d_%H-%M-%S}")

def to_world(values):
    """
    Convert whole-gel experimental amounts (e.g. sGAG, ug) to the volume the
    ABM simulates, so they compare directly with its 'Aggrecan (ug)' output
    """
    return [v * WORLD_VOLUME_MM3 / GEL_VOLUME_MM3 for v in values]

def make_criteria(c):
    """
    Pass set definition for one iteration. Criteria are defined for each scaffold
    condition in model_settings (m.conditions). A replicate passes a condition
    if it meets every criterion of that condition; a parameter set passes if,
    for every condition, at least rep_pass_fraction of its replicates pass.
    c loosens windows built from experimental data: [min / c, max * c]

    Parameters
    ----------
    c : float
        pass criteria flexibility for this iteration.

    Returns
    -------
    criteria : dict
        {condition: list of criteria} for eval_model_performance (bounds or
        functions)


    """
    # define your criteria here
    # experimental fold change (day 21 cells divided by day 1 cells), one entry per sample
    high_fold_change = [0.80, 1.11, 1.09, 1.07, 1.11, 1.25, 0.85] # high MW
    #low_fold_change = [1.09, 0.37, 1.15, 1.28, 1.44, 0.76, 0.73] # low MW

    # experimental sGAG (ug), one entry per sample, but scaled to ABM world size
    high_agg_d7 = to_world([36.91, 52.97, 55.78, 34.44])
    high_agg_d14 = to_world([102.11, 13.49, 47.59, 59.17])
    high_agg_d21 = to_world([111.88, 94.67, 37.10, 41.28])
    #low_agg_d7 = to_world([87.22, 51.62, 136.20, 52.13])
    #low_agg_d14 = to_world([130.80, 97.47, 90.61, 84.87])
    #low_agg_d21 = to_world([131.42, 131.09, 99.96, 100.93])

    # tolerance around single reported values (1.25 = within 25%), loosened by c
    tol = 1.25 ** c

    return {
        'high': [
            lambda out, days: ( # window around experimental cell fold change data
                (at_day(out, days, 'Total Cells', 21) / at_day(out, days, 'Total Cells', 1) >= min(high_fold_change) / c)
                & (at_day(out, days, 'Total Cells', 21) / at_day(out, days, 'Total Cells', 1) <= max(high_fold_change) * c)
            ),

            # threshold
            {'output': 'Viability Rate(%)', 'day': 21, 'min': 100 - 15 * c},

            # aggrecan: window around experimental samples
            {'output': 'Aggrecan (ug)', 'day': 7, 'min': min(high_agg_d7) / c, 'max': max(high_agg_d7) * c},
            {'output': 'Aggrecan (ug)', 'day': 14, 'min': min(high_agg_d14) / c, 'max': max(high_agg_d14) * c},
            {'output': 'Aggrecan (ug)', 'day': 21, 'min': min(high_agg_d21) / c, 'max': max(high_agg_d21) * c},

            # differentiation: within tolerance of the reported value
            {'output': 'Differentiation (%)', 'day': 7, 'min': 4 / tol, 'max': 4 * tol},
            {'output': 'Differentiation (%)', 'day': 14, 'min': 20 / tol, 'max': 20 * tol},
            {'output': 'Differentiation (%)', 'day': 21, 'min': 48.67 / tol, 'max': 48.67 * tol},

        ],
        # 'low': [
        #     lambda out, days: ( # window around experimental cell fold change data
        #         (at_day(out, days, 'Total Cells', 21) / at_day(out, days, 'Total Cells', 1) >= min(low_fold_change) / c)
        #         & (at_day(out, days, 'Total Cells', 21) / at_day(out, days, 'Total Cells', 1) <= max(low_fold_change) * c)
        #     ),
        #
        #     # threshold
        #     {'output': 'Viability Rate(%)', 'day': 21, 'min': 100 - 15 * c},
        #
        #     {'output': 'Aggrecan (ug)', 'day': 7, 'min': min(low_agg_d7) / c, 'max': max(low_agg_d7) * c},
        #     {'output': 'Aggrecan (ug)', 'day': 14, 'min': min(low_agg_d14) / c, 'max': max(low_agg_d14) * c},
        #     {'output': 'Aggrecan (ug)', 'day': 21, 'min': min(low_agg_d21) / c, 'max': max(low_agg_d21) * c},
        #
        #     {'output': 'Differentiation (%)', 'day': 7, 'min': 10 / tol, 'max': 10 * tol},
        #     {'output': 'Differentiation (%)', 'day': 14, 'min': 40 / tol, 'max': 40 * tol},
        #     {'output': 'Differentiation (%)', 'day': 21, 'min': 80 / tol, 'max': 80 * tol},
        # ],
    }

#############################################################
#   Calibration loop
#############################################################
def main():
    """Run the calibration main loop"""
    print(f'Saving to {out_dir}')

    os.makedirs(out_dir, exist_ok=True)
    results = []

    # position in pass_criteria_schedule: advances only when ranges are refined,
    # so a resampled iteration is evaluated with the same c again
    stage = 0
    resample_count = 0

    for runIteration in range(1, max_iter + 1):

        #   2-3. Sample parameters and run the model
        model_out, days, paramMatrix, names, error_runs = model_run(m, runIteration, rng, out_dir)

        #   3. Evaluate runs against the pass set definition
        # pass criteria for this stage of the schedule (last value repeats)
        c = pass_criteria_schedule[min(stage, len(pass_criteria_schedule) - 1)]
        passed_params, passed_runs, failed_params, failed_runs = \
            eval_model_performance(make_criteria(c), model_out, days, paramMatrix,
                                   m.reps, rep_pass_fraction)

        nsets = len(passed_params) + len(failed_params)
        frac_passed = len(passed_params) / nsets
        print(f'Iteration {runIteration}: {len(passed_params)} of {nsets} parameter sets '
              f'passed all conditions ({frac_passed:.0%})')

        # record this iteration (ranges sampled, runs, pass/fail split)
        record = {'iteration': runIteration, 'names': names,
                  'params': copy.deepcopy(m.params), 'paramMatrix': paramMatrix,
                  'reps': m.reps,
                  'passed_params': passed_params, 'failed_params': failed_params,
                  'frac_passed': frac_passed, 'pass_criteria': c,
                  'error_runs': error_runs, 'densities': {}}
        results.append(record)

        # termination criterion met at the strictest c: calibration complete.
        # Before c reaches the end of the schedule, keep refining instead
        strictest = stage >= len(pass_criteria_schedule) - 1
        if frac_passed >= terminate and strictest:
            print('Calibration complete according to user specifications')
            break
        if frac_passed >= terminate:
            print(f'  {frac_passed:.0%} passed at c = {c:g}; continuing until c = '
                  f'{pass_criteria_schedule[-1]:g}')

        # no passed runs -> nothing to refine from
        # too few passing sets to refine from: sample the same ranges again
        if len(passed_params) < min_pass_sets:
            resample_count += 1
            if resample_count > max_resample:
                print(f'Fewer than {min_pass_sets} parameter sets passed in {resample_count} '
                      'iterations in a row. Check initial parameter ranges, the pass set '
                      'definition, or the model.')
                break
            print(f'  only {len(passed_params)} set(s) passed (need {min_pass_sets}); resampling '
                  f'the same ranges at c = {c:g} ({resample_count} of {max_resample})')
            with open(os.path.join(out_dir, 'calibration_results.pkl'), 'wb') as f:
                pickle.dump(results, f)
            continue
        resample_count = 0

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

        # ranges refined: move to the next c in the schedule
        stage += 1

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

if __name__ == "__main__":
    main()
