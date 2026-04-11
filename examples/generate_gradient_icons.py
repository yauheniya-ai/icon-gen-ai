"""Generate icons showcasing all four gradient directions.

Produces 8 icons:
  - 4 icons with gradient-coloured icon shapes (white background), one per direction
  - 4 icons with gradient backgrounds (white icon), one per direction

Gradient directions: horizontal, vertical, diagonal, radial
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from icon_gen_ai.generator import IconGenerator


def main():
    generator = IconGenerator(
        output_dir=Path(__file__).parent.parent / "output" / "gradient_test"
    )

    size = 256
    border_radius = 48
    gradient = ('deeppink', 'deepskyblue')
    directions = ['horizontal', 'vertical', 'diagonal', 'radial']
    icons = ['ph:star-bold', 'ph:heart-bold', 'ph:lightning-bold', 'ph:fire-bold']

    # ------------------------------------------------------------------ #
    # 1. Gradient ICON colour on a plain dark background                  #
    # ------------------------------------------------------------------ #
    print("=== Gradient icon colour ===")
    icon_grad_icons = {
        f'grad_icon_{direction}': {
            'icon': icons[i],
            'color': gradient,
            'direction': direction,
            'bg_color': '#1a1a2e',
            'border_radius': border_radius,
        }
        for i, direction in enumerate(directions)
    }

    generated = generator.generate_batch(icon_grad_icons, size=size)

    for path in generated:
        print(f"  ✓ {path.resolve()}")
    if len(generated) < len(icon_grad_icons):
        print(f"  ✗ {len(icon_grad_icons) - len(generated)} icon(s) failed")

    # ------------------------------------------------------------------ #
    # 2. Gradient BACKGROUND with a white icon                            #
    # ------------------------------------------------------------------ #
    print("\n=== Gradient background ===")
    bg_grad_icons = {
        f'grad_bg_{direction}': {
            'icon': icons[i],
            'color': 'white',
            'bg_color': gradient,
            'bg_direction': direction,
            'border_radius': border_radius,
        }
        for i, direction in enumerate(directions)
    }

    generated = generator.generate_batch(bg_grad_icons, size=size)

    for path in generated:
        print(f"  ✓ {path.resolve()}")
    if len(generated) < len(bg_grad_icons):
        print(f"  ✗ {len(bg_grad_icons) - len(generated)} icon(s) failed")


if __name__ == "__main__":
    main()
