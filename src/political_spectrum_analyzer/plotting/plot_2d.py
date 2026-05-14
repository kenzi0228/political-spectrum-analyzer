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


def _confidence_alpha(confidence: str) -> float:
    confidence = confidence.lower().strip()

    if confidence == "high":
        return 0.14
    if confidence == "medium":
        return 0.18
    if confidence == "low":
        return 0.24

    return 0.18


def _confidence_scale(confidence: str) -> float:
    confidence = confidence.lower().strip()

    if confidence == "high":
        return 0.85
    if confidence == "medium":
        return 1.0
    if confidence == "low":
        return 1.25

    return 1.0


def _add_quadrant_labels(ax: Axes) -> None:
    labels = [
        (-2.6, 3.55, "Left / Authoritarian"),
        (2.25, 3.55, "Right / Authoritarian"),
        (-2.65, -3.55, "Left / Libertarian"),
        (2.2, -3.55, "Right / Libertarian"),
    ]

    for x, y, label in labels:
        ax.text(
            x,
            y,
            label,
            fontsize=9,
            fontweight="bold",
            alpha=0.45,
            ha="center",
            va="center",
            zorder=1,
        )


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

    ax.set_xlabel("Economic axis: Left (x < 0) | Right (x > 0)", fontsize=9)
    ax.set_ylabel("Societal axis: Libertarian (y < 0) | Authoritarian (y > 0)", fontsize=9)

    ax.set_title("Political Spectrum Projection", fontsize=12, fontweight="bold", pad=10)

    _add_quadrant_labels(ax)


def draw_people(ax: Axes, people: Iterable[PersonResult]) -> None:
    for index, person in enumerate(people):
        color = DEFAULT_COLOR_PALETTE[index % len(DEFAULT_COLOR_PALETTE)]

        ax.scatter(
            person.x,
            person.y,
            marker="X",
            s=90,
            color=color,
            edgecolors="black",
            linewidths=0.7,
            zorder=7,
        )

        label = f"{person.name} ({person.x:.2f}, {person.y:.2f})"

        ax.text(
            person.x + 0.08,
            person.y + 0.08,
            label,
            color=color,
            fontsize=9,
            fontweight="bold",
            zorder=8,
        )


def draw_personalities(ax: Axes, personalities: Iterable[PersonalityPoint]) -> None:
    for point in personalities:
        confidence = getattr(point, "confidence", "medium")
        scale = _confidence_scale(confidence)
        alpha = _confidence_alpha(confidence)

        ell = Ellipse(
            (point.x, point.y),
            width=2 * point.ux * scale,
            height=2 * point.uy * scale,
            alpha=alpha,
            linewidth=1.1,
            edgecolor="black",
            facecolor="gray",
            zorder=2,
        )
        ax.add_patch(ell)

        label = point.name
        if getattr(point, "is_estimated", True):
            label = f"{label} (est.)"

        ax.text(
            point.x,
            point.y,
            label,
            fontsize=8,
            ha="center",
            va="center",
            color="black",
            alpha=0.85,
            zorder=4,
        )