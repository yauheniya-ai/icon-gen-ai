"""Generate icons with transparent (cutout) icon color.

When color='transparent' is combined with a background, the icon shape punches
a hole through the background — the canvas behind the image is visible through
the icon silhouette while the surrounding area keeps its fill.

Use cases:
  - Icon on a solid/gradient background where the icon itself is a negative shape
  - Sticker-style icons where the background colour is the design element
  - Rounded-badge layouts with a cut-out logo
"""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from icon_gen_ai.generator import IconGenerator


def main():
    generator = IconGenerator(output_dir=Path(__file__).parent.parent / "output" / "transparency_test")

    size = 256
    border_radius = 48
    category = 'cutout'

    # ------------------------------------------------------------------ #
    # 1. Solid background with cutout icon                                 #
    # ------------------------------------------------------------------ #
    solid_bg_icons = {
        f'{category}_solid_sun':    'ph:sun-bold',
        f'{category}_solid_star':   'ph:star-bold',
        f'{category}_solid_heart':  'ph:heart-bold',
        f'{category}_solid_bolt':   'ph:lightning-bold',
    }

    generated = generator.generate_batch(
        solid_bg_icons,
        color='transparent',        # icon shape cut out of the background
        size=size,
        bg_color='mediumslateblue',
        border_radius=border_radius,
    )

    print(f"[solid bg] Generated {len(generated)}/{len(solid_bg_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.resolve()}")

    # ------------------------------------------------------------------ #
    # 2. Gradient background with cutout icon                             #
    # ------------------------------------------------------------------ #
    grad_bg_icons = {
        f'{category}_grad_fire':    'ph:fire-bold',
        f'{category}_grad_cloud':   'ph:cloud-bold',
        f'{category}_grad_leaf':    'ph:leaf-bold',
        f'{category}_grad_diamond': 'ph:diamond-bold',
    }

    generated = generator.generate_batch(
        grad_bg_icons,
        color='transparent',
        size=size,
        bg_color=('deeppink', 'deepskyblue'),   # gradient background
        bg_direction='diagonal',
        border_radius=border_radius,
    )

    print(f"\n[gradient bg] Generated {len(generated)}/{len(grad_bg_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.resolve()}")

    # ------------------------------------------------------------------ #
    # 3. Cutout + outline: background colour bleeds through icon shape     #
    #    while an outline frames the badge                                 #
    # ------------------------------------------------------------------ #
    outlined_icons = {
        f'{category}_outline_shield': 'ph:shield-bold',
        f'{category}_outline_bell':   'ph:bell-bold',
    }

    generated = generator.generate_batch(
        outlined_icons,
        color='transparent',
        size=size,
        bg_color='darkorange',
        border_radius=size // 2,    # full circle badge
        outline_width=8,
        outline_color='white',
    )

    print(f"\n[circular cutout + outline] Generated {len(generated)}/{len(outlined_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.resolve()}")

    # ------------------------------------------------------------------ #
    # 4. Single icon — direct call to show the API clearly                #
    # ------------------------------------------------------------------ #
    result = generator.generate_icon(
        icon_name='ph:cube-bold',
        output_name=f'{category}_single_cube',
        color='transparent',
        bg_color=('mediumslateblue', 'deeppink'),
        bg_direction='horizontal',
        size=size,
        border_radius=border_radius,
        format='png',
    )

    if result:
        print(f"\n[single PNG] ✓ {result.resolve()}")
    else:
        print("\n[single PNG] ✗ failed")


if __name__ == "__main__":
    main()
