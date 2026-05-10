"""Command-line interface for icon-gen-ai."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import typer
from importlib.metadata import version
from .generator import IconGenerator

VERSION = version("icon-gen-ai")


# -------------------- ENUMS --------------------


class OutputFormat(str, Enum):
    svg = "svg"
    png = "png"
    webp = "webp"


class Direction(str, Enum):
    horizontal = "horizontal"
    vertical = "vertical"
    diagonal = "diagonal"
    radial = "radial"


# -------------------- HELPERS --------------------


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https")


def parse_color(value: str | None, label: str):
    if not value or value.lower() == "none":
        return None

    if value.startswith("(") and value.endswith(")"):
        colors = [c.strip() for c in value[1:-1].split(",")]
        if len(colors) != 2:
            raise typer.BadParameter(
                f"{label} gradient must have exactly 2 colors: (color1,color2)"
            )
        return tuple(colors)

    return value


# -------------------- CLI --------------------

# Color palette
SLATEBLUE = (123, 104, 238)  # mediumslateblue
DEEPPINK = (255, 20, 147)    # deeppink
SKYBLUE = (0, 191, 255)      # deepskyblue

BANNER = """\
 +-+-+-+-+-+-+-+-+-+-+-+
 |i|c|o|n|-|g|e|n|-|a|i|
 +-+-+-+-+-+-+-+-+-+-+-+
