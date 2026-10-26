"""
GPU usage report for a CaliPro calibration attempt.

Each array task logs its GPU usage (gpu_<task>.csv in its iteration folder,
see calipro_array_job.sh). This summarizes those logs per ABM run and per
iteration: run time, peak GPU memory and average GPU utilization, and the
total GPU slice-hours used.

Usage, from the repo root:
    python gpu_report.py output/Calibration_job<ID>
Saves gpu_summary.csv in that folder and prints a summary per iteration.

"""
import sys
from pathlib import Path
import pandas as pd


def read_gpu_log(path):
    """
    Summarize one task's GPU log.

    Parameters
    ----------
    path : Path
        a gpu_<task>.csv written by nvidia-smi.

    Returns
    -------
    dict
        minutes (first to last sample), peak memory (MiB), memory total
        (MiB), mean and peak utilization (%), number of samples. NaN where
        the GPU did not report a value (e.g. utilization on some MIG slices).

    """
    log = pd.read_csv(path, skipinitialspace=True)
    log.columns = [c.split(' [')[0].strip() for c in log.columns]  # drop units

    # values nvidia-smi couldn't report ('[N/A]', '[Not Supported]') become NaN
    for col in ['utilization.gpu', 'memory.used', 'memory.total']:
        log[col] = pd.to_numeric(log[col], errors='coerce')

    times = pd.to_datetime(log['timestamp'], format='%Y/%m/%d %H:%M:%S.%f', errors='coerce')
    return {
        'minutes': (times.max() - times.min()).total_seconds() / 60 if len(log) > 1 else 0.0,
        'mem_peak_MiB': log['memory.used'].max(),
        'mem_total_MiB': log['memory.total'].max(),
        'util_mean_pct': log['utilization.gpu'].mean(),
        'util_peak_pct': log['utilization.gpu'].max(),
        'samples': len(log),
    }


def gpu_report(folder):
    """
    Summarize every task's GPU log in one calibration attempt.

    Parameters
    ----------
    folder : Path
        the attempt folder (output/Calibration_job<ID>).

    Returns
    -------
    summary : DataFrame
        one row per ABM run: iteration, task, workdir (run and condition),
        and its GPU usage.

    """
    rows = []
    for iter_dir in sorted(Path(folder).glob('iteration_*'),
                           key=lambda d: int(d.name.split('_')[1])):
        # task t's workdir name (e.g. run3_low), from the iteration's task list
        task_file = iter_dir / 'tasks.txt'
        workdirs = task_file.read_text().split() if task_file.exists() else []

        for log in sorted(iter_dir.glob('gpu_*.csv'), key=lambda p: int(p.stem.split('_')[1])):
            task = int(log.stem.split('_')[1])
            try:
                usage = read_gpu_log(log)
            except Exception as err:  # empty or cut-off log (e.g. task killed at start)
                usage = {'error': f'{type(err).__name__}: {err}'}
            rows.append({'iteration': int(iter_dir.name.split('_')[1]), 'task': task,
                         'workdir': workdirs[task] if task < len(workdirs) else '', **usage})

    if not rows:
        raise ValueError(f"no gpu_*.csv logs found in {folder} (runs were 'local', "
                         "or the array job script has no GPU monitor)")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    summary = gpu_report(folder)
    summary.to_csv(folder / 'gpu_summary.csv', index=False)

    # per iteration: how long runs took and how much of the GPU they used
    summary['gpu_hours'] = summary['minutes'] / 60
    per_iter = summary.groupby('iteration').agg(
        runs=('task', 'count'),
        gpu_hours=('gpu_hours', 'sum'),
        minutes_median=('minutes', 'median'),
        minutes_max=('minutes', 'max'),
        mem_peak_MiB=('mem_peak_MiB', 'max'),
        mem_total_MiB=('mem_total_MiB', 'max'),
        util_mean_pct=('util_mean_pct', 'mean'),
    )
    print(per_iter.round(2).to_string())

    # total over all iterations (time the ABM ran on a slice, not queue time)
    print(f"\nTotal: {summary['gpu_hours'].sum():.2f} GPU slice-hours "
          f"over {len(summary)} ABM runs")
    print(f"Saved {folder / 'gpu_summary.csv'}")
