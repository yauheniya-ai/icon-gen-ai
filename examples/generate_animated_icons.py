"""Generate AI model icons: Claude, OpenAI, Gemini, and DeepSeek."""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen.generator import IconGenerator


def main():
    """Generate animated SVG icons"""
    # Initialize generator
    generator = IconGenerator(output_dir="output")

    # Configuration
    color = 'mediumslateblue' 
    size = 256

    # Define the AI model icons we want
    animated_icons = {
        f'speedometer_loop_{color}': 'line-md:speedometer-loop',
        f'upload_outline_loop_{color}': 'line-md:upload-outline-loop',
        f'my_location_loop_{color}': 'line-md:my-location-loop',
        f'bars_scale_middle_{color}': 'svg-spinners:bars-scale-middle'
    }
    
    print("=" * 60)
    print("Animated SVG Icon Generator")
    print("=" * 60)
    print(f"Output directory: {generator.output_dir.absolute()}")
    print(f"Color: {color}")
    print(f"Size: {size}px")
    print(f"Format: SVG")
    print()
    
    # Generate all icons with specified color and size
    generated = generator.generate_batch(
        animated_icons, 
        color=color, 
        size=size, 
        outline_color='springgreen', 
        bg_color='snow', 
        outline_width=8, 
        border_radius=48)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Successfully generated {len(generated)}/{len(animated_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.name}")
    
    if len(generated) < len(animated_icons):
        print(f"\n⚠ Failed to generate {len(animated_icons) - len(generated)} icon(s)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()