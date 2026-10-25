# calipro-py
Python implementation of the CaliPro calibration protocol for biological modeling [(Joslyn et al., 2020)](https://doi.org/10.1007/s12195-020-00650-z). This repo contains the algorithm converted from the original MATLAB and adapted to run an ABM located on a Slurm cluster.

## Overview

Each iteration in this optimization protocol has the following steps:

1. **Sample** `NR` parameter sets from the current ranges with Latin hypercube sampling, each run `reps` times (stochastic replicates).
2. **Run** every run as one task of a Slurm job array.
3. **Evaluate** each run against the pass set definition (`make_criteria`). A run passes only if it meets every criterion.
4. **Stop** if at least `terminate` of runs passed. Otherwise **refine** each varied parameter's range from the pass/fail parameter densities (HDR or ADS) and repeat, up to `max_iter` iterations.

## Repo layout

```
calibration_driver.py      # calibration settings, pass set definition(s), main loop
model_settings.py          # runs, replicates, run length, ABM/Slurm settings
calipro_driver_job.sh      # submit this
calipro_array_job.sh       # one ABM run per array task (submitted by the driver)
ABM.py                     # config writing and ABM call (same as [ABM-NM-optimization](https://github.com/megmuni/ABM-NM-optimization))
bin/                       # ABM executable (testRun)
simulation_config.template.json
parameters.xlsx
calipro/                   # helper modules (no need to edit)
output/                    # created automatically
```

`ABM.py`, `bin/` and the template can be copies of, or symlinks to, the files in the ABM-NM-optimization repo. Keep `ABM.py` in sync with that repo.

## One-time setup
1. Python env (on the login node):

```bash
   module load StdEnv/2023 gcc/12.3 python/3.11
   virtualenv --no-download ~/calipro_env
   source ~/calipro_env/bin/activate
   pip install --no-index --upgrade pip
   pip install --no-index numpy pandas scipy openpyxl
   deactivate
```
2. **Job scripts**: edit lines in `calipro_driver_job.sh` and `calipro_array_job.sh` that are specific to your account, module loads matching
   `ABM_optimize_job.sh`, environment path, and desired memory and time limits.

## Configure a calibration

**`parameters.xlsx`** contains one row per model parameter

| Column | Meaning |
|---|---|
| `Parameter Name` | Must match the tagged parameter path in the template, e.g. `stem:proliferation:static_probability` |
| `Lower`, `Upper` | Initial sampling range |
| `Type` | 1 lognormal → log-uniform, 2 discrete → integers, 3 normal / 4 uniform → uniform |
| `Vary?` | `Y` or blank to vary, `N` to fix at `Mean` |
| `Mean` | Value used when the parameter is fixed |

**`model_settings.py`**

| Setting | Meaning |
|---|---|
| `NR` | Parameter sets sampled per iteration |
| `reps` | Replicate runs per parameter set (runs per iteration = `NR × reps`) |
| `t_end` | Run length in days (48 ticks per day) |
| `condition` | Scaffold condition, `'high'` or `'low'` |
| `executor` | `'slurm'` (job arrays) or `'local'` (sequential, needs a GPU) |
| `array_cap` | Most array tasks running at once |

**`calibration_driver.py`**

| Setting | Meaning |
|---|---|
| `make_criteria(c)` | The pass set definition (see below) |
| `hdr` | `True` to refine with HDR, `False` for ADS |
| `max_iter` | Maximum iterations |
| `terminate` | Fraction of runs that must pass to finish |
| `portion_params` | HDR coverage |
| `pass_criteria_initial`, `pass_criteria_non_initial` | Loosening factor `c` for iterations 1–2, then later iterations |
| `seed` | Random seed for sampling |

### Pass set definition

`make_criteria(c)` returns a list of criteria. Each is either a bound on one
output on one day, or a function returning True/False per run. Example:

```python
return [
    # window from experimental data, loosened by c
    {'output': 'Total Cells', 'day': 7, 'min': min(data) / c, 'max': max(data) * c},
    # threshold
    {'output': 'Viability Rate(%)', 'day': 7, 'min': 20},
    # trend or comparison
    lambda out, days: at_day(out, days, 'Collagen (ug)', 7) > at_day(out, days, 'Collagen (ug)', 1),
]
```

Output names should match the `Output_Biomarkers.csv` headers exactly, and days must be no later than `t_end`. Failed ABM runs fail every criterion.

## Run

From the repo root:

```bash
sbatch calipro_driver_job.sh
```

The driver job doesn't need a GPU; it submits one job array per iteration and waits for it. For a quick first test, use e.g. `NR = 5`, `reps = 3`, `max_iter = 2`.

To run without Slurm (e.g. inside an interactive GPU session), set `executor = 'local'` and run `python calibration_driver.py` directly.

## Output

Each attempt gets its own folder, `output/Calibration_job<job ID>/`
(or `output/Calibration_<date>_<time>/` without Slurm):

```
driver.log                  # progress, pass fractions, final ranges
calibration_results.pkl     # per iteration: ranges, parameter matrix,
                            # passed/failed sets, failed runs, densities
iteration_k/
    slurm_{i}.out           # array task logs
    run{i}/                 # config, ABM output, stdout/stderr, error.txt if failed
```

```python
import pickle
results = pickle.load(open('output/Calibration_job<ID>/calibration_results.pkl', 'rb'))
results[-1]['params']        # ranges sampled in the last iteration
results[-1]['frac_passed']   # fraction of runs that passed
```

Old attempt folders are not deleted automatically. Recommended to use a file transfer program for faster deletion (e.g., Globus.)
