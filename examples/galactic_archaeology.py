"""Example of using the Astro Virtual Lab for galactic archaeology research."""

from pathlib import Path

from astro_virtual_lab.config import load_config
from astro_virtual_lab.prompts import (
    GALACTIC_EVOLUTION_EXPERT,
    MACHINE_LEARNING_EXPERT,
    PRINCIPAL_INVESTIGATOR,
    STELLAR_EVOLUTION_EXPERT,
)
from astro_virtual_lab.run_meeting import run_meeting

# Load configuration
config = load_config()

# Ensure DeepSeek API key is configured
if not config.get("api_keys", {}).get("deepseek"):
    raise ValueError("Please configure your DeepSeek API key in config.yml")

# Define the research agenda
agenda = """
We want to study the chemical evolution and formation history of the Galactic thick disk.
 Specifically, we aim to:
1. Analyze the alpha-element abundances and metallicity distribution of thick disk stars
2. Investigate the age-metallicity relation in different regions of the thick disk
3. Compare chemical patterns with theoretical galactic evolution models
4. Identify potential ex-situ populations based on chemical and kinematic signatures

Focus on stars with [Fe/H] < 0.0 and use data from major surveys like APOGEE, GALAH,
and Gaia-ESO, along with Gaia astrometry for kinematics.
"""

# Define specific questions to answer
agenda_questions = (
    "What are the distinct chemical abundance patterns we observe in the thick disk population?",
    "How do the alpha-element abundances vary with metallicity and galactic location?",
    "Can we identify any chemically distinct populations that might indicate past accretion events?",
    "What does the age-metallicity relation tell us about the thick disk formation timeline?",
)

# Define rules for the research
agenda_rules = (
    "All abundance analysis must account for systematic uncertainties between different surveys",
    "Kinematic classifications must use full 6D phase space when available",
    "Population assignments should consider both chemical and kinematic information",
    "Age determinations must explicitly state their assumptions and limitations",
)

# Set up the save directory
save_dir = Path("meeting_outputs")

# Run a team meeting with all experts
summary = run_meeting(
    meeting_type="team",
    agenda=agenda,
    save_dir=save_dir,
    team_lead=PRINCIPAL_INVESTIGATOR,
    team_members=(
        GALACTIC_EVOLUTION_EXPERT,
        STELLAR_EVOLUTION_EXPERT,
        MACHINE_LEARNING_EXPERT,
    ),
    agenda_questions=agenda_questions,
    agenda_rules=agenda_rules,
    num_rounds=3,  # More rounds for complex chemical evolution discussion
    use_astronomy_tools=True,  # Enable ADS and SIMBAD searches
    return_summary=True,
    model="deepseek-reasoner",  # Use DeepSeek's reasoner model
)

print("\nGalactic Archaeology Meeting Summary:")
print("-" * 80)
print(summary)

# You can then run individual meetings with specific experts for detailed analysis:
# For example, with the ML Expert for data analysis:
ml_agenda = """
We need to develop a machine learning approach to:
1. Cross-calibrate abundance measurements from different surveys
2. Identify chemically distinct populations in a high-dimensional abundance space
3. Use deep learning to estimate stellar parameters and abundances from spectra
"""

data_meeting = run_meeting(
    meeting_type="individual",
    agenda=ml_agenda,
    save_dir=save_dir,
    save_name="ml_analysis",
    team_member=MACHINE_LEARNING_EXPERT,
    use_astronomy_tools=True,
    return_summary=True,
    model="deepseek-reasoner",  # Use DeepSeek's reasoner model
)

print("\nML Analysis Meeting Summary:")
print("-" * 80)
print(data_meeting)
