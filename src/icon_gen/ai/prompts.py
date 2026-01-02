"""System prompts for icon discovery and suggestions."""

ICON_DISCOVERY_SYSTEM_PROMPT = """You are an expert icon designer and UI/UX consultant helping users find the perfect icons from Iconify.

Iconify has 200,000+ icons from various collections including:
- simple-icons: Company and brand logos (e.g., simple-icons:openai, simple-icons:google)
- mdi (Material Design Icons): General purpose icons (e.g., mdi:home, mdi:account)
- fa6-solid (Font Awesome 6): Popular icon set (e.g., fa6-solid:user, fa6-solid:heart)
- heroicons: Modern minimal icons (e.g., heroicons:home, heroicons:user)
- lucide: Clean and consistent icons (e.g., lucide:home, lucide:settings)
- tabler: Outline style icons (e.g., tabler:home, tabler:user)

Your task is to:
1. Understand what the user needs icons for
2. Suggest 3-5 relevant icons with their exact Iconify names
3. Explain why each icon is appropriate
4. Suggest styling (color, size, background) if relevant

IMPORTANT: Always use the format "collection:icon-name" (e.g., "mdi:github" not just "github")

Respond in this JSON format:
{
  "search_query": "interpreted user need",
  "explanation": "brief explanation of your recommendations",
  "suggestions": [
    {
      "icon_name": "collection:icon-name",
      "reason": "why this icon fits",
      "use_case": "when to use this icon",
      "confidence": 0.95,
      "style_suggestions": {
        "color": "white",
        "size": 256,
        "bg_color": "#8B76E9",
        "border_radius": 0
      }
    }
  ]
}

Be concise but helpful. Focus on the most relevant and popular icons."""

ICON_CONTEXT_PROMPT = """Given this context about the user's project:

Project type: {project_type}
Design style: {design_style}
Color scheme: {color_scheme}
Platform: {platform}

Suggest appropriate icons and styling that match this context."""

USE_CASE_EXAMPLES = {
    "dashboard": "For a dashboard, consider: mdi:view-dashboard, mdi:chart-line, mdi:table, heroicons:chart-bar, lucide:layout-dashboard",
    "authentication": "For auth pages: mdi:login, mdi:logout, mdi:account, fa6-solid:user, heroicons:lock-closed",
    "e-commerce": "For shopping: mdi:cart, mdi:credit-card, fa6-solid:shopping-bag, lucide:shopping-cart, mdi:package",
    "social": "For social features: mdi:thumb-up, mdi:comment, mdi:share, fa6-solid:heart, heroicons:chat-bubble-left",
    "file-management": "For files: mdi:file, mdi:folder, mdi:download, mdi:upload, lucide:file-text",
    "communication": "For messaging: mdi:email, mdi:phone, mdi:message, heroicons:envelope, fa6-solid:comment",
    "settings": "For settings: mdi:cog, mdi:tune, heroicons:cog-6-tooth, lucide:settings, fa6-solid:gear",
    "media": "For media: mdi:play, mdi:pause, mdi:music, fa6-solid:image, heroicons:photo",
}

STYLE_RECOMMENDATIONS = {
    "modern": {
        "collections": ["heroicons", "lucide", "tabler"],
        "colors": ["#6366f1", "#8b5cf6", "#ec4899"],
        "border_radius": 20
    },
    "corporate": {
        "collections": ["mdi", "fa6-solid"],
        "colors": ["#1e40af", "#047857", "#dc2626"],
        "border_radius": 8
    },
    "minimal": {
        "collections": ["heroicons", "lucide"],
        "colors": ["#000000", "#ffffff", "#6b7280"],
        "border_radius": 0
    },
    "playful": {
        "collections": ["mdi", "fa6-solid"],
        "colors": ["#f59e0b", "#10b981", "#3b82f6"],
        "border_radius": 128  # Circular
    }
}

def get_enhanced_prompt(user_query: str, context: dict = None) -> str:
    """Generate an enhanced prompt with context.
    
    Args:
        user_query: The user's icon request
        context: Optional context dict with keys like project_type, design_style, etc.
        
    Returns:
        Enhanced prompt string
    """
    base_prompt = f"User request: {user_query}\n\n"
    
    if context:
        base_prompt += "Context:\n"
        for key, value in context.items():
            if value:
                base_prompt += f"- {key}: {value}\n"
        base_prompt += "\n"
    
    # Add relevant examples
    for use_case, examples in USE_CASE_EXAMPLES.items():
        if use_case.lower() in user_query.lower():
            base_prompt += f"Relevant examples for {use_case}: {examples}\n\n"
    
    return base_prompt

def get_style_recommendations(style: str) -> dict:
    """Get style recommendations for a given design style.
    
    Args:
        style: Design style (e.g., 'modern', 'corporate', 'minimal', 'playful')
        
    Returns:
        Dictionary with style recommendations
    """
    return STYLE_RECOMMENDATIONS.get(style.lower(), STYLE_RECOMMENDATIONS['modern'])