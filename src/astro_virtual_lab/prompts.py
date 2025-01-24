"""
Defines default Agents and prompt text used in the astro_virtual_lab.
Also contains helper functions for building multi-agent meeting prompts
(including agendas, rules, etc.).
"""

from typing import Iterable

from astro_virtual_lab.agent import Agent

###############################################################################
# Default Agents
###############################################################################
PRINCIPAL_INVESTIGATOR = Agent(
    title="Principal Investigator",
    expertise="galactic archaeology, stellar population analysis",
    goal="advance our understanding of galactic formation and evolution through chemical and dynamical studies",
    role=(
        "lead research into the Milky Way's formation history using stellar populations, "
        "coordinate chemical abundance analysis, and integrate results with galactic evolution models"
    ),
)

GALACTIC_EVOLUTION_EXPERT = Agent(
    title="Galactic Evolution Expert",
    expertise="chemical evolution modeling and galaxy formation theory",
    goal="understand the formation and evolution of galactic components through chemical and dynamical signatures",
    role=(
        "interpret chemical abundance patterns in the context of nucleosynthesis and galaxy formation scenarios, "
        "develop galactic evolution models, and connect observations with theoretical predictions"
    ),
)

STELLAR_EVOLUTION_EXPERT = Agent(
    title="Stellar Evolution Expert",
    expertise="stellar physics and spectroscopic analysis",
    goal="characterize stellar populations and their evolutionary states through spectroscopic and photometric data",
    role=(
        "analyze stellar spectra to derive fundamental parameters and chemical abundances, "
        "interpret stellar populations in the context of evolutionary tracks and isochrones"
    ),
)

MACHINE_LEARNING_EXPERT = Agent(
    title="Machine Learning Expert",
    expertise="astronomical data science and ML applications",
    goal="develop and apply ML techniques to extract insights from large astronomical datasets",
    role=(
        "implement machine learning models for stellar parameter estimation, chemical abundance analysis, "
        "and pattern recognition in astronomical data, with expertise in handling survey systematics "
        "and cross-calibration challenges"
    ),
)

SCIENTIFIC_CRITIC = Agent(
    title="Scientific Critic",
    expertise="critical analysis of galactic archaeology research",
    goal="ensure that chemical abundance analysis and population assignments are rigorous and well-justified",
    role=(
        "evaluate methodologies, identify potential biases in survey data, and ensure "
        "proper handling of systematic uncertainties"
    ),
)

###############################################################################
# Standard “actions” to direct the meeting
###############################################################################
SYNTHESIS_PROMPT = (
    "synthesize the points raised by each team member, make decisions regarding the "
    "astronomical research agenda based on team member input, and ask follow-up questions "
    "to gather more information and feedback"
)

SUMMARY_PROMPT = (
    "summarize the meeting in detail for future discussions, provide specific recommendations "
    "regarding the astronomical research agenda, and answer the agenda questions based on the "
    "discussion while strictly adhering to the agenda rules"
)

MERGE_PROMPT = (
    "Please read the summaries of multiple separate meetings about the same astronomical "
    "research agenda. Based on the summaries, provide a single answer that merges the "
    "best components of each individual answer. Use the same format as the individual "
    "answers and explain what components came from each answer and why they were included."
)

REWRITE_PROMPT = (
    "This script needs to be improved. Please rewrite the script to make the following "
    "improvements without changing anything else."
)


###############################################################################
# Helper functions to format agendas and rules
###############################################################################
def format_prompt_list(prompts: Iterable[str]) -> str:
    """Formats strings as a numbered list."""
    return "\n\n".join(f"{i+1}. {prompt}" for i, prompt in enumerate(prompts))


def format_agenda(
    agenda: str, intro: str = "Here is the agenda for the meeting:"
) -> str:
    """Formats agenda text with an optional introduction line."""
    return f"{intro}\n\n{agenda}\n\n"


def format_agenda_questions(
    agenda_questions: tuple[str, ...],
    intro: str = "Here are the agenda questions that must be answered:",
) -> str:
    if not agenda_questions:
        return ""
    return f"{intro}\n\n{format_prompt_list(agenda_questions)}\n\n"


def format_agenda_rules(
    agenda_rules: tuple[str, ...],
    intro: str = "Here are the agenda rules that must be followed:",
) -> str:
    if not agenda_rules:
        return ""
    return f"{intro}\n\n{format_prompt_list(agenda_rules)}\n\n"


def summary_structure_prompt(has_agenda_questions: bool) -> str:
    """
    Returns instructions on how to structure a final summary.
    If there are agenda questions, include the 'Answers' section.
    """
    base = [
        "### Agenda",
        "Restate the agenda in your own words.",
        "### Team Member Input",
        "Summarize all of the important points raised by each team member. This is to ensure that key details are preserved for future meetings.",
        "### Recommendation",
        (
            "Provide your expert recommendation regarding the agenda. You should consider the input from each team member, "
            "but you must also use your expertise to make a final decision and choose one option among several that "
            "may have been discussed. This decision can conflict with the input of some team members as long as it is well justified. "
            "It is essential that you provide a clear, specific, and actionable recommendation. Please justify your recommendation as well."
        ),
    ]

    if has_agenda_questions:
        base.extend(
            [
                "### Answers",
                "For each agenda question, please provide the following:",
                "Answer: A specific answer to the question based on your recommendation above.",
                "Justification: A brief explanation of why you provided that answer.",
            ]
        )

    base.extend(
        [
            "### Next Steps",
            "Outline the next steps that the team should take based on the discussion.",
        ]
    )
    return "\n\n".join(base)


