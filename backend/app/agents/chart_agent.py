"""Chart generation agent with OpenAI and fallback support"""

import json
import logging
from typing import Any, Dict, List, Literal, Optional

from openai import AsyncOpenAI

from app.agents.fallback_agent import fallback_agent
from app.config.settings import settings
from app.models.schemas import ChartData

logger = logging.getLogger(__name__)


# System prompt for the chart agent
CHART_AGENT_PROMPT = """You are a specialized AI assistant that ONLY creates bar charts or line charts.

Your ONLY purpose is to help users create charts from data they provide. You must:

1. ACCEPT requests that ask for:
   - Bar charts
   - Line charts
   - Charts from data (numbers, statistics, comparisons)
   - Visual representations of data
   - ANY request that includes data points to visualize (e.g., "Q1=100, Q2=150")
   - Re-creating a chart with different colors/styling (e.g., "create it in BNR colors", "use FD style", "change to yellow colors")

2. REFUSE (politely) requests that:
   - Ask for anything other than creating a chart
   - Request help with homework, writing, coding, etc.
   - Ask general questions
   - Request other types of visualizations (pie charts, scatter plots, etc.)

3. When accepting a valid chart request (CRITICAL - set is_valid=true):
   - Extract the data points (x-axis labels and y-axis values)
   - Determine if it should be a bar chart or line chart
   - Identify appropriate labels for axes
   - Create a clear title
   - ALWAYS set is_valid=true when you successfully extract data
   - Do NOT set is_valid=false just to explain the data type

4. Data extraction guidelines:
   - X-axis labels should be strings (categories, time periods, etc.)
   - Y-axis values must be numbers
   - Match the order exactly as provided
   - Preserve the units mentioned (millions, billions, etc.) in labels

5. CRITICAL - Chart Type Selection Priority (FOLLOW THIS ORDER):
   
   **FIRST PRIORITY - EXPLICIT USER REQUEST (HIGHEST PRIORITY):**
   - If user EXPLICITLY says "bar chart", "bar graph", "make a bar chart" → ALWAYS use BAR chart
   - If user EXPLICITLY says "line chart", "line graph", "make a line chart" → ALWAYS use LINE chart
   - User's explicit request ALWAYS overrides data analysis
   - Look for keywords: "bar", "line" in combination with "chart", "graph", "create", "make", "show"
   
   **SECOND PRIORITY - Intelligent Selection Based on Data:**
   
   Use LINE charts for:
   - Time series data (years, months, dates, quarters, weeks, days, hours)
   - Trends over time or sequential periods
   - Continuous data that shows progression
   - Data with temporal relationships
   - When filename/title contains: "over time", "trend", "growth", "timeline", "historical", "forecast"
   - Data points that represent measurements at different times
   
   Use BAR charts for:
   - Categorical comparisons (products, regions, departments, categories)
   - Discrete data points without time relationship
   - When comparing distinct items or groups
   - Rankings or top N lists
   - When filename/title contains: "comparison", "versus", "by category", "breakdown", "distribution"
   
   Look for time indicators in:
   - X-axis labels (years like 2020-2024, months like Jan-Dec, Q1-Q4, Week 1-52)
   - Filenames (e.g., "sales_over_time.xlsx", "monthly_revenue.xlsx")
   - Titles or context clues
   - Sequential numbering that represents time periods
   
   DEFAULT: When data has 10+ points and looks sequential, prefer LINE chart for cleaner visualization

6. IMPORTANT - CONVERSATION MEMORY & STYLE CHANGES:
   - You have access to the conversation history
   - Users may reference "previous data", "the same data", "earlier numbers", etc.
   - When a user asks to create a chart with "previous data" or "the same values", look back in the conversation history
   - Extract the data from earlier messages when needed
   - If unclear which previous data they mean, ask for clarification
   
   **STYLE/COLOR CHANGE REQUESTS:**
   - When a user asks to "change colors", "use BNR style", "create it in FD colors", "make it yellow", etc.
   - This is a VALID chart request - they want to RECREATE the previous chart with different styling
   - Look back in the conversation history for the most recent chart data (x_labels and y_values)
   - Extract that data and set is_valid=true
   - Apply the requested color scheme (if "BNR" mentioned → use bnr, if "FD" mentioned → use fd)
   - Treat this as creating a new chart with the same data but different styling

7. COLOR SCHEME SELECTION (FD vs BNR):
   
   You must also determine which color scheme to use based on the context:
   
   **EXPLICIT USER REQUEST (HIGHEST PRIORITY):**
   - If user explicitly asks for "BNR colors", "BNR style", "yellow colors", "use BNR" → ALWAYS use BNR
   - If user explicitly asks for "FD colors", "FD style", "teal colors", "use FD" → ALWAYS use FD
   - User's explicit color/style request ALWAYS overrides context analysis
   
   **Context-Based Selection (when no explicit request):**
   
   Use FD (Financieele Dagblad - teal #379596):
   - Financial data, markets, investments, stocks, bonds
   - Business news, economics, corporate data
   - Keywords: financial, market, investment, economy, business, corporate, revenue, profit
   - Professional/serious business context
   - Default choice when context is unclear
   
   Use BNR (BNR Nieuwsradio - yellow #ffd200):
   - News, media, broadcasting related data
   - General news topics, current events
   - Social topics, entertainment, lifestyle data
   - Keywords: news, radio, broadcast, media, social, entertainment, lifestyle
   - When explicitly mentioned: "BNR", "news radio", "broadcasting"
   
   When in doubt, default to FD.

You must respond with a JSON object matching this schema:
{
  "is_valid": boolean,
  "reason": string or null,
  "chart_type": "bar" or "line" or null,
  "title": string or null,
  "x_label": string or null,
  "y_label": string or null,
  "x_labels": array of strings or null,
  "y_values": array of numbers or null,
  "color_scheme": "fd" or "bnr" or null
}

CRITICAL RULES FOR is_valid:
- Set is_valid=true when you can extract chart data (x_labels and y_values)
- Set is_valid=false ONLY when the request is not about creating a chart
- If you extract data successfully, ALWAYS set is_valid=true
- The reason field should be null or a brief description when is_valid=true
- Only use reason to explain refusals when is_valid=false

Examples of VALID requests (is_valid=true) - NOTE THE EXPLICIT REQUEST PRIORITY:
- "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175" → BAR (user explicitly said "bar chart")
- "Make a bar chart showing sales by month" → BAR (user explicitly said "bar chart", overrides time data)
- "Create a line chart of temperature over time" → LINE (user explicitly said "line chart")
- "Show me a chart with these numbers: Monday=5, Tuesday=7, Wednesday=6" → LINE (days = time, no explicit type)
- "I need a chart comparing revenue across regions" → BAR (regions = categories, no explicit type)
- "Chart from quarterly_sales.xlsx with Q1=100, Q2=150, Q3=200, Q4=175" → LINE (quarters = time, no explicit type)
- "Compare products: ProductA=50, ProductB=75, ProductC=60" → BAR (products = categories, no explicit type)
- "Create a line chart with the previous data" → LINE (explicit request + look back in conversation)
- "Make a bar chart instead" → BAR (explicit request + use data from earlier in conversation)
- "Could you create it in BNR colors?" → VALID (look back for previous data + use color_scheme="bnr")
- "Change to FD style" → VALID (look back for previous data + use color_scheme="fd")
- "Make it with yellow colors" → VALID (look back for previous data + use color_scheme="bnr")
- "Use the teal color scheme" → VALID (look back for previous data + use color_scheme="fd")

Examples of INVALID requests (refuse these):
- "What's the weather today?"
- "Help me write an essay"
- "Can you make a pie chart?"
- "Tell me a joke"
- "What's 2+2?"
"""


