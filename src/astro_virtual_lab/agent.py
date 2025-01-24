"""
Provides the base Agent class and specialized Agents for astronomy.

Agents are designed to encapsulate a particular role or expertise. They each
carry a prompt that instructs the Large Language Model (LLM) how to behave.

Example:
    from astro_virtual_lab.agent import Agent

    spec_expert = Agent(
        title="Spectroscopy Specialist",
        expertise="stellar spectroscopy and chemical abundance analysis",
        goal="examine high-resolution spectra of metal-poor stars",
        role="analyze survey data for accurate alpha-element abundances"
    )
"""


class Agent:
    """A Large Language Model (LLM) agent with a defined role, expertise, and goal."""

    def __init__(self, title: str, expertise: str, goal: str, role: str) -> None:
        """
        Initialize the agent with a descriptive title, an area of expertise,
        a concrete goal, and a short role statement.

        :param title: A short descriptive name (e.g., "Galactic Structure Expert").
        :param expertise: A phrase describing the agent's domain knowledge.
        :param goal: The agent's overall purpose in the project.
        :param role: The agent's function, typically describing what tasks it handles.
        """
        self.title = title
        self.expertise = expertise
        self.goal = goal
        self.role = role

    @property
    def prompt(self) -> str:
        """
        Construct a 'system' style prompt to prime the LLM. This ensures the
        LLM knows its identity, domain knowledge, and function.

        :return: A single string used as the system prompt for the LLM.
        """
        return (
            f"You are a {self.title}. "
            f"Your expertise is in {self.expertise}. "
            f"Your goal is to {self.goal}. "
            f"Your role is to {self.role}."
        )

    @property
    def message(self) -> dict[str, str]:
        """
        Build an OpenAI-compatible system message from the prompt.

        :return: A dict with keys 'role' and 'content' to be used as the first message.
        """
        return {
            "role": "system",
            "content": self.prompt,
        }

    def __hash__(self) -> int:
        """Hash the agent by its title (unique enough for typical usage)."""
        return hash(self.title)

    def __eq__(self, other: object) -> bool:
        """
        Agents are equal if they share the same title.
        """
        if not isinstance(other, Agent):
            return False
        return self.title == other.title

    def __str__(self) -> str:
        """
        String representation returns the agent's title, which is usually sufficient for identification.
        """
        return self.title


class LiteratureSearchAgent(Agent):
    """
    A specialized agent for literature searches (ADS, SIMBAD, etc.).

    This agent can be used for tasks involving searching NASA ADS, browsing abstracts,
    or retrieving details from SIMBAD. The role is to discover relevant published research
    and summarize it for the team.
    """

    def __init__(self) -> None:
        super().__init__(
            title="Literature Search Expert",
            expertise="performing ADS queries, retrieving abstracts, summarizing relevant astrophysical literature",
            goal="retrieve, parse, and summarize relevant research papers from NASA ADS and gather object data from SIMBAD",
            role="enhance the research agenda with the latest published findings and observational details",
        )
