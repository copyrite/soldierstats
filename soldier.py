import random
from collections import namedtuple
from functools import partial
from typing import Sequence

# TODO: Rename to StatRange?
Stat = namedtuple(
    "Stat", ("default", "min_delta", "max_delta", "weight"), defaults=(1,)
)

StatSwap = namedtuple(
    "StatSwap", ("StatUp", "StatUp_Amount", "StatDown", "StatDown_Amount", "Weight")
)

LWOTC_SWAPS = (
    StatSwap("Offense", 1, "Will", 3, 1.0),
    StatSwap("Offense", 2, "Will", 6, 1.0),
    StatSwap("Offense", 4, "Mobility", 1, 1.5),
    StatSwap("Offense", 4, "HP", 1, 1.5),
    StatSwap("Offense", 1, "Hacking", 3, 0.5),
    StatSwap("Offense", 1, "PsiOffense", 3, 1.0),
    StatSwap("Offense", 2, "PsiOffense", 6, 1.0),
    StatSwap("Offense", 1, "Dodge", 3, 1.0),
    StatSwap("Offense", 2, "Dodge", 6, 0.5),
    StatSwap("HP", 1, "Mobility", 1, 2.0),
    StatSwap("HP", 1, "PsiOffense", 12, 1.0),
    StatSwap("Mobility", 1, "PsiOffense", 12, 1.0),
    StatSwap("Dodge", 1, "Will", 1, 1.0),
    StatSwap("Dodge", 2, "Will", 2, 1.0),
    StatSwap("Dodge", 3, "Will", 3, 1.0),
    StatSwap("Dodge", 4, "Will", 4, 1.0),
    StatSwap("Dodge", 1, "Hacking", 1, 0.5),
    StatSwap("Dodge", 2, "Hacking", 2, 0.5),
    StatSwap("Dodge", 3, "Hacking", 3, 0.5),
    StatSwap("Dodge", 4, "Hacking", 4, 0.5),
    StatSwap("Dodge", 4, "PsiOffense", 4, 1.0),
    StatSwap("Dodge", 5, "PsiOffense", 5, 1.0),
    StatSwap("Dodge", 6, "PsiOffense", 6, 1.0),
    StatSwap("Dodge", 7, "PsiOffense", 7, 1.0),
    StatSwap("Will", 1, "Hacking", 1, 0.5),
    StatSwap("Will", 2, "Hacking", 2, 0.5),
    StatSwap("Will", 4, "PsiOffense", 4, 0.5),
    StatSwap("Will", 5, "PsiOffense", 5, 1.0),
    StatSwap("Will", 6, "PsiOffense", 6, 1.0),
    StatSwap("Will", 7, "PsiOffense", 7, 1.0),
)

ANCEV1_SWAPS = (
    StatSwap("Offense", 1, "Offense", 0, 2.0),
    StatSwap("Offense", 2, "Offense", 0, 1.0),
    StatSwap("HP", 1, "HP", 0, 0.75),
    StatSwap("Mobility", 1, "Mobility", 0, 0.75),
    StatSwap("Dodge", 1, "Dodge", 0, 1.25),
    StatSwap("Dodge", 2, "Dodge", 0, 1.0),
    StatSwap("Dodge", 3, "Dodge", 0, 0.75),
    StatSwap("Will", 1, "Will", 0, 1.25),
    StatSwap("Will", 2, "Will", 0, 1.0),
    StatSwap("Will", 3, "Will", 0, 0.75),
    StatSwap("Hacking", 1, "Hacking", 0, 2.0),
    StatSwap("Hacking", 2, "Hacking", 0, 1.0),
    StatSwap("PsiOffense", 1, "PsiOffense", 0, 1.25),
    StatSwap("PsiOffense", 2, "PsiOffense", 0, 1.0),
    StatSwap("PsiOffense", 3, "PsiOffense", 0, 0.75),
)