"""


def _label(text: str) -> str:
    """Deepskyblue label."""
    return typer.style(text, fg=SKYBLUE)


def _value(text: str) -> str:
    """Bold white value."""
    return typer.style(str(text), bold=True)


def _ok(text: str) -> str:
    """Mediumslateblue success marker."""
    return typer.style(text, fg=SLATEBLUE, bold=True)


def _warn(text: str) -> str:
    """Deeppink warning/error marker."""
    return typer.style(text, fg=DEEPPINK, bold=True)


def _muted(text: str) -> str:
    return typer.style(text, fg=SKYBLUE)


def _dim(text: str) -> str:
    return typer.style(text, dim=True)


def _print_help():
    typer.echo(
        typer.style(
            "  Generate pixel-perfect icons from Iconify, URLs, and local files.",
            fg=SKYBLUE,
        )
    )
    typer.echo("")
    typer.echo(typer.style("Usage:", fg=DEEPPINK, bold=True))
    typer.echo(
        "  icon-gen-ai "
        + typer.style("[OPTIONS]", fg=SLATEBLUE)
        + " "
        + typer.style("COMMAND", fg=SKYBLUE, bold=True)
        + " [ARGS]..."
    )
    typer.echo("")
    typer.echo(typer.style("Options:", fg=DEEPPINK, bold=True))
    typer.echo(
        "  " + typer.style("--version", fg=SLATEBLUE) + "  Show the version and exit."
    )
    typer.echo(
        "  " + typer.style("--help   ", fg=SLATEBLUE) + "  Show this message and exit."
    )
    typer.echo("")
    typer.echo(typer.style("Commands:", fg=DEEPPINK, bold=True))
    typer.echo(
        "  "
        + typer.style("generate ", fg=SKYBLUE, bold=True)
        + "  Generate icons from Iconify or local files."
    )
    typer.echo(
        "  "
        + typer.style("search   ", fg=SKYBLUE, bold=True)
        + "  Search for icons using AI-powered natural language queries."
    )
    typer.echo(
        "  "
        + typer.style("providers", fg=SKYBLUE, bold=True)
        + "  Show AI provider status."
    )
    typer.echo("")


def _print_banner():
    typer.echo(typer.style(BANNER, fg=SLATEBLUE, bold=True))
    typer.echo(typer.style(f"  v{VERSION}", fg=SKYBLUE) + "\n")


def _version_callback(value: bool):
    if value:
        typer.echo(
            typer.style("icon-gen-ai", fg=SLATEBLUE, bold=True)
            + "  "
            + typer.style(f"v{VERSION}", fg=DEEPPINK, bold=True)
        )
        typer.echo("")
        raise typer.Exit()


app = typer.Typer(
    add_completion=True,
    no_args_is_help=False,
    help="icon-gen-ai — generate icons from Iconify, URLs, or local files.",
)


@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """icon-gen-ai — generate icons from Iconify, URLs, or local files."""
    if ctx.invoked_subcommand is None:
        _print_banner()
        _print_help()


# -------------------- GENERATE --------------------


@app.command()
def generate(
    icon: Optional[str] = typer.Argument(
        None, help="Iconify icon name (e.g. simple-icons:openai)"
    ),
    input_file: Optional[str] = typer.Option(
        None, "-i", "--input", help="Local image file or direct URL"
    ),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output file path"),
    format: OutputFormat = typer.Option(
        OutputFormat.svg, "--format", help="Output format"
    ),
    size: int = typer.Option(256, "--size", show_default=True),
    scale: Optional[float] = typer.Option(
        None,
        "--scale",
        help="Icon scale (0.0-1.0). Default: 1.0 without bg, 0.7 with bg",
    ),
    color: Optional[str] = typer.Option(
        None, "--color", help="Icon color or gradient '(c1,c2)'"
    ),
    direction: Direction = typer.Option(
        Direction.horizontal,
        "--direction",
        show_default=True,
        help="Icon gradient direction",
    ),
    bg_color: Optional[str] = typer.Option(
        None, "--bg-color", help="Background color or gradient '(c1,c2)'"
    ),
    bg_direction: Direction = typer.Option(
        Direction.horizontal,
        "--bg-direction",
        show_default=True,
        help="Background gradient direction",
    ),
    border_radius: int = typer.Option(0, "--border-radius", show_default=True),
    outline_width: int = typer.Option(0, "--outline-width", show_default=True),
    outline_color: Optional[str] = typer.Option(
        None, "--outline-color", help="Outline color"
    ),
    animation: Optional[str] = typer.Option(
        None,
        "--animation",
        help="Animation preset e.g. 'spin:2s', 'pulse:1.5s', 'flip-h:1s', 'flip-v:1s'",
    ),
):
    """Generate icons from Iconify or local files.

    Examples:

        # From Iconify:
        icon-gen-ai generate simple-icons:openai --color white --size 254

        # From direct URL
        icon-gen-ai generate -i https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg -o output/claude-icon.svg \\
  --color deeppink --bg-color white --border-radius 64 --size 128 --outline-color deeppink --outline-width 4

        # From local file:
        icon-gen-ai generate -i input/deepseek-icon.png -o output/deepseek-icon.svg \\
  --color white --bg-color '(mediumslateblue,deeppink)' --border-radius 10 --size 128

        # Preserve original colors:
        icon-gen-ai generate -i devicon:pypi --bg-color '(tan,cyan)' --size 128 --border-radius 64

        # With gradient directions:
        icon-gen-ai generate gis:globe --color '(deeppink,mediumslateblue)' --direction diagonal \\
  --bg-color '(lime,white)' --bg-direction vertical --size 256 -o notes/globe.svg
    """

    if not icon and not input_file:
        typer.echo(_warn("Error: Provide ICON or --input"), err=True)
        raise typer.Exit(code=2)

    if icon and input_file:
        typer.echo(_warn("Error: Use either ICON or --input, not both"), err=True)
        raise typer.Exit(code=2)

    # Resolve input
    direct_url = None
    local_file = None
    icon_name = icon

    if input_file:
        # Check if it's an Iconify icon name (contains colon)
        if (
            ":" in input_file
            and not is_url(input_file)
            and not os.path.exists(input_file)
        ):
            icon_name = input_file
            input_file = None
        elif is_url(input_file):
            direct_url = input_file
        else:
            if not os.path.exists(input_file):
                typer.echo(_warn(f"Error: {input_file}: File does not exist"), err=True)
                raise typer.Exit(code=2)
            local_file = input_file

    # Parse colors
    parsed_color = parse_color(color, "Icon color")
    parsed_bg = parse_color(bg_color, "Background")

    # Output
    output_path = Path(output) if output else None
    output_dir = output_path.parent if output_path else Path("output")
    format_str = format.value

    if output_path:
        output_name = output_path.stem
        # Infer format from extension if output path is specified
        if output_path.suffix:
            inferred_format = output_path.suffix.lstrip(".")
            if inferred_format in ["svg", "png", "webp", "ico"]:
                format_str = inferred_format
    elif local_file:
        output_name = Path(local_file).stem
    elif direct_url:
        output_name = Path(urlparse(direct_url).path).stem or "icon"
    else:
        output_name = icon_name.replace(":", "_").replace("/", "_")

    generator = IconGenerator(output_dir=str(output_dir))

    typer.echo("\n" + _ok("◆ Generating icon") + "\n")
    typer.echo(f"  {_label('Source')}        {_value(icon_name or input_file)}")
    typer.echo(f"  {_label('Size')}          {_value(str(size) + 'px')}")
    if scale is not None:
        typer.echo(f"  {_label('Scale')}         {_value(f'{scale:.0%}')}")
    typer.echo(f"  {_label('Color')}         {_value(parsed_color or 'original')}")
    typer.echo(f"  {_label('Background')}    {_value(parsed_bg or 'transparent')}")
    typer.echo(f"  {_label('Border radius')} {_value(str(border_radius) + 'px')}")
    typer.echo(f"  {_label('Animation')}     {_value(animation or 'none')}")
    if outline_width > 0:
        typer.echo(
            f"  {_label('Outline')}       {_value(str(outline_width) + 'px')} {_muted('(' + str(outline_color) + ')')}"
        )

    result = generator.generate_icon(
        icon_name=icon_name,
        direct_url=direct_url,
        local_file=local_file,
        output_name=output_name,
        format=format_str,
        size=size,
        scale=scale,
        color=parsed_color,
        direction=direction.value,
        bg_color=parsed_bg,
        bg_direction=bg_direction.value,
        border_radius=border_radius,
        outline_width=outline_width,
        outline_color=outline_color,
        animation=animation,
    )

    if not result:
        typer.echo(_warn("Error: Failed to generate icon"), err=True)
        raise typer.Exit(code=1)

    typer.echo(
        "\n"
        + _ok("✓ Saved to ")
        + typer.style(str(result), fg=SKYBLUE, underline=True)
        + "\n"
    )


# -------------------- SEARCH --------------------


@app.command()
def search(
    query: str = typer.Argument(..., help="Natural language icon search query"),
    count: Optional[int] = typer.Option(
        None,
        "-c",
        "--count",
        help="Limit number of results to display (overrides LLM response)",
    ),
    generate_icons: bool = typer.Option(
        False, "-g", "--generate", help="Generate icon files"
    ),
    style: Optional[str] = typer.Option(
        None, "--style", help="Design style (modern, corporate, minimal, playful)"
    ),
    project_type: Optional[str] = typer.Option(
        None, "--project-type", help="Project type for context"
    ),
):
    """Search for icons using AI-powered natural language queries.

    The AI parses the count from your query (e.g., "5 icons for payment").
    Use -c to limit/truncate the results shown.

    Examples:

        icon-gen-ai search "payment icons for checkout"

        icon-gen-ai search "suggest 10 icons for drone" --style modern

        icon-gen-ai search "social media icons" -c 5 --generate

    Requires: pip install icon-gen-ai[ai] and ANTHROPIC_API_KEY, HF_TOKEN, or OPENAI_API_KEY
    """

    try:
        from .ai import IconAssistant, get_available_providers
    except ImportError:
        typer.echo(
            _warn("AI features not installed.")
            + " Run: "
            + typer.style('pip install "icon-gen-ai[ai]"', fg=SLATEBLUE),
            err=True,
        )
        raise typer.Exit(code=1)

    providers = get_available_providers()
    if not providers:
        typer.echo("\n" + _warn("✗ AI provider packages not found") + "\n")
        typer.echo(_label("Install AI extras:"))
        typer.echo(typer.style('  pip install "icon-gen-ai[ai]"', fg=SLATEBLUE))
        typer.echo("\n" + _label("Then configure an API key:"))
        typer.echo(f"  {_dim('•')} ANTHROPIC_API_KEY  (Anthropic)")
        typer.echo(f"  {_dim('•')} HF_TOKEN           (Hugging Face)")
        typer.echo(f"  {_dim('•')} OPENAI_API_KEY     (OpenAI)\n")
        return

    assistant = IconAssistant()
    if not assistant.is_available():
        typer.echo(
            _warn(
                "AI extras installed but no API key configured.\n"
                "Set one of: ANTHROPIC_API_KEY, HF_TOKEN, or OPENAI_API_KEY"
            ),
            err=True,
        )
        raise typer.Exit(code=1)

    context = {}
    if style:
        context["design_style"] = style
    if project_type:
        context["project_type"] = project_type

    typer.echo("\n" + _ok("◆ Searching: ") + _value(query) + "\n")

    response = assistant.discover_icons(query, context=context)

    # Truncate to user-specified count or show all (max 25)
    display_count = (
        min(count, len(response.suggestions))
        if count
        else min(25, len(response.suggestions))
    )

    for i, s in enumerate(response.suggestions[:display_count], 1):
        typer.echo(
            typer.style(f"  {i}. ", fg=DEEPPINK, bold=True) + _value(s.icon_name)
        )
        typer.echo(_muted(f"     {s.reason}") + "\n")

    if not generate_icons:
        return

    generator = IconGenerator(output_dir="output")

    typer.echo("\n" + _ok("◆ Generating icons...") + "\n")

    for s in response.suggestions[:display_count]:
        generator.generate_icon(
            icon_name=s.icon_name,
            output_name=s.icon_name.replace(":", "_"),
            size=(s.style_suggestions or {}).get("size", 256),
            color=(s.style_suggestions or {}).get("color", "white"),
            bg_color=(s.style_suggestions or {}).get("bg_color"),
            border_radius=(s.style_suggestions or {}).get("border_radius", 0),
        )


# -------------------- PROVIDERS --------------------


@app.command()
def providers():
    """Show AI provider status."""

    try:
        from .ai import IconAssistant, get_available_providers
    except ImportError:
        typer.echo("\n" + _warn("✗ AI features not installed") + "\n")
        typer.echo(_label("Install AI extras:"))
        typer.echo(typer.style('  pip install "icon-gen-ai[ai]"', fg=SLATEBLUE))
        typer.echo("\n" + _label("Then configure an API key:"))
        typer.echo(f"  {_dim('•')} ANTHROPIC_API_KEY  (Anthropic)")
        typer.echo(f"  {_dim('•')} HF_TOKEN           (Hugging Face)")
        typer.echo(f"  {_dim('•')} OPENAI_API_KEY     (OpenAI)\n")
        return

    providers_list = get_available_providers()

    if not providers_list:
        typer.echo("\n" + _warn("✗ AI provider packages not found") + "\n")
        typer.echo(_label("Install AI extras:"))
        typer.echo(typer.style('  pip install "icon-gen-ai[ai]"', fg=SLATEBLUE))
        typer.echo("\n" + _label("Then configure an API key:"))
        typer.echo(f"  {_dim('•')} ANTHROPIC_API_KEY  (Anthropic)")
        typer.echo(f"  {_dim('•')} HF_TOKEN           (Hugging Face)")
        typer.echo(f"  {_dim('•')} OPENAI_API_KEY     (OpenAI)\n")
        return

    typer.echo("")
    typer.echo(_ok("✓ ") + _label("AI extras installed"))
    typer.echo(
        _ok("✓ ") + _label("Available providers: ") + _value(", ".join(providers_list))
    )

    assistant = IconAssistant()
    if assistant.is_available():
        typer.echo(
            _ok("✓ ")
            + _label("Active provider:    ")
            + typer.style(
                assistant.provider.get_provider_name(), fg=DEEPPINK, bold=True
            )
            + _muted(f" ({assistant.provider.model})")
            + "\n"
        )
    else:
        typer.echo("\n" + _warn("⚠ No API key configured") + "\n")
        typer.echo(_label("Configure an API key to use AI features:"))
        typer.echo(f"  {_dim('•')} ANTHROPIC_API_KEY  (Anthropic)")
        typer.echo(f"  {_dim('•')} HF_TOKEN           (Hugging Face)")
        typer.echo(f"  {_dim('•')} OPENAI_API_KEY     (OpenAI)")
        typer.echo(_muted("\n  Set via environment variable or .env file") + "\n")


# -------------------- ENTRYPOINT --------------------


def main(args=None):
    """
    Entry point for console_scripts and testing.

    Args:
        args (list[str], optional): Command-line arguments to pass to Typer app.
    """
    app(args)


if __name__ == "__main__":
    main()