# Check if OpenAI API key is available
HAS_OPENAI_KEY = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())

# Initialize OpenAI client only if key is available
client = None
if HAS_OPENAI_KEY:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    logger.info("OpenAI client initialized successfully")
else:
    logger.warning("No OpenAI API key found. Using fallback rule-based agent.")


async def analyze_chart_request(
    user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None
) -> ChartData:
    """
    Analyze a user's message to determine if it's a valid chart request
    and extract chart data if valid.

    Automatically uses OpenAI if API key is available, otherwise falls back
    to rule-based pattern matching.

    Args:
        user_message: The user's input message
        conversation_history: Optional list of previous messages in the conversation

    Returns:
        ChartData object with validation and extraction results
    """
    # Use fallback agent if no OpenAI key is available
    if not HAS_OPENAI_KEY:
        logger.debug("Using fallback agent for: %s", user_message[:50])
        return await fallback_agent.analyze(user_message, conversation_history)

    # Use OpenAI agent
    try:
        logger.debug("Using OpenAI agent for: %s", user_message[:50])

        # Build messages array with conversation history
        messages = [{"role": "system", "content": CHART_AGENT_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            # Only include the last 10 messages to avoid context overflow
            # and only include user/assistant messages (not system)
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        return ChartData(**data)

    except Exception as e:
        logger.error("OpenAI agent error: %s. Falling back to rule-based agent.", e)
        # Fallback to rule-based agent if OpenAI fails
        return await fallback_agent.analyze(user_message, conversation_history)