ANCEV2_SWAPS = (
    StatSwap("Offense", 1, "Offense", 0, 3.5),
    StatSwap("Offense", 2, "Offense", 0, 2.5),
    StatSwap("Offense", 4, "Offense", 0, 3.0),
    StatSwap("HP", 1, "HP", 0, 4.5),
    StatSwap("Mobility", 1, "Mobility", 0, 4.5),
    StatSwap("Will", 1, "Will", 0, 1.5),
    StatSwap("Will", 2, "Will", 0, 1.5),
    StatSwap("Will", 3, "Will", 0, 2.0),
    StatSwap("Will", 4, "Will", 0, 1.5),
    StatSwap("Will", 5, "Will", 0, 1.0),
    StatSwap("Will", 6, "Will", 0, 2.0),
    StatSwap("Will", 7, "Will", 0, 1.0),
    StatSwap("Dodge", 1, "Dodge", 0, 1.5),
    StatSwap("Dodge", 2, "Dodge", 0, 1.5),
    StatSwap("Dodge", 3, "Dodge", 0, 2.5),
    StatSwap("Dodge", 4, "Dodge", 0, 2.5),
    StatSwap("Dodge", 5, "Dodge", 0, 1.0),
    StatSwap("Dodge", 6, "Dodge", 0, 1.5),
    StatSwap("Dodge", 7, "Dodge", 0, 1.0),
    StatSwap("Hacking", 1, "Hacking", 0, 1.0),
    StatSwap("Hacking", 2, "Hacking", 0, 1.0),
    StatSwap("Hacking", 3, "Hacking", 0, 1.0),
    StatSwap("Hacking", 4, "Hacking", 0, 0.5),
    StatSwap("PsiOffense", 3, "PsiOffense", 0, 1.0),
    StatSwap("PsiOffense", 4, "PsiOffense", 0, 1.5),
    StatSwap("PsiOffense", 5, "PsiOffense", 0, 2.0),
    StatSwap("PsiOffense", 6, "PsiOffense", 0, 3.0),
    StatSwap("PsiOffense", 7, "PsiOffense", 0, 2.0),
    StatSwap("PsiOffense", 12, "PsiOffense", 0, 2.0),
)

ANCEV3_SWAPS = (
    StatSwap("Offense", 1, "Offense", 0, 2.5),
    StatSwap("Offense", 2, "Offense", 0, 2.0),
    StatSwap("Offense", 3, "Offense", 0, 1.5),
    StatSwap("Offense", 4, "Offense", 0, 1.0),
    StatSwap("Offense", 5, "Offense", 0, 0.5),
    StatSwap("Offense", 6, "Offense", 0, 0.5),
    StatSwap("Mobility", 1, "Mobility", 0, 3.5),
    StatSwap("HP", 1, "HP", 0, 4.0),
    StatSwap("Will", 1, "Will", 0, 2.0),
    StatSwap("Will", 2, "Will", 0, 2.0),
    StatSwap("Will", 3, "Will", 0, 1.5),
    StatSwap("Will", 4, "Will", 0, 1.5),
    StatSwap("Will", 5, "Will", 0, 1.5),
    StatSwap("Will", 6, "Will", 0, 1.0),
    StatSwap("Will", 7, "Will", 0, 1.0),
    StatSwap("Dodge", 1, "Dodge", 0, 2.5),
    StatSwap("Dodge", 2, "Dodge", 0, 2.5),
    StatSwap("Dodge", 3, "Dodge", 0, 1.5),
    StatSwap("Dodge", 4, "Dodge", 0, 1.5),
    StatSwap("Dodge", 5, "Dodge", 0, 1.5),
    StatSwap("Dodge", 6, "Dodge", 0, 1.0),
    StatSwap("Dodge", 7, "Dodge", 0, 1.0),
    StatSwap("Hacking", 1, "Hacking", 0, 3.0),
    StatSwap("Hacking", 2, "Hacking", 0, 1.0),
    StatSwap("Hacking", 3, "Hacking", 0, 0.75),
    StatSwap("Hacking", 4, "Hacking", 0, 0.5),
    StatSwap("Hacking", 5, "Hacking", 0, 0.25),
    StatSwap("PsiOffense", 1, "PsiOffense", 0, 1.5),
    StatSwap("PsiOffense", 2, "PsiOffense", 0, 1.5),
    StatSwap("PsiOffense", 3, "PsiOffense", 0, 2.0),
    StatSwap("PsiOffense", 4, "PsiOffense", 0, 2.0),
    StatSwap("PsiOffense", 5, "PsiOffense", 0, 2.0),
    StatSwap("PsiOffense", 6, "PsiOffense", 0, 1.5),
    StatSwap("PsiOffense", 7, "PsiOffense", 0, 1.5),
    # StatSwap("PsiOffense", 12, "PsiOffense", 0, 2.0),
)


