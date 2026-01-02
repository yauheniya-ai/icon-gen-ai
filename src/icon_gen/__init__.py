"""icon-gen: Generate customizable icons from Iconify."""

__version__ = "0.1.0"

from .generator import IconGenerator

__all__ = ["IconGenerator"]

# AI features - optional, only available if ai extras are installed
try:
    from .ai import (
        IconAssistant,
        is_ai_available,
        get_available_providers
    )
    __all__.extend([
        "IconAssistant",
        "is_ai_available", 
        "get_available_providers"
    ])
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


def check_ai_available():
    """Check if AI features are available.
    
    Returns:
        True if AI features can be used, False otherwise
    """
    if not AI_AVAILABLE:
        return False
    return is_ai_available()