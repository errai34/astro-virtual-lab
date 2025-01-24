"""
Utilities for the astro_virtual_lab, including:
 - NASA ADS queries
 - SIMBAD queries
 - Token counting and cost estimation
 - Saving/loading discussion logs

All code uses appropriate astropy, astroquery, or standard library calls.
Ensure your environment has the optional dependencies installed if you plan
to use ADS or SIMBAD queries (e.g., astroquery).
"""

import json
from pathlib import Path
from typing import Dict, List

import astropy.units as u
import tiktoken
from astropy.coordinates import SkyCoord
from astroquery.nasa_ads import ADS
from astroquery.simbad import Simbad

from astro_virtual_lab.config import load_config
from astro_virtual_lab.constants import (
    MODEL_TO_INPUT_PRICE_PER_TOKEN,
    MODEL_TO_OUTPUT_PRICE_PER_TOKEN,
)


def run_ads_search(query: str, num_articles: int = 3, verbose: bool = True) -> str:
    """
    Runs a NASA ADS search using astroquery.nasa_ads, returning abstracts and
    bibliographic info of the top matching articles.

    :param query: The search query for NASA ADS.
    :param num_articles: The maximum number of articles to retrieve.
    :param verbose: Print search details for debugging or clarity.
    :return: Formatted string containing relevant article details.
    """
    # Load config and set ADS token
    config = load_config()
    ADS.TOKEN = config["api_keys"]["nasa_ads"]
    
    if verbose:
        print(f"[ADS Search] Searching for up to {num_articles} articles with query: '{query}'")

    # Query ADS using astroquery
    try:
        papers = ADS.query_simple(query, max_pages=1, rows=num_articles)
        if not papers:
            return f"No ADS results found for query: {query}"
    except Exception as e:
        return f"ADS search failed: {str(e)}"

    # Build a readable output
    output_lines = []
    for paper in papers:
        # Some fields may be missing or None, so we handle that gracefully
        title = paper.title[0] if paper.title else "No title"
        authors = ", ".join(paper.author) if paper.author else "No authors"
        year = paper.year if paper.year else "Unknown year"
        abstract = paper.abstract if paper.abstract else "No abstract available"
        bibcode = paper.bibcode if paper.bibcode else "No bibcode"
        
        line = (
            f"TITLE: {title}\n"
            f"AUTHORS: {authors}\n"
            f"YEAR: {year}\n"
            f"BIBCODE: {bibcode}\n"
            f"ABSTRACT: {abstract}\n"
            f"{'-'*80}"
        )
        output_lines.append(line)

    return "\n\n".join(output_lines)


def query_simbad(object_name: str, verbose: bool = True) -> dict:
    """
    Query the SIMBAD database for information about an astronomical object.

    :param object_name: The name or identifier of the object.
    :param verbose: Print debug info.
    :return: Dictionary with keys like 'name', 'coordinates', 'spectral_type', etc.
    """
    if verbose:
        print(f"[SIMBAD Query] Looking up object '{object_name}'")

    custom_simbad = Simbad()
    custom_simbad.add_votable_fields(
        "flux(V)", "flux(B)", "flux(R)", "distance", "rv_value", "sp_type", "parallax"
    )
    result_table = custom_simbad.query_object(object_name)
    if result_table is None or len(result_table) == 0:
        return {"error": f"Object '{object_name}' not found in SIMBAD."}

    row = result_table[0]
    coords = SkyCoord(
        ra=row["RA"], dec=row["DEC"], unit=(u.hourangle, u.deg), frame="icrs"
    )

    output = {
        "name": str(row["MAIN_ID"]).strip(),
        "coordinates": {
            "ra_deg": coords.ra.deg,
            "dec_deg": coords.dec.deg,
            "ra_hms": coords.ra.to_string(unit=u.hour, sep=":"),
            "dec_dms": coords.dec.to_string(unit=u.deg, sep=":"),
        },
        "object_type": str(row["OTYPE"]) if row["OTYPE"] else None,
        "spectral_type": str(row["SP_TYPE"]) if row["SP_TYPE"] else None,
        "magnitudes": {
            "V": float(row["FLUX_V"]) if row["FLUX_V"] else None,
            "B": float(row["FLUX_B"]) if row["FLUX_B"] else None,
            "R": float(row["FLUX_R"]) if row["FLUX_R"] else None,
        },
        "distance_pc": (
            float(row["Distance_distance"]) if row["Distance_distance"] else None
        ),
        "radial_velocity_km_s": float(row["RV_VALUE"]) if row["RV_VALUE"] else None,
        "parallax_mas": float(row["PLX_VALUE"]) if row["PLX_VALUE"] else None,
    }
    return output


###############################################################################
# Token Counting and Cost Estimation
###############################################################################


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count how many tokens are in a given text, using a specified encoding.
    This is used for approximate cost calculation.

    :param text: Input text.
    :param encoding_name: Tokenizer name. "cl100k_base" is typical for GPT-3.5.
    :return: Number of tokens in the text.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def compute_token_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Compute the cost of a completion given the model's pricing per 1M tokens.

    :param model: Model identifier (must be in MODEL_TO_INPUT_PRICE_PER_TOKEN and MODEL_TO_OUTPUT_PRICE_PER_TOKEN).
    :param input_tokens: Number of input tokens.
    :param output_tokens: Number of output tokens.
    :return: Dollar cost as a float.
    """
    if (
        model not in MODEL_TO_INPUT_PRICE_PER_TOKEN
        or model not in MODEL_TO_OUTPUT_PRICE_PER_TOKEN
    ):
        raise ValueError(f"Unknown model for cost calculation: {model}")

    in_price = MODEL_TO_INPUT_PRICE_PER_TOKEN[model] * input_tokens
    out_price = MODEL_TO_OUTPUT_PRICE_PER_TOKEN[model] * output_tokens
    return in_price + out_price


###############################################################################
# Discussion Storage/Loading
###############################################################################


def save_meeting(
    save_dir: Path, save_name: str, discussion: List[Dict[str, str]]
) -> None:
    """
    Save the entire discussion to two files: JSON and Markdown.

    :param save_dir: Directory to save the files.
    :param save_name: Base filename for saving.
    :param discussion: List of message dicts with "agent" and "message".
    """
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = save_dir / f"{save_name}.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(discussion, f, indent=4)

    # Save Markdown
    md_path = save_dir / f"{save_name}.md"
    with md_path.open("w", encoding="utf-8") as f:
        for turn in discussion:
            agent = turn["agent"]
            text = turn["message"]
            f.write(f"## {agent}\n\n{text}\n\n")


def get_summary(discussion: List[Dict[str, str]]) -> str:
    """
    Return the very last message in the discussion as the summary.
    This presumes the final turn is the official meeting summary.

    :param discussion: Entire list of messages (agent, message).
    :return: The text of the last message.
    """
    if not discussion:
        return "No summary available."
    return discussion[-1]["message"]
