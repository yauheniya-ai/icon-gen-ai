"""Example: Using AI to search and generate icons."""

import os
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from icon_gen import IconGenerator, IconAssistant, check_ai_available

os.makedirs("output/ai", exist_ok=True)

def main():
    """Demonstrate AI-powered icon search."""
    
    print("=" * 70)
    print("AI-Powered Icon Search Example")
    print("=" * 70)
    
    # Check if AI is available
    if not check_ai_available():
        print("\n✗ AI features not available!")
        print("  Install with: pip install icon-gen[ai]")
        print("  Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    # Initialize assistant
    try:
        assistant = IconAssistant()
        generator = IconGenerator(output_dir="output/ai")
        
        if not assistant.is_available():
            print("\n✗ No AI provider configured!")
            print("  Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
            return
        
        print(f"\n✓ Using AI provider: {assistant.provider.get_provider_name()}")
        print(f"  Model: {assistant.provider.model}")
        print()
        
        # Example 1: Search for payment icons
        print("\n" + "=" * 70)
        print("Example 1: Search for payment icons")
        print("=" * 70)
        
        query = "I need icons for a payment checkout page"
        print(f"\nQuery: {query}\n")
        
        response = assistant.discover_icons(query)
        
        print(f"Explanation: {response.explanation}\n")
        print(f"Found {len(response.suggestions)} suggestions:\n")
        
        for i, suggestion in enumerate(response.suggestions[:3], 1):
            print(f"{i}. {suggestion.icon_name}")
            print(f"   Reason: {suggestion.reason}")
            print(f"   Use case: {suggestion.use_case}")
            print(f"   Confidence: {suggestion.confidence:.0%}\n")
            
            # Generate the icon
            output_name = f"payment_{i}_" + suggestion.icon_name.replace(':', '_').replace('/', '_')
            style = suggestion.style_suggestions or {}
            
            result = generator.generate_icon(
                icon_name=suggestion.icon_name,
                output_name=output_name,
                color=style.get('color', 'white'),
                size=style.get('size', 256),
                bg_color=style.get('bg_color'),
                border_radius=style.get('border_radius', 0)
            )
            
            if result:
                print(f"   ✓ Generated: {result}\n")
        
        # Example 2: Search with context
        print("\n" + "=" * 70)
        print("Example 2: Search with design context")
        print("=" * 70)
        
        query = "dashboard navigation icons"
        context = {
            'project_type': 'SaaS dashboard',
            'design_style': 'modern',
            'color_scheme': 'blue and purple'
        }
        
        print(f"\nQuery: {query}")
        print(f"Context: {context}\n")
        
        response = assistant.discover_icons(query, context=context)
        
        print(f"Explanation: {response.explanation}\n")
        print(f"Suggestions:\n")
        
        for i, suggestion in enumerate(response.suggestions[:3], 1):
            print(f"{i}. {suggestion.icon_name}")
            print(f"   {suggestion.reason}\n")
            
            # Generate with modern styling
            output_name = f"dashboard_{i}_" + suggestion.icon_name.replace(':', '_').replace('/', '_')
            
            result = generator.generate_icon(
                icon_name=suggestion.icon_name,
                output_name=output_name,
                color='white',
                size=256,
                bg_color='#6366f1',  # Modern blue
                border_radius=20
            )
            
            if result:
                print(f"   ✓ Generated: {result}\n")
        
        print("\n" + "=" * 70)
        print("✓ Examples completed! Check the output/ai/ directory")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()