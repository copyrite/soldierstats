import argparse
import random
from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt


StatRange = namedtuple("StatRange", ("default", "min_delta", "max_delta"))

STAT_NAMES = [
    "eStat_Offense",
    "eStat_Mobility",
    "eStat_HP",
    "eStat_Will",
    "eStat_Dodge",
    "eStat_Hacking",
    "eStat_PsiOffense",
]

stats = {
    "eStat_Offense": StatRange(65, -10, 10),
    "eStat_Mobility": StatRange(15, -2, 3),
    "eStat_HP": StatRange(4, -1, 3),
    "eStat_Will": StatRange(30, -15, 15),
    "eStat_Dodge": StatRange(5, -15, 15),
    "eStat_Hacking": StatRange(5, -4, 15),
    "eStat_PsiOffense": StatRange(20, -15, 15),
}


StatSwap = namedtuple(
    "StatSwap", ("StatUp", "StatUp_Amount", "StatDown", "StatDown_Amount", "Weight")
)

LWOTC_STAT_SWAPS = [
    StatSwap("eStat_Offense", 1, "eStat_Will", 3, 1.0),
    StatSwap("eStat_Offense", 2, "eStat_Will", 6, 1.0),
    StatSwap("eStat_Offense", 4, "eStat_Mobility", 1, 1.5),
    StatSwap("eStat_Offense", 4, "eStat_HP", 1, 1.5),
    StatSwap("eStat_Offense", 1, "eStat_Hacking", 3, 0.5),
    StatSwap("eStat_Offense", 1, "eStat_PsiOffense", 3, 1.0),
    StatSwap("eStat_Offense", 2, "eStat_PsiOffense", 6, 1.0),
    StatSwap("eStat_Offense", 1, "eStat_Dodge", 3, 1.0),
    StatSwap("eStat_Offense", 2, "eStat_Dodge", 6, 0.5),
    StatSwap("eStat_HP", 1, "eStat_Mobility", 1, 2.0),
    StatSwap("eStat_HP", 1, "eStat_PsiOffense", 12, 1.0),
    StatSwap("eStat_Mobility", 1, "eStat_PsiOffense", 12, 1.0),
    StatSwap("eStat_Dodge", 1, "eStat_Will", 1, 1.0),
    StatSwap("eStat_Dodge", 2, "eStat_Will", 2, 1.0),
    StatSwap("eStat_Dodge", 3, "eStat_Will", 3, 1.0),
    StatSwap("eStat_Dodge", 4, "eStat_Will", 4, 1.0),
    StatSwap("eStat_Dodge", 1, "eStat_Hacking", 1, 0.5),
    StatSwap("eStat_Dodge", 2, "eStat_Hacking", 2, 0.5),
    StatSwap("eStat_Dodge", 3, "eStat_Hacking", 3, 0.5),
    StatSwap("eStat_Dodge", 4, "eStat_Hacking", 4, 0.5),
    StatSwap("eStat_Dodge", 4, "eStat_PsiOffense", 4, 1.0),
    StatSwap("eStat_Dodge", 5, "eStat_PsiOffense", 5, 1.0),
    StatSwap("eStat_Dodge", 6, "eStat_PsiOffense", 6, 1.0),
    StatSwap("eStat_Dodge", 7, "eStat_PsiOffense", 7, 1.0),
    StatSwap("eStat_Will", 1, "eStat_Hacking", 1, 0.5),
    StatSwap("eStat_Will", 2, "eStat_Hacking", 2, 0.5),
    StatSwap("eStat_Will", 4, "eStat_PsiOffense", 4, 0.5),
    StatSwap("eStat_Will", 5, "eStat_PsiOffense", 5, 1.0),
    StatSwap("eStat_Will", 6, "eStat_PsiOffense", 6, 1.0),
    StatSwap("eStat_Will", 7, "eStat_PsiOffense", 7, 1.0),
]

