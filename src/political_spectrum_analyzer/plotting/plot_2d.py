from __future__ import annotations

from typing import Iterable

from matplotlib.axes import Axes
from matplotlib.patches import Ellipse, Rectangle

from political_spectrum_analyzer.constants import (
    DEFAULT_COLOR_PALETTE,
    PLOT_X_MAX,
    PLOT_X_MIN,
    PLOT_Y_MAX,
    PLOT_Y_MIN,
)
from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint


def draw_base(ax: Axes) -> None:
    ax.clear()
    ax.set_xlim(PLOT_X_MIN, PLOT_X_MAX)
    ax.set_ylim(PLOT_Y_MIN, PLOT_Y_MAX)

    ax.add_patch(Rectangle((PLOT_X_MIN, 0), 4, 4, color="#ffcccc", alpha=0.22, zorder=0))
    ax.add_patch(Rectangle((0, 0), 4, 4, color="#ccffcc", alpha=0.22, zorder=0))
    ax.add_patch(Rectangle((PLOT_X_MIN, PLOT_Y_MIN), 4, 4, color="#ccccff", alpha=0.22, zorder=0))
    ax.add_patch(Rectangle((0, PLOT_Y_MIN), 4, 4, color="#ffffcc", alpha=0.22, zorder=0))

    ax.axhline(0, color="black", linewidth=1.2, zorder=3)
    ax.axvline(0, color="black", linewidth=1.2, zorder=3)
    ax.grid(True, linestyle="--", alpha=0.35, zorder=1)

    ax.set_xlabel("Economic: Left (x < 0) | Right (x > 0)", fontsize=9)
    ax.set_ylabel("Societal: Libertarian (y < 0) | Authoritarian (y > 0)", fontsize=9)


def draw_people(ax: Axes, people: Iterable[PersonResult]) -> None:
    for index, person in enumerate(people):
        color = DEFAULT_COLOR_PALETTE[index % len(DEFAULT_COLOR_PALETTE)]
        ax.plot(person.x, person.y, marker="x", color=color, markersize=8, linewidth=2, zorder=6)
        ax.text(person.x, person.y, " " + person.name, color=color, fontsize=9, zorder=7)


def draw_personalities(ax: Axes, personalities: Iterable[PersonalityPoint]) -> None:
    for point in personalities:
        ell = Ellipse(
            (point.x, point.y),
            width=2 * point.ux,
            height=2 * point.uy,
            alpha=0.18,
            linewidth=1.1,
            edgecolor="black",
            facecolor="gray",
            zorder=2,
        )
        ax.add_patch(ell)
        ax.text(
            point.x,
            point.y,
            point.name,
            fontsize=8,
            ha="center",
            va="center",
            color="black",
            alpha=0.85,
            zorder=4,
        )