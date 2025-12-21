"""Generate AI model icons: Claude, OpenAI, and Gemini."""

from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen.generator import IconGenerator


def main():
    """Generate white SVG icons for major AI models."""
    
    # Initialize generator
    generator = IconGenerator(output_dir="output")
    
    # Define the AI model icons we want
    # Format: {output_filename: iconify_icon_name}
    ai_icons = {
        'claude_logo': 'logos:claude',
        'anthropic': 'simple-icons:anthropic',      # Anthropic/Claude icon
        'openai': 'simple-icons:openai',          # OpenAI icon
        'gemini': 'simple-icons:googlegemini',    # Google Gemini icon
    }
    
    print("=" * 60)
    print("AI Model Icon Generator")
    print("=" * 60)
    print(f"Output directory: {generator.output_dir.absolute()}")
    print(f"Color: white")
    print(f"Format: SVG")
    print()
    
    # Generate all icons
    generated = generator.generate_batch(ai_icons, color="white")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Successfully generated {len(generated)}/{len(ai_icons)} icons:")
    for path in generated:
        print(f"  • {path.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()