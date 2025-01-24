"""Client initialization for various APIs used in astro_virtual_lab."""

from openai import OpenAI
from astro_virtual_lab.config import load_config

def init_openai_client(model_type: str = "openai") -> OpenAI:
    """Initialize OpenAI client with appropriate configuration.
    
    Args:
        model_type: Either 'openai' or 'deepseek' to determine which API to use
        
    Returns:
        OpenAI: Configured OpenAI client
    """
    config = load_config()
    
    if model_type == "openai":
        return OpenAI(api_key=config["api_keys"]["openai"])
    elif model_type == "deepseek":
        return OpenAI(
            api_key=config["api_keys"]["deepseek"],
            base_url="https://api.deepseek.com"
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
