import argparse
from textwrap import dedent

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from soldier import Soldier, LWOTCSoldier, ActuallyNCESoldier

COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]
EXPLAINER = {
    "edgecolor": "black",
    "facecolor": "lightgray",
    "linewidth": 0.75,
    "alpha": 0.5,
}
IMG_FILE_PREFIX = "SteamWorkshop_"

if __name__ == "__main__":
    parser = argparse.ArgumentParser("python steam_workshop_images.py")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Number of soldiers to generate, per generation type",
    )
    args = parser.parse_args()

    lwotc_sample = dict(
        (stat, np.zeros(range_.max_delta - range_.min_delta + 1))
        for stat, range_ in Soldier.STATS.items()
    )

    mod_sample = dict(
        (stat, np.zeros(range_.max_delta - range_.min_delta + 1))
        for stat, range_ in Soldier.STATS.items()
    )

    mod_stat_totals = []

    for _ in range(args.number):
        lwotc_soldier = LWOTCSoldier()
        mod_soldier = ActuallyNCESoldier()
        for stat, range_ in Soldier.STATS.items():
            lwotc_sample[stat][
                getattr(lwotc_soldier, stat).current
                - (range_.default + range_.min_delta)
            ] += 1
            mod_sample[stat][
                getattr(mod_soldier, stat).current - (range_.default + range_.min_delta)
            ] += 1
        mod_stat_totals.append(mod_soldier.weighed_stat_total())

    # The 7 base stats
    plt.rcParams["legend.fancybox"] = False
    plt.rcParams["legend.framealpha"] = EXPLAINER["alpha"]
    plt.rcParams["legend.facecolor"] = EXPLAINER["facecolor"]
    plt.rcParams["legend.edgecolor"] = EXPLAINER["edgecolor"]
    # plt.rcParams["legend.linewidth"] = EXPLAINER["linewidth"]

    for stat, range_ in Soldier.STATS.items():
        values = range(
            range_.default + range_.min_delta, range_.default + range_.max_delta + 1
        )
        fig, ax = plt.subplots(1, 1)
        ax.set_title(f"{stat} (n = {args.number})")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(args.number))
        for i, sample in enumerate((lwotc_sample, mod_sample)):
            ax.bar(
                x=[value - 0.75 / 4 + i * 0.75 / 2 for value in values],
                width=0.75 / 2,
                height=sample[stat],
                color=COLORS[i],
                edgecolor="black",
                linewidth=0.75,
            )
            legend = ax.legend(["Base LWOTC", "Actually NCE"])
            legend.get_frame().set_edgecolor(EXPLAINER["edgecolor"])
            legend.get_frame().set_linewidth(EXPLAINER["linewidth"])
            fig.savefig(
                f"{IMG_FILE_PREFIX}{stat}.png",
            )

    # Weighed Stat Total chart
    fig, ax = plt.subplots(1, 1)
    ax.set_title(f"Weighed Stat Totals (n = {args.number})")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(args.number))
    ax.hist(
        mod_stat_totals,
        color=COLORS[1],
        edgecolor="black",
        linewidth=0.75,
    )
    ax.set_ylim([0, ax.get_ylim()[1] * 1.35])
    ax.text(
        0.5,
        0.96,
        dedent(
            """
            The relative quality of soldiers generated by this mod,
            in terms of how LWOTC's swap table values stats.
            This is zero for all unmodded LWOTC soldiers.
            Aim is worth 4, Mob and HP are worth 12,
            everything else is 1.
            """
        ).strip(),
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="center",
        bbox=EXPLAINER,
    )
    fig.savefig(f"{IMG_FILE_PREFIX}Totals.png")