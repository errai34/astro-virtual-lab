"""
Holds constants used throughout the astro_virtual_lab package, such as token pricing
details, default temperatures, and tool function descriptions for ADS/SIMBAD searches.
"""

###############################################################################
# Model Cost Info (example placeholders). Your actual costs or usage tracking
# might differ depending on your LLM provider or plan.
###############################################################################

MODEL_TO_INPUT_PRICE_PER_TOKEN = {
    # example cost in USD per 1M tokens
    "gpt-3.5-turbo": 0.5 / 1_000_000,
    "gpt-4o": 5.0 / 1_000_000,
}

MODEL_TO_OUTPUT_PRICE_PER_TOKEN = {
    "gpt-3.5-turbo": 1.5 / 1_000_000,
    "gpt-4o": 15.0 / 1_000_000,
}

###############################################################################
# Temperature Presets
###############################################################################
CONSISTENT_TEMPERATURE = 0.2
CREATIVE_TEMPERATURE = 0.8

###############################################################################
# Tool Descriptions (ADS & SIMBAD)
###############################################################################
ADS_TOOL_NAME = "ads_search"
ADS_TOOL_DESCRIPTION = {
    "type": "function",
    "function": {
        "name": ADS_TOOL_NAME,
        "description": (
            "Search NASA's Astrophysics Data System (ADS) for astronomy research papers. "
            "Returns abstracts and bibliographic information for the most relevant papers. "
            "Use this when you need references or background from peer-reviewed literature."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query to use to search NASA ADS for astronomy papers. "
                        "More specific queries are more likely to return relevant papers."
                    ),
                },
                "num_articles": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "The number of papers to return from the search query.",
                },
            },
            "required": ["query", "num_articles"],
        },
    },
}

SIMBAD_TOOL_NAME = "simbad_search"
SIMBAD_TOOL_DESCRIPTION = {
    "type": "function",
    "function": {
        "name": SIMBAD_TOOL_NAME,
        "description": (
            "Query the SIMBAD astronomical database for information about celestial objects. "
            "Returns detailed information including coordinates, magnitudes, spectral type, and more. "
            "Use this to retrieve details for a known star, galaxy, or object by name."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "object_name": {
                    "type": "string",
                    "description": (
                        "The name of the astronomical object to search for. "
                        "Can be a common name (e.g., 'M31'), catalog identifier, or coordinates."
                    ),
                },
            },
            "required": ["object_name"],
        },
    },
}
