import random
from collections import namedtuple

Stat = namedtuple(
    "Stat", ("default", "min_delta", "max_delta", "weight"), defaults=(1,)
)

StatSwap = namedtuple(
    "StatSwap", ("StatUp", "StatUp_Amount", "StatDown", "StatDown_Amount", "Weight")
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
    __slots__ = STATS

    def __init__(self):
        for stat, range_ in self.STATS.items():
            setattr(self, stat, EStat(range_))

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

    def try_swap(self, swap: StatSwap):
        old_up = getattr(self, swap.StatUp).current
        old_down = getattr(self, swap.StatDown).current

        getattr(self, swap.StatUp).current += swap.StatUp_Amount
        getattr(self, swap.StatDown).current -= swap.StatDown_Amount

        if (
            getattr(self, swap.StatDown).current
            < self.STATS[swap.StatDown].default + self.STATS[swap.StatDown].min_delta
        ) or (
            getattr(self, swap.StatUp).current
            > self.STATS[swap.StatUp].default + self.STATS[swap.StatUp].max_delta
        ):
            getattr(self, swap.StatUp).current = old_up
            getattr(self, swap.StatDown).current = old_down
            raise RuntimeError(
                f"Swap {swap} would have shifted an attribute out of bounds"
            )


class StatSwapSoldier(Soldier):
    dice_count = 0
    dice_size = 1

    def __init__(self):
        super().__init__()

        # Roll for number of stats to apply
        for __ in range(
            sum(random.randint(1, self.dice_size) for _ in range(self.dice_count))
        ):
            # Try 1000 times to find a suitable swap
            for ___ in range(1000):
                swap = random.choices(
                    self.STAT_SWAPS,
                    weights=list(swap.Weight for swap in self.STAT_SWAPS),
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
                    self.try_swap(swap)
                except RuntimeError:
                    pass  # Swap not applied, try again
                else:
                    break  # Swap applied, exit inner loop


class LWOTCSoldier(StatSwapSoldier):
    """Implements soldier generation as defined in unmodded LWOTC."""

    dice_count = 5
    dice_size = 4

    STAT_SWAPS = [
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
    ]


class ActuallyNCESoldier(StatSwapSoldier):
    """
    Implements soldier generation as defined in LWOTC, but with
    the swap table defined by the mod "Actually Not Created Equal".
    """

    dice_count = 8
    dice_size = 8

    STAT_SWAPS = [
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
    ]
