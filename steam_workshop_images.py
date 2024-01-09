import argparse
from textwrap import dedent
from typing import Any

import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from numpy.typing import NDArray


from soldier import Soldier, INITIALIZERS

COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]
CORR_COLORMAP = mpl.colormaps["seismic"]
EXPLAINER = {
    "edgecolor": "black",
    "facecolor": "lightgray",
    "linewidth": 0.75,
    "alpha": 0.5,
}
IMG_PREFIX = "img/SteamWorkshop"

AIM_RANGE = range(
    Soldier.STATS["Offense"].default + Soldier.STATS["Offense"].min_delta,
    Soldier.STATS["Offense"].default + Soldier.STATS["Offense"].max_delta + 1,
)
MOB_RANGE = range(
    Soldier.STATS["Mobility"].default + Soldier.STATS["Mobility"].min_delta,
    Soldier.STATS["Mobility"].default + Soldier.STATS["Mobility"].max_delta + 1,
)


class FigSaver:
    """
    Saves matplotlib figures to files that have otherwise the same names,
    but also have sequential numbering in the end.
    """

    count = 0

    @staticmethod
    def save_fig(fig):
        __class__.count += 1
        fig.savefig(f"{IMG_PREFIX}{str(__class__.count).zfill(2)}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("python steam_workshop_images.py")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Number of soldiers to generate per sample",
    )
    args = parser.parse_args()

    plt.rcParams["legend.fancybox"] = False
    plt.rcParams["legend.framealpha"] = EXPLAINER["alpha"]
    plt.rcParams["legend.facecolor"] = EXPLAINER["facecolor"]
    plt.rcParams["legend.edgecolor"] = EXPLAINER["edgecolor"]
    stat_figs = {}
    stat_axes = {}

    # Create figures/axes
    for stat, range_ in Soldier.STATS.items():
        fig, ax = plt.subplots()
        stat_figs[stat], stat_axes[stat] = fig, ax

    totals_fig, totals_ax = plt.subplots()
    corr_fig, corr_axes = plt.subplot_mosaic(
        [["top", "top_text"], ["bottom", "bottom_text"], ["colorbar", "colorbar"]],
        width_ratios=[50, 50],
        height_ratios=[40, 40, 10],
    )
    mob_aim_fig, mob_aim_axes = plt.subplot_mosaic(
        [["top", "colorbar"], ["bottom", "colorbar"]], width_ratios=[95, 5]
    )
    mob_aim_samples = []  # Need to plot after loop, otherwise colormap won't be shared

    for sample_index, initializer in enumerate(INITIALIZERS[key] for key in ("lwotc", "ancev1")):
        # Put sample in a matrix
        sample = np.zeros([args.number, len(Soldier.STATS)], dtype=np.int16)
        totals = np.zeros([args.number], dtype=np.int16)
        mob_aim_sample = np.zeros([len(MOB_RANGE), len(AIM_RANGE)], dtype=np.uint64)

        # TODO: Refactor to use `main.generate_sample`
        for i in range(args.number):
            sol = Soldier(initializer)
            sample[i, :] = [getattr(sol, stat).current for stat in Soldier.STATS]
            totals[i] = sol.weighed_stat_total() - Soldier.DEFAULT_WEIGHED_STAT_TOTAL
            mob_aim_sample[
                getattr(sol, "Mobility").current - min(MOB_RANGE),
                getattr(sol, "Offense").current - min(AIM_RANGE),
            ] += 1

        # The 7 stat charts
        for stat_index, (stat, range_) in enumerate(Soldier.STATS.items()):
            values = range(
                range_.default + range_.min_delta, range_.default + range_.max_delta + 1
            )
            stat_axes[stat].bar(
                x=[value - 0.75 / 4 + sample_index * 0.75 / 2 for value in values],
                width=0.75 / 2,
                height=[(sample[:, stat_index] == value).sum() for value in values],
                color=COLORS[sample_index],
                edgecolor="black",
                linewidth=0.75,
            )

        # Weighed Stat Total chart
        if initializer == ancev1_initializer:
            totals_ax.hist(
                totals,
                color=COLORS[1],
                edgecolor="black",
                linewidth=0.75,
            )

        # Covariance matrices
        cov = np.cov(sample.T)
        cov /= np.sqrt(np.asmatrix(cov).diagonal().T * np.asmatrix(cov).diagonal())
        corr_axes[("top", "bottom")[sample_index]].pcolor(
            cov,
            cmap=CORR_COLORMAP,
            vmin=-max(abs(cov.min(None)), abs(cov.max(None))),
            vmax=max(abs(cov.min(None)), abs(cov.max(None))),
        )

        # Aim/Mob correlation chart
        mob_aim_samples.append(mob_aim_sample)

    # Edit axes, save figs
    for stat in Soldier.STATS:
        ax = stat_axes[stat]
        ax.set_title(f"{stat} (n = {args.number})")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(args.number))
        legend = ax.legend(["Base LWOTC", "Actually NCE"])
        legend.get_frame().set_edgecolor(EXPLAINER["edgecolor"])
        legend.get_frame().set_linewidth(EXPLAINER["linewidth"])
        FigSaver.save_fig(stat_figs[stat])

    totals_ax.set_title(f"Weighed Stat Totals (n = {args.number})")
    totals_ax.yaxis.set_major_formatter(mtick.PercentFormatter(args.number))
    totals_ax.set_ylim([0, totals_ax.get_ylim()[1] * 1.35])
    totals_ax.text(
        0.5,
        0.96,
        dedent(
            """
            The relative quality of soldiers generated by this mod,
            in terms of how LWOTC's swap table values stats.
            This is zero for all unmodded LWOTC soldiers.
            Offense is worth 3, Mobility and HP are worth 12,
            everything else is 1.
            """
        ).strip(),
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="center",
        bbox=EXPLAINER,
    )
    FigSaver.save_fig(totals_fig)

    for ax_key in ("top", "bottom"):
        ax = corr_axes[ax_key]
        ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
        ax.set_xticks(
            [0.5 + i for i in range(len(Soldier.STATS))],
            labels=Soldier.STATS,
        )
        ax.set_ylim(len(Soldier.STATS), 0)
        ax.set_yticks(
            [0.5 + i for i in range(len(Soldier.STATS))],
            labels=Soldier.STATS,
        )
        plt.setp(
            ax.get_xticklabels(),
            rotation=45,
            ha="left",
            rotation_mode="anchor",
        )
    for ax_key in ("top_text", "bottom_text"):
        ax = corr_axes[ax_key]
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    corr_axes["top_text"].text(
        0.65,
        0.55,
        dedent(
            """
            In base LWOTC, all stats are
            (mostly) negatively correlated.
            This is expected, since one
            high stat predicts others to
            be lower -- and vice versa.
            """
        ).strip(),
        verticalalignment="center",
        horizontalalignment="center",
        bbox=EXPLAINER,
    )
    corr_axes["bottom_text"].text(
        0.65,
        0.55,
        dedent(
            """
            This mod's goal was to make
            stat rolls independent of
            each other. According to
            these correlations, the goal
            was met.
            """
        ).strip(),
        verticalalignment="center",
        horizontalalignment="center",
        bbox=EXPLAINER,
    )

    corr_axes["colorbar"].set_axis_off()
    colorbar = corr_fig.colorbar(
        cm.ScalarMappable(cmap=CORR_COLORMAP),
        ax=corr_axes["colorbar"],
        orientation="horizontal",
        location="top",
        fraction=1,
    )
    colorbar.set_ticks(
        [0, 0.5, 1],
        labels=["More anticorrelated", "Uncorrelated", "More correlated"],
    )
    corr_fig.tight_layout()
    FigSaver.save_fig(corr_fig)

    mob_aim_max = max(sample.max(None) for sample in mob_aim_samples)
    for ax, sample in zip(
        [mob_aim_axes["top"], mob_aim_axes["bottom"]], np.array(mob_aim_samples)
    ):
        ax.pcolor(sample, vmax=mob_aim_max)

        aim_tick_range = range(AIM_RANGE.start, AIM_RANGE.stop, 5)
        ax.set_xticks(
            [0.5 + 5 * i for i in range(len(aim_tick_range))],
            labels=aim_tick_range,
        )
        ax.set_yticks(
            [0.5 + i for i in range(len(MOB_RANGE))],
            labels=MOB_RANGE,
        )
        ax.set_xlabel("Offense")
        ax.set_ylabel("Mobility")
    mob_aim_axes["top"].set_title(f"Base LWOTC (n = {args.number})")
    mob_aim_axes["bottom"].set_title(f"Actually NCE (n = {args.number})")

    mob_aim_axes["colorbar"].set_axis_off()
    colorbar = mob_aim_fig.colorbar(
        cm.ScalarMappable(),
        ax=mob_aim_axes["colorbar"],
        orientation="vertical",
        location="right",
        fraction=1,
    )
    colorbar.set_ticks(
        [i / 5 for i in range(6)],
        labels=[f"{100 * i * mob_aim_max / 5 / args.number}%" for i in range(6)],
    )
    mob_aim_fig.tight_layout()
    FigSaver.save_fig(mob_aim_fig)