INDEP_STAT_SWAPS = [
    StatSwap("eStat_Offense", 1, "eStat_Offense", 0, 2.0),
    StatSwap("eStat_Offense", 2, "eStat_Offense", 0, 1.0),
    StatSwap("eStat_HP", 1, "eStat_HP", 0, 0.75),
    StatSwap("eStat_Mobility", 1, "eStat_Mobility", 0, 0.75),
    StatSwap("eStat_Dodge", 1, "eStat_Dodge", 0, 1.25),
    StatSwap("eStat_Dodge", 2, "eStat_Dodge", 0, 1.0),
    StatSwap("eStat_Dodge", 3, "eStat_Dodge", 0, 0.75),
    StatSwap("eStat_Will", 1, "eStat_Will", 0, 1.25),
    StatSwap("eStat_Will", 2, "eStat_Will", 0, 1.0),
    StatSwap("eStat_Will", 3, "eStat_Will", 0, 0.75),
    StatSwap("eStat_Hacking", 1, "eStat_Hacking", 0, 2.0),
    StatSwap("eStat_Hacking", 2, "eStat_Hacking", 0, 1.0),
    StatSwap("eStat_PsiOffense", 1, "eStat_PsiOffense", 0, 1.25),
    StatSwap("eStat_PsiOffense", 2, "eStat_PsiOffense", 0, 1.0),
    StatSwap("eStat_PsiOffense", 3, "eStat_PsiOffense", 0, 0.75),
]

SWAP_TABLES = {
    "lwotc": LWOTC_STAT_SWAPS,
    "indep": INDEP_STAT_SWAPS,
}


class Soldier:
    __slots__ = stats
    stat_swaps = LWOTC_STAT_SWAPS
    dice_count = 5
    dice_size = 4

    def __init__(self):
        delta = dict((stat, 0) for stat in stats)
        nRolls = sum(random.randint(1, self.dice_size) for _ in range(self.dice_count))

        for _ in range(nRolls):
            for __ in range(1000):
                swap = random.choices(
                    self.stat_swaps,
                    weights=list(swap.Weight for swap in self.stat_swaps),
                )[0]
                if random.getrandbits(1):
                    swap = StatSwap(
                        swap.StatDown,
                        swap.StatDown_Amount,
                        swap.StatUp,
                        swap.StatUp_Amount,
                        swap.Weight,
                    )

                if is_valid_swap(delta, swap):
                    delta[swap.StatUp] += swap.StatUp_Amount
                    delta[swap.StatDown] -= swap.StatDown_Amount

                    break

        for stat, range_ in stats.items():
            setattr(self, stat, range_.default + delta[stat])

    def weighed_stat_total(self) -> int:
        """
        A numeric estimation of how good stats the soldier rolled.
        With the default stat table, this is constant, thus this is only ever useful if the table or the algorithm is modified.
        """
        WEIGHTS = {
            "eStat_Offense": 3,
            "eStat_Mobility": 12,
            "eStat_HP": 12,
            "eStat_Will": 1,
            "eStat_Dodge": 1,
            "eStat_Hacking": 1,
            "eStat_PsiOffense": 1,
        }
        return sum(getattr(self, stat) * WEIGHTS[stat] for stat in stats)


def is_valid_swap(delta, swap: StatSwap):
    return (
        delta[swap.StatUp] + swap.StatUp_Amount <= stats[swap.StatUp].max_delta
    ) and (
        delta[swap.StatDown] - swap.StatDown_Amount >= stats[swap.StatDown].min_delta
    )


def dice_notation(shorthand: str) -> tuple[int, int]:
    """A simple parser for "NdX" style dice notation."""
    left, _, right = shorthand.partition("d")
    return int(left), int(right)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python soldierstats.py")
    parser.add_argument(
        "-n", "--number", type=int, help="Number of soldiers to generate"
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
        "--table",
        "--swap-table",
        choices=SWAP_TABLES,
        help="Which stat swap table to use",
    )
    args = parser.parse_args()

    Soldier.stat_swaps = SWAP_TABLES[args.table]
    Soldier.dice_count, Soldier.dice_size = args.rolls

    # dataset will look like:
    # {
    #     "eStat_Offense": np.array([0, 0, 0, ..., 0]),
    #     "eStat_Mobility": np.array([0, 0, 0, 0, 0, 0]),
    #     ...
    #     "eStat_PsiOffense": np.array([0, 0, 0, ..., 0]),
    # }
    dataset = dict(
        (stat, np.zeros(range_.max_delta - range_.min_delta + 1))
        for stat, range_ in stats.items()
    )

    barracks = [Soldier() for _ in range(args.number)]
    for sol in barracks:
        for stat, range_ in stats.items():
            # Increment the correct position in the array by 1. [0] contains the minimum of the stat, etc.
            dataset[stat][getattr(sol, stat) - (range_.default + range_.min_delta)] += 1

    fig, axs = plt.subplots(4, 2)
    for i, (stat, range_) in enumerate(stats.items()):
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
