"""Excel file parsing service"""

import re
from pathlib import Path
from typing import Literal, Optional

import pandas as pd


class ExcelParser:
    """Parse Excel files to extract chart data"""

    def parse_excel(self, file_path: Path) -> dict:
        """
        Parse an Excel file and extract data

        Args:
            file_path: Path to the Excel file

        Returns:
            Dict with 'success', 'data', 'columns', 'rows', and 'text' keys
        """
        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name=0)

            # Convert to dict and get basic info
            data_dict = df.to_dict("records")
            columns = df.columns.tolist()

            # Create a text representation for the AI agent
            text_representation = self._dataframe_to_text(df)

            return {
                "success": True,
                "data": data_dict,
                "columns": columns,
                "rows": len(df),
                "text": text_representation,
                "dataframe": df,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": f"Error reading Excel file: {str(e)}",
            }

    def _dataframe_to_text(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to a text representation for the AI agent

        Args:
            df: Pandas DataFrame

        Returns:
            Text representation of the data
        """
        lines = []
        lines.append(f"Excel file contains {len(df)} rows and {len(df.columns)} columns.")
        lines.append(f"Columns: {', '.join(df.columns.tolist())}")
        lines.append("\nData:")

        # If it looks like it has 2 columns (common for charts), format nicely
        if len(df.columns) == 2:
            col1, col2 = df.columns[0], df.columns[1]
            for _, row in df.iterrows():
                lines.append(f"{row[col1]} = {row[col2]}")
        else:
            # Otherwise, show the raw data
            lines.append(df.to_string(index=False))

        return "\n".join(lines)

    def auto_detect_chart_data(self, df: pd.DataFrame, filename: str = "") -> Optional[dict]:
        """
        Attempt to auto-detect chart data from DataFrame

        Args:
            df: Pandas DataFrame
            filename: Original filename for context clues

        Returns:
            Dict with x_labels, y_values, and intelligent chart_type if detected, None otherwise
        """
        # Simple heuristic: if 2 columns, first is labels, second is values
        if len(df.columns) == 2:
            col1, col2 = df.columns[0], df.columns[1]

            # Check if second column is numeric
            if pd.api.types.is_numeric_dtype(df[col2]):
                x_labels = df[col1].astype(str).tolist()
                y_values = df[col2].tolist()

                # Intelligently determine chart type
                chart_type = self._determine_chart_type(x_labels, filename, str(col1))

                return {
                    "x_labels": x_labels,
                    "y_values": y_values,
                    "x_label": str(col1),
                    "y_label": str(col2),
                    "chart_type": chart_type,
                }

        return None

    def _determine_chart_type(
        self, x_labels: list[str], filename: str = "", x_column_name: str = ""
    ) -> Literal["bar", "line"]:
        """
        Intelligently determine whether data should be a bar or line chart

        Args:
            x_labels: The x-axis labels
            filename: Original filename for context
            x_column_name: Name of the x-axis column

        Returns:
            "line" or "bar"
        """
        # Combine all text for analysis
        all_text = f"{filename} {x_column_name} {' '.join(x_labels)}".lower()

        # Strong indicators for LINE charts (time-based data)
        time_indicators = [
            # Temporal words
            r"\b(year|month|quarter|week|day|date|time|period|hour|minute)\b",
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
            r"\b(january|february|march|april|june|july|august|september|october|november|december)\b",
            r"\b(q1|q2|q3|q4)\b",
            r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            r"\b(trend|timeline|historical|forecast|growth|over time)\b",
            # Year patterns (2020, 2021, etc.)
            r"\b(19|20)\d{2}\b",
            # Month/Year patterns (2024-01, Jan-2024, etc.)
            r"\d{4}-\d{2}",
            r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[-\s]?\d{2,4}",
            # Quarter patterns
            r"q[1-4][-\s]?\d{2,4}",
            r"\d{4}[-\s]?q[1-4]",
        ]

        # Check for time indicators
        for pattern in time_indicators:
            if re.search(pattern, all_text):
                return "line"

        # Check x_labels for sequential time patterns
        # Years: 2020, 2021, 2022...
        if len(x_labels) >= 3:
            try:
                # Try to convert to numbers and check if sequential
                nums = [
                    int(re.search(r"\d{4}", label).group())
                    for label in x_labels[:3]
                    if re.search(r"\d{4}", label)
                ]
                if len(nums) >= 2 and all(nums[i + 1] - nums[i] == 1 for i in range(len(nums) - 1)):
                    return "line"
            except (ValueError, AttributeError):
                pass

        # If many data points (10+), line chart is cleaner
        if len(x_labels) >= 10:
            # Check if labels look sequential (Week 1, Week 2, etc.)
            if all(
                str(i) in label or f"{i:02d}" in label for i, label in enumerate(x_labels[:5], 1)
            ):
                return "line"
            return "line"  # Default to line for many points

        # Strong indicators for BAR charts (categorical data)
        category_indicators = [
            r"\b(product|category|region|department|country|city|team|company)\b",
            r"\b(compar|versus|vs|breakdown|distribution|by category)\b",
            r"\b(top|rank|best|worst)\b",
        ]

        for pattern in category_indicators:
            if re.search(pattern, all_text):
                return "bar"

        # Default: BAR for few categorical items, LINE for sequential data
        return "bar" if len(x_labels) < 10 else "line"


# Global instance
excel_parser = ExcelParser()
