# -*- coding: utf-8 -*-
"""
Shows which pass criteria runs fail, for one iteration of a calibration
"""

import pickle
import sys
from pathlib import Path
import numpy as np
from calibration_driver import make_criteria, m, rep_pass_fraction
from calipro.eval_model_performance import at_day, check_criterion
from calipro.read_outputs import read_outputs


def describe(criterion):
    """Short label for a criterion."""
    if callable(criterion):
        return 'function criterion'
    lo, hi = criterion.get('min'), criterion.get('max')
    bounds = (f"{lo:.4g}" if lo is not None else '-inf') + ' to ' + (f"{hi:.4g}" if hi is not None else 'inf')
    return f"{criterion['output']}, day {criterion['day']:g}: {bounds}"


def main(folder, iteration=None):
    folder = Path(folder)
    with open(folder / 'calibration_results.pkl', 'rb') as f:
        results = pickle.load(f)

    # the iteration to check, and the c it was evaluated with
    record = results[-1] if iteration is None else next(r for r in results if r['iteration'] == iteration)
    it, c, reps = record['iteration'], record['pass_criteria'], record['reps']
    iter_dir = folder / f'iteration_{it}'
    nruns = len(record['paramMatrix'])
    print(f'Iteration {it}: {nruns // reps} parameter sets x {reps} replicates, c = {c:g}\n')

    criteria = make_criteria(c)
    set_ok = np.ones(nruns // reps, dtype=bool)
    for cond, cond_criteria in criteria.items():
        # this condition's outputs (None where the ABM run failed)
        files = [iter_dir / f'run{r}_{cond}' / 'output' / 'Output_Biomarkers.csv' for r in range(nruns)]
        files = [str(f) if f.exists() else None for f in files]
        out, days = read_outputs(files)
        crashed = sum(f is None for f in files)
        print(f'[{cond}]  {nruns - crashed} of {nruns} runs produced output')

        run_ok = np.ones(nruns, dtype=bool)
        for criterion in cond_criteria:
            try:
                ok = (np.asarray(criterion(out, days), dtype=bool) if callable(criterion)
                      else check_criterion(criterion, out, days))
            except ValueError as err:          # e.g. day not simulated, output misspelled
                print(f'  ERROR  {describe(criterion)}: {err}')
                continue
            run_ok &= ok
            line = f'  {ok.mean():5.0%} pass  {describe(criterion)}'
            # model values for bound criteria, to compare with the bounds
            if not callable(criterion):
                v = at_day(out, days, criterion['output'], criterion['day'])
                v = v[~np.isnan(v)]
                if v.size:
                    line += f'   (model: min {v.min():.4g}, median {np.median(v):.4g}, max {v.max():.4g})'
            print(line)

        # sets passing this condition with enough replicates
        needed = int(np.ceil(rep_pass_fraction * reps - 1e-9))
        cond_sets = run_ok.reshape(-1, reps).sum(axis=1) >= needed
        set_ok &= cond_sets
        print(f'  -> {run_ok.mean():.0%} of runs pass every {cond} criterion; '
              f'{cond_sets.sum()} of {cond_sets.size} sets have {needed}+ of {reps} replicates passing\n')

    print(f'Parameter sets passing all conditions: {set_ok.sum()} of {set_ok.size}')


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
