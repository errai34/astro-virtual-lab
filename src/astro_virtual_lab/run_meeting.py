"""
Provides the main function `run_meeting` to orchestrate a meeting with one or more LLM agents.

Usage Example:

    from astro_virtual_lab.run_meeting import run_meeting
    from astro_virtual_lab.prompts import PRINCIPAL_INVESTIGATOR, MACHINE_LEARNING_EXPERT
    from pathlib import Path

    summary = run_meeting(
        meeting_type="team",
        agenda="We want to explore the chemical abundance trends in thick disk stars.",
        save_dir=Path("meeting_outputs"),
        save_name="thick_disk_exploration",
        team_lead=PRINCIPAL_INVESTIGATOR,
        team_members=(MACHINE_LEARNING_EXPERT,),
        agenda_questions=("What do we know about alpha-element trends?",),
        agenda_rules=("All analyses must account for cross-survey calibration",),
        num_rounds=1,
        use_astronomy_tools=True,
        return_summary=True,
        model="deepseek-chat"
    )

    print("Meeting Summary:")
    print(summary)
"""

import json
from pathlib import Path
from typing import Dict, List, Literal, Optional

############################
# External LLM client
############################
from astro_virtual_lab.clients import init_openai_client
from astro_virtual_lab.utils import run_ads_search

############################
# Internal references
############################
from astro_virtual_lab.agent import Agent
from astro_virtual_lab.constants import CONSISTENT_TEMPERATURE
from astro_virtual_lab.prompts import (
    individual_meeting_start_prompt,
    team_meeting_start_prompt,
    team_meeting_team_lead_final_prompt,
    team_meeting_team_lead_intermediate_prompt,
    team_meeting_team_member_prompt,
)
from astro_virtual_lab.utils import (
    get_summary,
    save_meeting,
)

###############################################################################
# run_meeting
###############################################################################


def run_meeting(
    meeting_type: Literal["team", "individual"],
    agenda: str,
    save_dir: Path,
    save_name: str = "discussion",
    team_lead: Optional[Agent] = None,
    team_members: Optional[tuple[Agent, ...]] = None,
    team_member: Optional[Agent] = None,
    agenda_questions: tuple[str, ...] = (),
    agenda_rules: tuple[str, ...] = (),
    summaries: tuple[str, ...] = (),
    contexts: tuple[str, ...] = (),
    num_rounds: int = 2,
    temperature: float = CONSISTENT_TEMPERATURE,
    use_astronomy_tools: bool = True,
    return_summary: bool = False,
    model: str = "gpt-3.5-turbo",
) -> Optional[str]:
    """
    Orchestrates a meeting with one or more LLM agents, either a "team" (with
    a principal investigator and multiple specialized experts) or an "individual"
    (one agent plus an internal critic).

    :param meeting_type: "team" or "individual".
    :param agenda: Main text describing the project's scientific goals.
    :param save_dir: Directory where conversation logs will be saved (JSON + MD).
    :param save_name: Filename (without extension) for the conversation logs.
    :param team_lead: Required if meeting_type == "team".
    :param team_members: Additional agents, required if meeting_type == "team".
    :param team_member: Single agent, required if meeting_type == "individual".
    :param agenda_questions: Specific questions that must be answered by the end.
    :param agenda_rules: Key constraints or rules for the research.
    :param summaries: Summaries of previous related meetings to provide context.
    :param contexts: Additional contextual paragraphs or references.
    :param num_rounds: Number of “rounds” of back-and-forth in the meeting (for a team).
    :param temperature: The LLM "temperature".
    :param use_astronomy_tools: If True, allow the usage of ADS and SIMBAD in the conversation.
    :param return_summary: If True, returns the final text summary (last message).
    :param model: The OpenAI model name to use (e.g. "gpt-3.5-turbo", "gpt-4", "deepseek-chat").
    :return: The final summary of the meeting, if `return_summary` is True. Otherwise None.
    """
    # Basic checks
    if meeting_type == "team":
        if not team_lead or not team_members:
            raise ValueError(
                "For a 'team' meeting, you must specify a team_lead and team_members."
            )
        if team_member:
            raise ValueError(
                "For a 'team' meeting, do not provide an individual team_member."
            )
        if team_lead in team_members:
            raise ValueError("team_lead must not appear in team_members.")
    elif meeting_type == "individual":
        if not team_member:
            raise ValueError(
                "For an 'individual' meeting, you must specify a single team_member."
            )
        if team_lead or team_members:
            raise ValueError(
                "For an 'individual' meeting, do not provide team_lead or team_members."
            )
    else:
        raise ValueError(
            f"Invalid meeting_type: {meeting_type}. Must be 'team' or 'individual'."
        )

    # Create the output directory if needed
    save_dir.mkdir(parents=True, exist_ok=True)

    # Prepare an in-memory discussion list
    # Format: [{"agent": "User" or agent.title, "message": "Text..."}]
    discussion: List[Dict[str, str]] = []

    # Function to add a turn to the discussion
    def add_turn(agent_label: str, message: str):
        discussion.append({"agent": agent_label, "message": message.strip()})

    ######################
    # Initialize the conversation with the meeting start prompt
    ######################

    if meeting_type == "team":
        # Build the system message for the team lead
        system_prompt_lead = team_lead.prompt

        # Build the user message describing the entire scenario
        user_prompt = team_meeting_start_prompt(
            team_lead=team_lead,
            team_members=team_members,
            agenda=agenda,
            agenda_questions=agenda_questions,
            agenda_rules=agenda_rules,
            summaries=summaries,
            contexts=contexts,
            num_rounds=num_rounds,
        )

        add_turn("User", user_prompt)

        # Let the team lead respond
        lead_response = _get_llm_response(
            system_prompt=system_prompt_lead,
            conversation=discussion,
            temperature=temperature,
            model=model,
            use_astronomy_tools=use_astronomy_tools,
        )
        add_turn(team_lead.title, lead_response)

        # Then begin the round-based discussion
        for r in range(num_rounds):
            round_num = r + 1
            # Each team member responds
            for member in team_members:
                prompt = team_meeting_team_member_prompt(member, round_num, num_rounds)
                add_turn("User", prompt)
                member_response = _get_llm_response(
                    system_prompt=member.prompt,
                    conversation=discussion,
                    temperature=temperature,
                    model=model,
                    use_astronomy_tools=use_astronomy_tools,
                )
                add_turn(member.title, member_response)

            # Team lead synthesizes after each round
            if r < num_rounds - 1:
                # Intermediate synthesis
                pi_prompt = team_meeting_team_lead_intermediate_prompt(
                    team_lead, round_num, num_rounds
                )
            else:
                # Final
                pi_prompt = team_meeting_team_lead_final_prompt(
                    team_lead=team_lead,
                    agenda=agenda,
                    agenda_questions=agenda_questions,
                    agenda_rules=agenda_rules,
                ).format(round_num, num_rounds)

            add_turn("User", pi_prompt)
            lead_synthesis = _get_llm_response(
                system_prompt=system_prompt_lead,
                conversation=discussion,
                temperature=temperature,
                model=model,
                use_astronomy_tools=use_astronomy_tools,
            )
            add_turn(team_lead.title, lead_synthesis)

    else:
        # individual meeting
        # System message for the single agent
        system_prompt_ind = team_member.prompt

        # The user prompt
        user_prompt = individual_meeting_start_prompt(
            team_member=team_member,
            agenda=agenda,
            agenda_questions=agenda_questions,
            agenda_rules=agenda_rules,
            summaries=summaries,
            contexts=contexts,
        )
        add_turn("User", user_prompt)

        # The agent responds
        agent_response = _get_llm_response(
            system_prompt=system_prompt_ind,
            conversation=discussion,
            temperature=temperature,
            model=model,
            use_astronomy_tools=use_astronomy_tools,
        )
        add_turn(team_member.title, agent_response)

        # Then we might let a "Scientific Critic" chime in for X rounds, or
        # keep it simple. For brevity, we won't do multiple rounds here unless
        # you specifically want that logic. You can adapt similarly to the
        # team approach if desired.

    # Save the entire discussion
    save_meeting(save_dir=save_dir, save_name=save_name, discussion=discussion)

    # Return summary if requested
    if return_summary:
        return get_summary(discussion)
    return None


