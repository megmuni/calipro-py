# -*- coding: utf-8 -*-
"""
Parameter density plots for a CaliPro calibration

Makes a grid with one row per refined iteration and one column per varied parameter.
Each panel shows the density of parameter values for passed runs (blue) and
failed runs (red) over the range sampled in that iteration, with the range
chosen for the next iteration as a purple bar on the x-axis.

Usage, from the repo root:
    python plot_results.py output/Calibration_job<ID>
Saves density_plots.png in that folder

"""
import pickle
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")  # no display needed (e.g. on the cluster)
import matplotlib.pyplot as plt
from calipro.ks_density import ks_density

# colors (in RGB, but matplotlib also accepts hex strings if you want to use that instead)
PASS_BLUE = (51/255, 187/255, 255/255)
FAIL_RED = (192/255, 43/255, 32/255)
NEXT_PURPLE = (137/255, 65/255, 249/255)


def plot_densities(results, out_file):
    """
    Plot the pass/fail parameter densities for every refined iteration.

    Parameters
    ----------
    results : list of dict
        contents of calibration_results.pkl (one dict per iteration)
    out_file : str or Path
        image file to save (e.g. density_plots.png)

    Returns
    -------
    None.

    """
    # only iterations whose ranges were refined (the final, calibrated
    # iteration has no next range, as in the MATLAB plot)
    rows = [r for r in results if r['densities']]
    if not rows:
        raise ValueError("no refined iterations to plot (calibration ended after iteration 1?)")
    names = rows[0]['names']

    fig, axes = plt.subplots(len(rows), len(names), squeeze=False,
                             figsize=(2.6 * len(names), 1.6 * len(rows)))

    for i, r in enumerate(rows):
        for k, name in enumerate(names):
            ax = axes[i, k]
            # x-axis spans the range sampled in this iteration
            lo, hi = r['params'][name]['lower'], r['params'][name]['upper']

            # density of passed and failed values, each over its observed values
            for values, color in [(r['failed_params'][:, k], FAIL_RED),
                                  (r['passed_params'][:, k], PASS_BLUE)]:
                if np.unique(values).size >= 2:
                    p, x = ks_density(values)
                    ax.fill_between(x, p, color=color, alpha=0.5, linewidth=0)

            # range for the next iteration (missing if refinement was skipped)
            if name in r['densities']:
                nlo, nhi = r['densities'][name]['new_range']
                ax.plot([nlo, nhi], [0, 0], color=NEXT_PURPLE, linewidth=3,
                        solid_capstyle='butt', clip_on=False)
            else:
                ax.text(0.5, 0.5, 'range kept', transform=ax.transAxes,
                        ha='center', va='center', fontsize=7, color='gray')

            ax.set_xlim(lo, hi)
            ax.set_ylim(bottom=0)
            ax.set_yticks([])   # densities are for shape, as in the MATLAB plot
            ax.tick_params(axis='x', labelsize=7)

            # iteration label on the left, parameter names on the bottom row
            if k == 0:
                ax.set_ylabel(f"Iteration {r['iteration']}\n({r['frac_passed']:.0%} passed)",
                              fontsize=8)
            if i == len(rows) - 1:
                ax.set_xlabel(name.replace(':', ':\n'), fontsize=7)

    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=PASS_BLUE, alpha=0.5),
                        plt.Rectangle((0, 0), 1, 1, color=FAIL_RED, alpha=0.5),
                        plt.Line2D([], [], color=NEXT_PURPLE, linewidth=3)],
               labels=['passed runs', 'failed runs', 'next iteration range'],
               loc='upper center', ncol=3, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_file, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    # folder of one calibration attempt
    folder = Path(sys.argv[1])
    with open(folder / "calibration_results.pkl", "rb") as f:
        results = pickle.load(f)

    out_file = folder / "density_plots.png"
    plot_densities(results, out_file)
    print(f"Saved {out_file}")
