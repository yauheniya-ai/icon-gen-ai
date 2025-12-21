"""Command-line interface for icon-gen."""

import click
from .generator import IconGenerator

@click.command()
@click.argument('icon_name')
@click.option('--color', default='white', help='Icon color')
@click.option('--size', default=256, help='Icon size in pixels')
@click.option('--format', 'output_format', default='png', 
              type=click.Choice(['png', 'svg', 'webp']))
@click.option('--output', '-o', help='Output file path')
def main(icon_name, color, size, output_format, output):
    """Generate icons from Iconify."""
    generator = IconGenerator()
    # Implementation here
    click.echo(f"Generating {icon_name} in {color}...")

if __name__ == '__main__':
    main()