"""Command-line interface for icon-gen."""

import click
from pathlib import Path
from .generator import IconGenerator


@click.group()
def cli():
    """Icon-gen-ai: AI-powered icon generator from Iconify.
    
    Use 'icon-gen-ai generate' for basic icon generation.
    Use 'icon-gen-ai search' for AI-powered icon discovery.
    """
    pass


@cli.command()
@click.argument('icon_name')
@click.option('--color', default='white', help='Icon color (e.g., white, #FF0000)')
@click.option('--size', default=256, help='Icon size in pixels')
@click.option('--format', 'output_format', default='svg', 
              type=click.Choice(['png', 'svg', 'webp']))
@click.option('--output', '-o', help='Output file path')
@click.option('--bg-color', help='Background color (e.g., #8B76E9 or none for transparent)')
@click.option('--border-radius', default=0, help='Border radius (0=square, size/2=circle)')
def generate(icon_name, color, size, output_format, output, bg_color, border_radius):
    """Generate icons from Iconify.
    
    Examples:
    
        icon-gen-ai generate simple-icons:googlegemini
        
        icon-gen-ai generate simple-icons:openai --color white --size 512
        
        icon-gen-ai generate mdi:github --bg-color "#8B76E9" --border-radius 20
        
        icon-gen-ai generate simple-icons:openai -o my-icon.svg
    """
    try:
        # Initialize generator
        output_dir = "output" if not output else str(Path(output).parent)
        generator = IconGenerator(output_dir=output_dir)
        
        # Parse background color
        parsed_bg_color = None
        if bg_color and bg_color.lower() != 'none':
            parsed_bg_color = bg_color
        
        # Determine output name
        if output:
            output_name = Path(output).stem
        else:
            output_name = icon_name.replace(':', '_').replace('/', '_')
        
        click.echo(f"Generating {icon_name}...")
        click.echo(f"  Color: {color}")
        click.echo(f"  Size: {size}px")
        click.echo(f"  Background: {bg_color or 'transparent'}")
        click.echo(f"  Border radius: {border_radius}px")
        
        # Generate icon
        result = generator.generate_icon(
            icon_name=icon_name,
            output_name=output_name,
            color=color,
            size=size,
            format=output_format,
            bg_color=parsed_bg_color,
            border_radius=border_radius
        )
        
        if result:
            click.echo(f"✓ Success! Saved to: {result}")
        else:
            click.echo("✗ Failed to generate icon", err=True)
            raise click.Abort()
            
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('query')
@click.option('--count', '-n', default=5, help='Number of suggestions to show')
@click.option('--generate', '-g', is_flag=True, help='Auto-generate suggested icons')
@click.option('--style', help='Design style (modern, corporate, minimal, playful)')
@click.option('--project-type', help='Project type (dashboard, e-commerce, social, etc.)')
def search(query, count, generate, style, project_type):
    """Search for icons using AI-powered natural language queries.
    
    Examples:
    
        icon-gen-ai search "payment icons for checkout"
        
        icon-gen-ai search "dashboard navigation" --style modern
        
        icon-gen-ai search "social media icons" --generate
        
        icon-gen-ai search "file management" --project-type "document editor"
    
    Requires: pip install icon-gen-ai[ai] and OPENAI_API_KEY or ANTHROPIC_API_KEY
    """
    try:
        from .ai import IconAssistant
    except ImportError:
        click.echo("✗ AI features not available. Install with: pip install icon-gen-ai[ai]", err=True)
        click.echo("  Then set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable", err=True)
        raise click.Abort()
    
    try:
        # Initialize assistant
        assistant = IconAssistant()
        
        if not assistant.is_available():
            click.echo("✗ No AI provider configured.", err=True)
            click.echo("  Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable", err=True)
            raise click.Abort()
        
        # Build context
        context = {}
        if style:
            context['design_style'] = style
        if project_type:
            context['project_type'] = project_type
        
        # Search for icons
        click.echo(f"\n🔍 Searching for: {query}")
        if context:
            click.echo(f"   Context: {context}")
        click.echo()
        
        response = assistant.discover_icons(query, context=context)
        
        # Display results
        click.echo(f"\n📋 {response.explanation}\n")
        click.echo(f"Found {len(response.suggestions)} suggestions:\n")
        
        for i, suggestion in enumerate(response.suggestions[:count], 1):
            click.echo(f"{i}. {suggestion.icon_name}")
            click.echo(f"   Reason: {suggestion.reason}")
            click.echo(f"   Use case: {suggestion.use_case}")
            click.echo(f"   Confidence: {suggestion.confidence:.0%}")
            
            if suggestion.style_suggestions:
                click.echo(f"   Suggested style: {suggestion.style_suggestions}")
            click.echo()
        
        # Auto-generate if requested
        if generate:
            click.echo("📦 Generating icons...")
            generator = IconGenerator(output_dir="output")
            
            generated = []
            for suggestion in response.suggestions[:count]:
                output_name = suggestion.icon_name.replace(':', '_').replace('/', '_')
                
                # Use style suggestions if available
                style_opts = suggestion.style_suggestions or {}
                
                result = generator.generate_icon(
                    icon_name=suggestion.icon_name,
                    output_name=output_name,
                    color=style_opts.get('color', 'white'),
                    size=style_opts.get('size', 256),
                    bg_color=style_opts.get('bg_color'),
                    border_radius=style_opts.get('border_radius', 0)
                )
                
                if result:
                    generated.append(result)
                    click.echo(f"✓ {result}")
            
            click.echo(f"\n✓ Generated {len(generated)}/{count} icons in output/")
        else:
            click.echo("💡 Tip: Add --generate to automatically create these icons")
            
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def providers():
    """Show available AI providers and their status."""
    try:
        from .ai import get_available_providers, IconAssistant
        
        click.echo("\n📡 AI Provider Status\n")
        
        available = get_available_providers()
        
        if not available:
            click.echo("✗ No AI providers installed")
            click.echo("  Install with: pip install icon-gen-ai[ai]")
            return
        
        click.echo(f"Installed providers: {', '.join(available)}\n")
        
        # Check configuration
        assistant = IconAssistant()
        
        if assistant.is_available():
            provider_name = assistant.provider.get_provider_name()
            model = assistant.provider.model
            click.echo(f"✓ Active provider: {provider_name}")
            click.echo(f"  Model: {model}")
            click.echo(f"  Status: Ready")
        else:
            click.echo("⚠ No provider configured")
            click.echo("  Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        
        click.echo()
        
    except ImportError:
        click.echo("✗ AI features not available")
        click.echo("  Install with: pip install icon-gen-ai[ai]")


# Keep backwards compatibility - default command
@click.command()
@click.argument('icon_name')
@click.option('--color', default='white', help='Icon color')
@click.option('--size', default=256, help='Icon size in pixels')
@click.option('--format', 'output_format', default='svg', 
              type=click.Choice(['png', 'svg', 'webp']))
@click.option('--output', '-o', help='Output file path')
@click.option('--bg-color', help='Background color')
@click.option('--border-radius', default=0, help='Border radius')
def main(icon_name, color, size, output_format, output, bg_color, border_radius):
    """Generate icons from Iconify (legacy command).
    
    New syntax: Use 'icon-gen-ai generate' instead.
    """
    # Redirect to generate command
    from click import Context
    ctx = Context(generate)
    ctx.invoke(
        generate,
        icon_name=icon_name,
        color=color,
        size=size,
        output_format=output_format,
        output=output,
        bg_color=bg_color,
        border_radius=border_radius
    )


if __name__ == '__main__':
    cli()