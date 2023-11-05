import argparse
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt

from soldier import Soldier, lwotc_factory, ancev1_factory

SOLDIER_GEN_TYPES = {
    "lwotc": lwotc_factory,
    "ancev1": ancev1_factory,
}


def dice_notation(shorthand: str) -> Tuple[int, int]:
    """A simple parser for "NdX" style dice notation."""
    left, _, right = shorthand.partition("d")
    return int(left), int(right)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python soldierstats.py")
    parser.add_argument(
        "-n", "--number", type=int, help="Number of soldiers to generate", required=True
    )
    parser.add_argument(
        "--rolls",
        type=dice_notation,
        help="Number and sidedness of dice to generate",
        default="5d4",
    )
    # Do/don't plot weighed stat totals. It doesn't make much sense with LWOTC defaults.
    parser.add_argument(
        "--totals", action="store_true", help="Plot the weighed stat totals"
    )
    parser.add_argument(
        "--generation-type",
        choices=SOLDIER_GEN_TYPES,
        help="Which stat generation type to use",
        required=True,
    )
    args = parser.parse_args()

    # dataset will look like:
    # {
    #     "eStat_Offense": np.array([0, 0, 0, ..., 0]),
    #     "eStat_Mobility": np.array([0, 0, 0, 0, 0, 0]),
    #     ...
    #     "eStat_PsiOffense": np.array([0, 0, 0, ..., 0]),
    # }
    dataset = dict(
        (stat, np.zeros(range_.max_delta - range_.min_delta + 1))
        for stat, range_ in Soldier.STATS.items()
    )

    barracks = [SOLDIER_GEN_TYPES[args.generation_type]() for _ in range(args.number)]
    for sol in barracks:
        for stat, range_ in Soldier.STATS.items():
            # Increment the correct position in the array by 1. [0] contains the minimum of the stat, etc.
            dataset[stat][
                getattr(sol, stat).current - (range_.default + range_.min_delta)
            ] += 1

    fig, axs = plt.subplots(4, 2)
    for i, (stat, range_) in enumerate(Soldier.STATS.items()):
        ax = axs[i // 2, i % 2]
        ax.set_title(stat)
        ax.bar(
            x=range(
                range_.default + range_.min_delta, range_.default + range_.max_delta + 1
            ),
            height=dataset[stat] / args.number,
        )

    if args.totals:
        axs[3, 1].hist(list(sol.weighed_stat_total() for sol in barracks))
    else:
        axs[-1, -1].remove()

    fig.tight_layout()
    plt.show()