###############################################################################
# Team and Individual Meeting Prompts
###############################################################################
def team_meeting_start_prompt(
    team_lead: Agent,
    team_members: tuple[Agent, ...],
    agenda: str,
    agenda_questions: tuple[str, ...] = (),
    agenda_rules: tuple[str, ...] = (),
    summaries: tuple[str, ...] = (),
    contexts: tuple[str, ...] = (),
    num_rounds: int = 1,
) -> str:
    """
    Generates the initial user prompt describing a team meeting.

    The meeting lead is `team_lead`. The participants are `team_members`.
    The function aggregates the agenda, agenda_questions, and rules,
    plus any prior meeting summaries or contextual text.
    """

    # Optionally embed prior contexts or summaries
    def format_references(refs: tuple[str, ...], ref_type: str, intro: str) -> str:
        if not refs:
            return ""
        blocks = []
        for idx, ref in enumerate(refs):
            blocks.append(
                f"[begin {ref_type} {idx+1}]\n\n{ref}\n\n[end {ref_type} {idx+1}]"
            )
        return f"{intro}\n\n{'\n\n'.join(blocks)}\n\n"

    context_str = format_references(
        contexts, "context", "Here is context for this meeting:"
    )
    summary_str = format_references(
        summaries, "summary", "Here are summaries of the previous meetings:"
    )

    # Construct the meeting start text
    return (
        f"This is the beginning of a team meeting to discuss your astronomical research project. "
        f"This is a meeting with the team lead, {team_lead.title}, and the following team members: "
        f"{', '.join(member.title for member in team_members)}.\n\n"
        f"{context_str}"
        f"{summary_str}"
        f"{format_agenda(agenda)}"
        f"{format_agenda_questions(agenda_questions)}"
        f"{format_agenda_rules(agenda_rules)}"
        f"{team_lead.title} will convene the meeting. Then, each team member will provide their thoughts on the discussion one-by-one in the order above. "
        f"After all team members have given their input, {team_lead.title} will {SYNTHESIS_PROMPT}. "
        f"This will continue for {num_rounds} rounds. Once the discussion is complete, {team_lead.title} will {SUMMARY_PROMPT}."
    )


def team_meeting_team_lead_initial_prompt(team_lead: Agent) -> str:
    """Prompt for the team lead to provide initial thoughts on the agenda."""
    return (
        f"{team_lead.title}, please provide your initial thoughts on the agenda as well as any questions "
        f"you have to guide the discussion among the team members."
    )


def team_meeting_team_member_prompt(
    team_member: Agent,
    round_num: int,
    num_rounds: int,
) -> str:
    """Prompt for a single team member in a given round of the meeting."""
    return (
        f"{team_member.title}, please provide your thoughts on the discussion (round {round_num} of {num_rounds}). "
        'If you do not have anything new or relevant to add, you may say "pass". '
        "Remember that you can and should (politely) disagree with other team members if you have a different perspective."
    )


def team_meeting_team_lead_intermediate_prompt(
    team_lead: Agent, round_num: int, num_rounds: int
) -> str:
    """Prompt for the team lead to summarize and ask for more info, at the end of each round except the final one."""
    return (
        f"This concludes round {round_num} of {num_rounds} of discussion. "
        f"{team_lead.title}, please {SYNTHESIS_PROMPT}."
    )


def team_meeting_team_lead_final_prompt(
    team_lead: Agent,
    agenda: str,
    agenda_questions: tuple[str, ...] = (),
    agenda_rules: tuple[str, ...] = (),
) -> str:
    """
    Prompt for the team lead to provide the final summary of the meeting,
    strictly following the requested structure (Agenda, Team Member Input, Recommendation, Answers, Next Steps).
    """
    has_agenda_questions = len(agenda_questions) > 0
    structure_instructions = summary_structure_prompt(
        has_agenda_questions=has_agenda_questions
    )

    return (
        f"This concludes round {{}} of {{}} of discussion. "  # We can fill these placeholders or ignore
        f"{team_lead.title}, please {SUMMARY_PROMPT}.\n\n"
        f"{format_agenda(agenda, intro='As a reminder, here is the agenda for the meeting:')}"
        f"{format_agenda_questions(agenda_questions, intro='As a reminder, here are the agenda questions that must be answered:')}"
        f"{format_agenda_rules(agenda_rules, intro='As a reminder, here are the agenda rules that must be followed:')}"
        f"Your summary should take the following form.\n\n"
        f"{structure_instructions}"
    )


def individual_meeting_start_prompt(
    team_member: Agent,
    agenda: str,
    agenda_questions: tuple[str, ...] = (),
    agenda_rules: tuple[str, ...] = (),
    summaries: tuple[str, ...] = (),
    contexts: tuple[str, ...] = (),
) -> str:
    """
    Generates a start prompt for a 1:1 (individual) meeting with a single agent.
    Embeds context, summaries, the agenda, etc.
    """

    def format_references(refs: tuple[str, ...], ref_type: str, intro: str) -> str:
        if not refs:
            return ""
        blocks = []
        for idx, ref in enumerate(refs):
            blocks.append(
                f"[begin {ref_type} {idx+1}]\n\n{ref}\n\n[end {ref_type} {idx+1}]"
            )
        return f"{intro}\n\n{'\n\n'.join(blocks)}\n\n"

    context_str = format_references(
        contexts, "context", "Here is context for this meeting:"
    )
    summary_str = format_references(
        summaries, "summary", "Here are summaries of the previous meetings:"
    )

    return (
        f"This is the beginning of an individual meeting with {team_member.title} to discuss your astronomical research project.\n\n"
        f"{context_str}"
        f"{summary_str}"
        f"{format_agenda(agenda)}"
        f"{format_agenda_questions(agenda_questions)}"
        f"{format_agenda_rules(agenda_rules)}"
        f"{team_member.title}, please provide your response to the agenda."
    )
