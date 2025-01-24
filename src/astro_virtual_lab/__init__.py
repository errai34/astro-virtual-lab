"""
Astro Virtual Lab package initialization.

This package allows collaborative astronomical research with multiple LLM-based
agents, each with a specialized role (e.g., spectroscopic analysis, galactic
structure, theory). The package also supports integrated literature searches,
custom meeting flows, and saving conversation logs.

Exposed top-level symbols:
- __version__      : The version of the astro_virtual_lab package
- Agent            : The base agent class
- run_meeting      : Main function to orchestrate a meeting with one or more agents
"""

from astro_virtual_lab.__about__ import __version__
from astro_virtual_lab.agent import Agent
from astro_virtual_lab.run_meeting import run_meeting


__all__ = [
    "__version__",
    "Agent",
    "run_meeting",
]