###############################################################################
# Internal function to get a response from the LLM
###############################################################################


def _get_llm_response(
    system_prompt: str,
    conversation: List[Dict[str, str]],
    temperature: float,
    model: str,
    use_astronomy_tools: bool,
) -> str:
    """
    Queries the OpenAI ChatCompletion API with the given system prompt + conversation.

    If use_astronomy_tools is True, the function can handle ADS or SIMBAD tool calls
    by intercepting function calls from the model. Otherwise, it runs purely in text mode.

    Args:
        system_prompt: The system prompt for the agent.
        conversation: The discussion so far (list of dicts with 'agent','message').
        temperature: The sampling temperature.
        model: The OpenAI model name to use.
        use_astronomy_tools: If True, handle ADS and SIMBAD tool usage.

    Returns:
        str: LLM's answer as text.
    """
    # Initialize client based on model type
    client = init_openai_client("deepseek" if model.startswith("deepseek-") else "openai")
    
    messages = [{"role": "system", "content": system_prompt}]

    # For DeepSeek Reasoner, we need to ensure messages alternate between user/assistant
    if model == "deepseek-reasoner":
        # Combine consecutive messages from the same role
        combined_messages = []
        current_role = None
        current_content = []
        
        for msg in conversation:
            role = "assistant" if msg["agent"] == "Assistant" else "user"
            if role == current_role:
                current_content.append(msg["message"])
            else:
                if current_role is not None:
                    combined_messages.append({
                        "role": current_role,
                        "content": "\n".join(current_content)
                    })
                current_role = role
                current_content = [msg["message"]]
        
        if current_content:
            combined_messages.append({
                "role": current_role,
                "content": "\n".join(current_content)
            })
        
        messages.extend(combined_messages)
    else:
        # For other models, just add messages as is
        for msg in conversation:
            messages.append({
                "role": "assistant" if msg["agent"] == "Assistant" else "user",
                "content": msg["message"]
            })

    # Some models like deepseek-reasoner don't support function calling
    supports_functions = not model == "deepseek-reasoner"
    
    # Only add functions if the model supports them and astronomy tools are enabled
    if use_astronomy_tools and supports_functions:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            functions=get_astronomy_tool_functions(),
            function_call="auto",
        )
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

    return response.choices[0].message.content


###############################################################################
# Internal function to get the astronomy tool functions
###############################################################################


def get_astronomy_tool_functions() -> List[Dict]:
    """Get the function definitions for astronomy tools."""
    return [
        {
            "name": "run_ads_search",
            "description": "Search NASA ADS for papers matching a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_articles": {
                        "type": "integer",
                        "description": "Maximum number of papers to return",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    ]
