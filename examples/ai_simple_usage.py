"""Simple example: AI icon discovery and generation in one script."""

import os
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

os.makedirs("output/ai", exist_ok=True)

def simple_example():
    """Simplest possible AI icon generation."""
    
    from icon_gen import IconGenerator, IconAssistant
    
    # Initialize
    assistant = IconAssistant()
    generator = IconGenerator(output_dir="output/ai")
    
    # Ask AI for icon suggestions
    response = assistant.discover_icons("icons for a settings page")
    
    # Generate the first 3 suggestions
    for suggestion in response.suggestions[:3]:
        print(f"Generating {suggestion.icon_name}...")
        
        generator.generate_icon(
            icon_name=suggestion.icon_name,
            output_name=suggestion.icon_name.replace(':', '_'),
            color='white',
            size=256,
            bg_color='#6366f1',
            border_radius=20
        )
    
    print("\n✓ Done! Check output/ai folder")


def with_context_example():
    """Example with project context."""
    
    from icon_gen import IconGenerator, IconAssistant
    
    assistant = IconAssistant()
    generator = IconGenerator(output_dir="output/ai")
    
    # Search with context about your project
    response = assistant.discover_icons(
        query="navigation icons",
        context={
            'project_type': 'mobile app',
            'design_style': 'minimal'
        }
    )
    
    print(f"\n{response.explanation}\n")
    
    # Generate icons with recommended styling
    for i, suggestion in enumerate(response.suggestions[:4], 1):
        print(f"{i}. {suggestion.icon_name} - {suggestion.reason}")
        
        style = suggestion.style_suggestions or {}
        
        generator.generate_icon(
            icon_name=suggestion.icon_name,
            output_name=f"nav_{i}_" + suggestion.icon_name.replace(':', '_'),
            color=style.get('color', 'white'),
            size=style.get('size', 256),
            bg_color=style.get('bg_color'),
            border_radius=style.get('border_radius', 0)
        )


if __name__ == "__main__":
    print("=" * 70)
    print("Icon-Gen AI Examples")
    print("=" * 70)
    print("\nChoose an example:")
    print("1. Simple search and generate: Three icons for a settings page")
    print("2. With project context: Four navigation icons for a mobile app in minimal style")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    try:
        if choice == "1":
            simple_example()
        elif choice == "2":
            with_context_example()
        else:
            print("Invalid choice. Running simple example...")
            simple_example()
    except ImportError as e:
        print("\n✗ AI features not available!")
        print("  Install with: pip install icon-gen[ai]")
        print("  export OPENAI_API_KEY=... or export ANTHROPIC_API_KEY=...")
    except Exception as e:
        print(f"\n✗ Error: {e}")