import argparse
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
import scipy

from soldier import Soldier, INITIALIZERS


def dice_notation(shorthand: str) -> Tuple[int, int]:
    """A simple parser for "NdX" style dice notation."""
    if shorthand is None:
        return
    left, _, right = shorthand.partition("d")
    return int(left) * (int(right),)


def generate_sample(n, initializer, totals=False):
    """Generate a sample of `n` soldiers initialized with `initializer`"""
    sample = np.zeros([n, len(Soldier.STATS) + bool(totals)], dtype=np.int16)

    for i in range(n):
        sol = Soldier(initializer)
        stats = [getattr(sol, stat).current for stat in Soldier.STATS]
        if totals:
            total = sol.weighed_stat_total() - Soldier.DEFAULT_WEIGHED_STAT_TOTAL
            sample[i, :] = stats + [total]
        else:
            sample[i, :] = stats

    return sample


def main(args):
    initializer = INITIALIZERS[args.initializer]
    if args.rolls is not None:
        initializer.dice = args.rolls

    sample = generate_sample(args.number, initializer, args.totals)

    if args.statistics:
        mean = sample.mean(0)
        cov = np.diag(np.cov(sample.T))
        skew = scipy.stats.skew(sample)
        print("Mean:", mean)
        print("Variance:", cov)
        print("Skewness:", skew)

    if args.plt_show:
        fig, axs = plt.subplots(4, 2)
        for stat_index, (stat, range_) in enumerate(Soldier.STATS.items()):
            values = range(
                range_.default + range_.min_delta, range_.default + range_.max_delta + 1
            )

            ax = axs[stat_index // 2, stat_index % 2]
            ax.set_title(stat)
            ax.bar(
                x=[value for value in values],
                width=0.75,
                height=[(sample[:, stat_index] == value).sum() for value in values],
                edgecolor="black",
                linewidth=0.75,
            )

        if args.totals:
            axs[3, 1].hist(sample[:, -1])
        else:
            axs[-1, -1].remove()

        fig.tight_layout()
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python soldierstats.py")
    parser.add_argument(
        "-n", "--number", type=int, help="Number of soldiers to generate", required=True
    )
    parser.add_argument(
        "--rolls",
        type=dice_notation,
        help="Override the number and sidedness of the dice of the given initializer",
        default=None,
    )
    # Do/don't plot weighed stat totals. It doesn't make much sense with LWOTC defaults.
    parser.add_argument(
        "--totals", action="store_true", help="Plot the weighed stat totals"
    )
    parser.add_argument(
        "--initializer",
        choices=INITIALIZERS,
        help="Which initializer to use",
        required=True,
    )
    parser.add_argument(
        "--plt-show",
        "--mpl-show",
        "--show",
        action="store_true",
        help="Show a MatPlotLib window with the results",
    )
    parser.add_argument(
        "--statistics",
        action="store_true",
        # help="Calculate statistics of the input and append them to the given file"
    )
    args = parser.parse_args()

    main(args)