class EStat:  # Called that because that's what they're called internally in LWOTC
    def __init__(self, stat_range: Stat):
        self.stat_range = stat_range
        self.current = stat_range.default


class Soldier:
    STATS = {
        "Offense": Stat(65, -10, 10, 3),
        "Mobility": Stat(15, -2, 3, 12),
        "HP": Stat(4, -1, 3, 12),
        "Will": Stat(30, -15, 15),
        "Dodge": Stat(5, -15, 15),
        "Hacking": Stat(5, -4, 15),
        "PsiOffense": Stat(20, -15, 15),
    }
    DEFAULT_WEIGHED_STAT_TOTAL: int
    __slots__ = list(STATS) + ["initializer"]

    def __init__(self, initializer=None):
        for stat, range_ in self.STATS.items():
            setattr(self, stat, EStat(range_))

        self.initializer = initializer
        if initializer:
            initializer(self)

    def weighed_stat_total(self) -> int:
        """
        A numeric estimation of how good stats the soldier rolled.
        This is zero for soldiers with no stat randomization.
        This is also zero for unmodded LWOTC soldiers.
        Therefore, this is only ever useful in practice if the swap table
        or the algorithm is modified.
        """
        return sum(
            (getattr(self, stat).current - range_.default) * range_.weight
            for stat, range_ in self.STATS.items()
        )

    def to_dict(self):
        return {stat: getattr(self, stat).current for stat in self.STATS}


Soldier.DEFAULT_WEIGHED_STAT_TOTAL = Soldier().weighed_stat_total()


class StatSwapper:
    __slots__ = ["dice", "swap_table"]

    def __init__(self, dice: Sequence[int] = (), swap_table: Sequence[StatSwap] = ()):
        self.dice = dice
        self.swap_table = swap_table

    def __call__(self, sol: Soldier):
        # Roll for number of stats to apply
        for __ in range(sum(random.randint(1, dice) for dice in self.dice)):
            # Try 1000 times to find a suitable swap
            for ___ in range(1000):
                swap = random.choices(
                    self.swap_table,
                    weights=list(swap.Weight for swap in self.swap_table),
                )[0]

                # 50% chance to flip it around
                if random.getrandbits(1):
                    swap = StatSwap(
                        swap.StatDown,
                        swap.StatDown_Amount,
                        swap.StatUp,
                        swap.StatUp_Amount,
                        swap.Weight,
                    )
                try:
                    self.try_swap(sol, swap)
                except RuntimeError:
                    pass  # Swap not applied, try again
                else:
                    break  # Swap applied, exit inner loop

    def try_swap(self, sol: Soldier, swap: StatSwap):
        old_up = getattr(sol, swap.StatUp).current
        old_down = getattr(sol, swap.StatDown).current

        getattr(sol, swap.StatUp).current += swap.StatUp_Amount
        getattr(sol, swap.StatDown).current -= swap.StatDown_Amount

        if (
            getattr(sol, swap.StatDown).current
            < Soldier.STATS[swap.StatDown].default + Soldier.STATS[swap.StatDown].min_delta
        ) or (
            getattr(sol, swap.StatUp).current
            > Soldier.STATS[swap.StatUp].default + Soldier.STATS[swap.StatUp].max_delta
        ):  # fmt: skip
            getattr(sol, swap.StatUp).current = old_up
            getattr(sol, swap.StatDown).current = old_down
            raise RuntimeError(
                f"Swap {swap} would have swapped an attribute out of bounds"
            )


INITIALIZERS = {
    "lwotc": StatSwapper(5 * (4,), LWOTC_SWAPS),
    "ancev1": StatSwapper(8 * (8,), ANCEV1_SWAPS),
    "ancev2": StatSwapper(10 * (4,), ANCEV2_SWAPS),
    "ancev3": StatSwapper(10 * (4,), ANCEV3_SWAPS),
}
