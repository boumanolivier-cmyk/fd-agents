"""Chart generation service using matplotlib"""
import uuid
from pathlib import Path
from typing import Literal, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from app.config.settings import settings


class ChartGenerator:
    """Generates bar and line charts with FD/BNR styling"""
    
    def __init__(self, charts_dir: Path = settings.CHARTS_DIR):
        self.charts_dir = charts_dir
        self.colors = settings.COLORS
    
    def _smart_sample_labels(
        self, 
        x_labels: list[str], 
        y_values: list[float],
        max_points: int = 15
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
    
    def generate_chart(
        self,
        chart_type: Literal["bar", "line"],
        x_labels: list[str],
        y_values: list[float],
        title: str,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        style: Literal["fd", "bnr"] = "fd",
        format: Literal["png", "svg"] = "png"
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
        
        # Get colors for selected style
        color_scheme = self.colors[style]
        
        # Smart data sampling for readability (reduces visual clutter)
        sampled_labels, sampled_values, original_indices = self._smart_sample_labels(
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
                        bar.get_x() + bar.get_width()/2., 
                        height,
                        f'{height:.1f}',
                        ha='center', 
                        va='bottom',
                        color=color_scheme["content"],
                        fontsize=9
                    )
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)
            
        elif chart_type == "line":
            ax.plot(
                range(len(sampled_labels)), 
                sampled_values, 
                color=color_scheme["primary"],
                linewidth=2.5,
                marker='o',
                markersize=8,
                markerfacecolor=color_scheme["primary"],
                markeredgecolor=color_scheme["content"],
                markeredgewidth=1.5
            )
            # Add value labels (only if few points)
            if len(sampled_labels) <= 15:
                for i, y in enumerate(sampled_values):
                    ax.text(
                        i, 
                        y, 
                        f'{y:.1f}',
                        ha='center',
                        va='bottom',
                        color=color_scheme["content"],
                        fontsize=9
                    )
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)
        
        # Set title and labels
        ax.set_title(
            title, 
            color=color_scheme["content"], 
            fontsize=16, 
            fontweight='bold',
            pad=20
        )
        
        if x_label:
            ax.set_xlabel(
                x_label, 
                color=color_scheme["content"], 
                fontsize=12,
                fontweight='semibold'
            )
        
        if y_label:
            ax.set_ylabel(
                y_label, 
                color=color_scheme["content"], 
                fontsize=12,
                fontweight='semibold'
            )
        
        # Style the axes
        ax.tick_params(colors=color_scheme["content"], labelsize=10)
        ax.spines['bottom'].set_color(color_scheme["content"])
        ax.spines['left'].set_color(color_scheme["content"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Grid for better readability
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, color=color_scheme["content"])
        ax.set_axisbelow(True)
        
        # Rotate x-labels if they're long or if we have many points
        if any(len(str(label)) > 10 for label in sampled_labels) or len(sampled_labels) > 12:
            plt.xticks(rotation=45, ha='right')
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(
            filepath, 
            format=format, 
            dpi=300 if format == "png" else None,
            facecolor=color_scheme["background"],
            edgecolor='none',
            bbox_inches='tight'
        )
        plt.close()
        
        return chart_id, filepath
    
    def generate_both_formats(
        self,
        chart_type: Literal["bar", "line"],
        x_labels: list[str],
        y_values: list[float],
        title: str,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
        style: Literal["fd", "bnr"] = "fd"
    ) -> dict[str, tuple[str, Path]]:
        """
        Generate both PNG and SVG versions of a chart
        
        Returns:
            Dict with 'png' and 'svg' keys containing (chart_id, filepath) tuples
        """
        # Generate PNG
        png_id, png_path = self.generate_chart(
            chart_type, x_labels, y_values, title, x_label, y_label, style, "png"
        )
        
        # Generate SVG with same base ID
        svg_id = png_id  # Use same ID for both formats
        svg_filename = f"{svg_id}.svg"
        svg_path = self.charts_dir / svg_filename
        
        # Get sampled data
        sampled_labels, sampled_values, original_indices = self._smart_sample_labels(
            x_labels, y_values, max_points=30
        )
        
        # Create figure again for SVG
        color_scheme = self.colors[style]
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(color_scheme["background"])
        ax.set_facecolor(color_scheme["background"])
        
        if chart_type == "bar":
            bars = ax.bar(range(len(sampled_labels)), sampled_values, color=color_scheme["primary"])
            if len(sampled_labels) <= 20:
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2., height, f'{height:.1f}',
                        ha='center', va='bottom', color=color_scheme["content"], fontsize=9
                    )
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)
            
        elif chart_type == "line":
            ax.plot(
                range(len(sampled_labels)), sampled_values, color=color_scheme["primary"],
                linewidth=2.5, marker='o', markersize=8,
                markerfacecolor=color_scheme["primary"],
                markeredgecolor=color_scheme["content"], markeredgewidth=1.5
            )
            if len(sampled_labels) <= 15:
                for i, y in enumerate(sampled_values):
                    ax.text(i, y, f'{y:.1f}', ha='center', va='bottom', 
                           color=color_scheme["content"], fontsize=9)
            ax.set_xticks(range(len(sampled_labels)))
            ax.set_xticklabels(sampled_labels)
        
        ax.set_title(title, color=color_scheme["content"], fontsize=16, 
                    fontweight='bold', pad=20)
        if x_label:
            ax.set_xlabel(x_label, color=color_scheme["content"], fontsize=12, 
                         fontweight='semibold')
        if y_label:
            ax.set_ylabel(y_label, color=color_scheme["content"], fontsize=12, 
                         fontweight='semibold')
        
        ax.tick_params(colors=color_scheme["content"], labelsize=10)
        ax.spines['bottom'].set_color(color_scheme["content"])
        ax.spines['left'].set_color(color_scheme["content"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, color=color_scheme["content"])
        ax.set_axisbelow(True)
        
        if any(len(str(label)) > 10 for label in sampled_labels) or len(sampled_labels) > 12:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(svg_path, format='svg', facecolor=color_scheme["background"],
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        return {
            "png": (png_id, png_path),
            "svg": (svg_id, svg_path)
        }


# Global instance
chart_generator = ChartGenerator()
