"""Chart generation service using matplotlib"""

import logging
import uuid
from pathlib import Path
from typing import Literal, Optional, Tuple

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates bar and line charts with FD/BNR styling"""

    def __init__(self, charts_dir: Path = settings.CHARTS_DIR):
        self.charts_dir = charts_dir
        self.colors = settings.COLORS

    def _smart_sample_labels(
        self, x_labels: list[str], y_values: list[float], max_points: int = 15
    ) -> tuple[list[str], list[float], list[int]]:
        """
        Intelligently sample data points to avoid overcrowding

        Args:
            x_labels: Original x-axis labels
            y_values: Corresponding y-values
            max_points: Maximum number of points to show

        Returns:
            Tuple of (sampled_labels, sampled_values, original_indices)
        """
        n = len(x_labels)

        # If we have few points, show all
        if n <= max_points:
            return x_labels, y_values, list(range(n))

        # Calculate step to show approximately max_points
        step = max(1, n // max_points)

        # Always include first and last
        indices = [0]

        # Add intermediate points with even spacing
        current = step
        while current < n - 1:
            indices.append(current)
            current += step

        # Always include last point
        if indices[-1] != n - 1:
            indices.append(n - 1)

        # Sample the data
        sampled_labels = [x_labels[i] for i in indices]
        sampled_values = [y_values[i] for i in indices]

        return sampled_labels, sampled_values, indices

    def _create_chart_figure(
        self,
        chart_type: Literal["bar", "line"],
        x_labels: list[str],
        y_values: list[float],
        title: str,
        x_label: Optional[str],
        y_label: Optional[str],
        style: Literal["fd", "bnr"],
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Internal method to create and style a matplotlib figure

        Args:
            chart_type: Type of chart ("bar" or "line")
            x_labels: Labels for x-axis
            y_values: Values for y-axis
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            style: Color style ("fd" or "bnr")

        Returns:
            Tuple of (figure, axes)
        """
        # Get colors for selected style
        color_scheme = self.colors[style]

        # Smart data sampling for readability
        sampled_labels, sampled_values, _ = self._smart_sample_labels(
            x_labels, y_values, max_points=30
        )

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))

        # Set background color
        fig.patch.set_facecolor(color_scheme["background"])
        ax.set_facecolor(color_scheme["background"])

        # Generate chart based on type
        if chart_type == "bar":
            bars = ax.bar(range(len(sampled_labels)), sampled_values, color=color_scheme["primary"])
            # Add value labels on top of bars (only for visible points or if few points)
            if len(sampled_labels) <= 20:
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height,
                        f"{height:.1f}",
                        ha="center",
                        va="bottom",
                        color=color_scheme["content"],
                        fontsize=9,
                    )
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)

        elif chart_type == "line":
            ax.plot(
                range(len(sampled_labels)),
                sampled_values,
                color=color_scheme["primary"],
                linewidth=2.5,
                marker="o",
                markersize=8,
                markerfacecolor=color_scheme["primary"],
                markeredgecolor=color_scheme["content"],
                markeredgewidth=1.5,
            )
            # Add value labels (only if few points)
            if len(sampled_labels) <= 15:
                for i, y in enumerate(sampled_values):
                    ax.text(
                        i,
                        y,
                        f"{y:.1f}",
                        ha="center",
                        va="bottom",
                        color=color_scheme["content"],
                        fontsize=9,
                    )
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)

        # Set title and labels
        ax.set_title(title, color=color_scheme["content"], fontsize=16, fontweight="bold", pad=20)

        if x_label:
            ax.set_xlabel(
                x_label, color=color_scheme["content"], fontsize=12, fontweight="semibold"
            )

        if y_label:
            ax.set_ylabel(
                y_label, color=color_scheme["content"], fontsize=12, fontweight="semibold"
            )

        # Style the axes
        ax.tick_params(colors=color_scheme["content"], labelsize=10)
        ax.spines["bottom"].set_color(color_scheme["content"])
        ax.spines["left"].set_color(color_scheme["content"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Grid for better readability
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5, color=color_scheme["content"])
        ax.set_axisbelow(True)

        # Rotate x-labels if they're long or if we have many points
        if any(len(str(label)) > 10 for label in sampled_labels) or len(sampled_labels) > 12:
            plt.xticks(rotation=45, ha="right")

        # Tight layout to prevent label cutoff
        plt.tight_layout()

        return fig, ax

    def _cleanup_old_charts(self) -> None:
        """Delete all existing chart files to keep only the latest"""
        try:
            if self.charts_dir.exists():
                for file in self.charts_dir.glob("*"):
                    if file.is_file() and file.suffix in [".png", ".svg"]:
                        file.unlink()
                        logger.debug("Deleted old chart file: %s", file.name)
            logger.info("Cleaned up old chart files")
        except Exception as e:
            logger.warning("Failed to cleanup old charts: %s", e)

    def generate_chart(
        self,
        chart_type: Literal["bar", "line"],
        x_labels: list[str],
        y_values: list[float],
        title: str,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        style: Literal["fd", "bnr"] = "fd",
        format: Literal["png", "svg"] = "png",
    ) -> tuple[str, Path]:
        """
        Generate a chart and return the chart ID and file path

        Args:
            chart_type: Type of chart ("bar" or "line")
            x_labels: Labels for x-axis
            y_values: Values for y-axis
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            style: Color style ("fd" or "bnr")
            format: Output format ("png" or "svg")

        Returns:
            Tuple of (chart_id, file_path)
        """
        # Generate unique chart ID
        chart_id = str(uuid.uuid4())
        filename = f"{chart_id}.{format}"
        filepath = self.charts_dir / filename

        # Create the chart figure using internal method
        fig, ax = self._create_chart_figure(
            chart_type, x_labels, y_values, title, x_label, y_label, style
        )

        # Get colors for saving
        color_scheme = self.colors[style]

        # Save the chart
        plt.savefig(
            filepath,
            format=format,
            dpi=300 if format == "png" else None,
            facecolor=color_scheme["background"],
            edgecolor="none",
            bbox_inches="tight",
        )
        plt.close()

        logger.debug("Generated %s chart: %s.%s", chart_type, chart_id, format)
        return chart_id, filepath

    def generate_both_formats(
        self,
        chart_type: Literal["bar", "line"],
        x_labels: list[str],
        y_values: list[float],
        title: str,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        style: Literal["fd", "bnr"] = "fd",
    ) -> dict[str, tuple[str, Path]]:
        """
        Generate both PNG and SVG versions of a chart

        Returns:
            Dict with 'png' and 'svg' keys containing (chart_id, filepath) tuples
        """
        # Clean up old charts before generating new ones
        self._cleanup_old_charts()

        # Generate PNG using the main method
        png_id, png_path = self.generate_chart(
            chart_type, x_labels, y_values, title, x_label, y_label, style, "png"
        )

        # Generate SVG using the main method with the same base ID
        svg_id, svg_path = self.generate_chart(
            chart_type, x_labels, y_values, title, x_label, y_label, style, "svg"
        )

        # Override svg_id to match png_id for consistency
        new_svg_filename = f"{png_id}.svg"
        new_svg_path = self.charts_dir / new_svg_filename

        # Rename the SVG file to use the PNG's ID
        if svg_path.exists():
            svg_path.rename(new_svg_path)
            svg_path = new_svg_path

        logger.info("Generated both formats for chart: %s", png_id)
        return {"png": (png_id, png_path), "svg": (png_id, new_svg_path)}  # Use same ID for both


# Global instance
chart_generator = ChartGenerator()
