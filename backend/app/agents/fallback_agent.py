"""Rule-based fallback agent for chart generation (no API key required)"""
import re
from typing import Optional, List, Dict, Any, Tuple
from app.models.schemas import ChartData


class FallbackChartAgent:
    """
    Rule-based chart agent that works without an API key.
    Uses pattern matching to extract chart data from user messages.
    """
    
    def __init__(self):
        # Keywords for chart type detection
        self.bar_keywords = ['bar chart', 'bar graph', 'bar', 'compare', 'comparison', 'versus']
        self.line_keywords = ['line chart', 'line graph', 'line', 'trend', 'over time', 'timeline']
        
        # Time-related patterns for line chart detection
        self.time_patterns = [
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(q1|q2|q3|q4)\b',
            r'\b(20\d{2})\b',  # Years like 2020-2099
            r'\b(mon|tue|wed|thu|fri|sat|sun)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(week|month|quarter|year)\b',
        ]
        
        # Color scheme keywords
        self.bnr_keywords = ['bnr', 'yellow', 'news', 'radio', 'broadcast']
        self.fd_keywords = ['fd', 'teal', 'financial', 'financieele dagblad']
        
        # Style change keywords
        self.style_change_keywords = ['change color', 'change style', 'use', 'in', 'colors', 'style', 'make it']
        
        # Refusal keywords
        self.refusal_keywords = ['weather', 'essay', 'joke', 'homework', 'write', 'story', 'code', 
                                'program', 'calculate', 'what is', 'help me with', 'pie chart', 
                                'scatter plot', 'histogram']
    
    def _extract_data_pairs(self, message: str) -> Optional[Tuple[List[str], List[float]]]:
        """
        Extract key=value pairs from message.
        Examples: "Q1=100, Q2=150" or "Apple=25, Banana=30"
        """
        # Pattern for key=value pairs
        pattern = r'([a-zA-Z0-9\s\-\/]+)\s*[=:]\s*([0-9]+\.?[0-9]*)'
        matches = re.findall(pattern, message)
        
        if not matches or len(matches) < 2:
            return None
        
        x_labels = [match[0].strip() for match in matches]
        try:
            y_values = [float(match[1]) for match in matches]
        except ValueError:
            return None
        
        return x_labels, y_values
    
    def _is_time_series(self, x_labels: List[str]) -> bool:
        """Check if x_labels represent time-based data"""
        combined_text = ' '.join(x_labels).lower()
        
        for pattern in self.time_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        
        # Check for sequential years or quarters
        if all(re.match(r'^(q|Q)[1-4]$', label.strip()) for label in x_labels):
            return True
        if all(re.match(r'^(20\d{2})$', label.strip()) for label in x_labels):
            return True
        
        return False
    
    def _detect_chart_type(self, message: str, x_labels: List[str]) -> str:
        """
        Detect chart type based on explicit request or data characteristics.
        Priority: Explicit request > Data analysis
        """
        message_lower = message.lower()
        
        # FIRST PRIORITY: Explicit user request
        for keyword in self.bar_keywords:
            if keyword in message_lower:
                return "bar"
        
        for keyword in self.line_keywords:
            if keyword in message_lower:
                return "line"
        
        # SECOND PRIORITY: Intelligent selection based on data
        if self._is_time_series(x_labels):
            return "line"
        
        # DEFAULT: Bar chart for categorical data, but prefer line for many points
        if len(x_labels) >= 10:
            return "line"
        
        return "bar"
    
    def _detect_color_scheme(self, message: str, x_labels: List[str] = None) -> Optional[str]:
        """Detect color scheme preference from message"""
        message_lower = message.lower()
        
        # Explicit BNR request
        for keyword in self.bnr_keywords:
            if keyword in message_lower:
                return "bnr"
        
        # Explicit FD request
        for keyword in self.fd_keywords:
            if keyword in message_lower:
                return "fd"
        
        # Context-based: Default to FD
        return None  # Let the system use default
    
    def _is_style_change_request(self, message: str) -> bool:
        """Check if message is requesting a style/color change"""
        message_lower = message.lower()
        
        # Check for style change keywords
        has_style_keyword = any(keyword in message_lower for keyword in self.style_change_keywords)
        has_color_keyword = any(keyword in message_lower for keyword in self.bnr_keywords + self.fd_keywords)
        
        # If it's asking for a style change but has no data, it's likely referring to previous data
        has_data = self._extract_data_pairs(message) is not None
        
        return has_style_keyword and has_color_keyword and not has_data
    
    def _get_previous_chart_data(self, conversation_history: Optional[List[Dict[str, Any]]]) -> Optional[Tuple[List[str], List[float]]]:
        """Extract chart data from previous conversation"""
        if not conversation_history:
            return None
        
        # Look through history in reverse order for assistant messages with metadata
        for msg in reversed(conversation_history):
            if msg.get('role') == 'assistant' and msg.get('metadata'):
                metadata = msg['metadata']
                if 'x_labels' in metadata and 'y_values' in metadata:
                    return metadata['x_labels'], metadata['y_values']
        
        # Also try to extract from previous user messages
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                data = self._extract_data_pairs(msg['content'])
                if data:
                    return data
        
        return None
    
    def _should_refuse(self, message: str) -> bool:
        """Check if the request should be refused"""
        message_lower = message.lower()
        
        # Check for refusal keywords
        for keyword in self.refusal_keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def _generate_title(self, chart_type: str, x_labels: List[str]) -> str:
        """Generate a chart title"""
        if self._is_time_series(x_labels):
            return f"{chart_type.title()} Chart Over Time"
        else:
            return f"{chart_type.title()} Chart Comparison"
    
    async def analyze(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ChartData:
        """
        Analyze a user's message using rule-based pattern matching.
        
        Args:
            user_message: The user's input message
            conversation_history: Optional list of previous messages
        
        Returns:
            ChartData object with validation and extraction results
        """
        try:
            # Check if this should be refused
            if self._should_refuse(user_message):
                return ChartData(
                    is_valid=False,
                    reason="I can only help you create bar or line charts. Please ask me to make a chart with some data!"
                )
            
            # Check if this is a style change request
            if self._is_style_change_request(user_message):
                # Try to get data from previous conversation
                previous_data = self._get_previous_chart_data(conversation_history)
                if previous_data:
                    x_labels, y_values = previous_data
                    chart_type = self._detect_chart_type(user_message, x_labels)
                    color_scheme = self._detect_color_scheme(user_message, x_labels)
                    
                    return ChartData(
                        is_valid=True,
                        chart_type=chart_type,
                        x_labels=x_labels,
                        y_values=y_values,
                        title=self._generate_title(chart_type, x_labels),
                        x_label="Category" if chart_type == "bar" else "Time",
                        y_label="Value",
                        color_scheme=color_scheme
                    )
                else:
                    return ChartData(
                        is_valid=False,
                        reason="I couldn't find previous chart data to apply the new style to. Please provide the data again."
                    )
            
            # Try to extract data from current message
            data = self._extract_data_pairs(user_message)
            
            if not data:
                # Check if message references previous data
                if conversation_history and any(keyword in user_message.lower() for keyword in ['previous', 'same', 'earlier', 'last', 'that']):
                    previous_data = self._get_previous_chart_data(conversation_history)
                    if previous_data:
                        data = previous_data
                    else:
                        return ChartData(
                            is_valid=False,
                            reason="I couldn't find previous chart data. Please provide the data points."
                        )
                else:
                    return ChartData(
                        is_valid=False,
                        reason="I couldn't find any data to chart. Please provide data in format like: A=10, B=20, C=30"
                    )
            
            x_labels, y_values = data
            
            # Detect chart type and color scheme
            chart_type = self._detect_chart_type(user_message, x_labels)
            color_scheme = self._detect_color_scheme(user_message, x_labels)
            
            # Generate labels and title
            title = self._generate_title(chart_type, x_labels)
            x_label = "Time" if self._is_time_series(x_labels) else "Category"
            y_label = "Value"
            
            return ChartData(
                is_valid=True,
                chart_type=chart_type,
                x_labels=x_labels,
                y_values=y_values,
                title=title,
                x_label=x_label,
                y_label=y_label,
                color_scheme=color_scheme
            )
        
        except Exception as e:
            return ChartData(
                is_valid=False,
                reason=f"I encountered an error processing your request: {str(e)}"
            )


# Global instance
fallback_agent = FallbackChartAgent()
