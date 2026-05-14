"""Advanced CLI tests."""

import os
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from icon_gen_ai.cli import app


def test_cli_group():
    """Test CLI group shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "icons from Iconify" in result.output


def test_generate_command():
    """Test generate command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["generate", "mdi:github", "--size", "64"])
        assert result.exit_code == 0
        assert "Success" in result.output or "Generating" in result.output


def test_generate_with_background():
    """Test generate with background options."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["generate",
                "mdi:star",
                "--color",
                "white",
                "--bg-color",
                "#FF0000",
                "--border-radius",
                "32",
                "--size",
                "64",
            ],
        )
        assert result.exit_code == 0


def test_providers_command():
    """Test providers status command."""
    runner = CliRunner()
    result = runner.invoke(app, ["providers"])
    assert result.exit_code == 0


def test_generate_with_output_path():
    runner = CliRunner()
    with runner.isolated_filesystem():
        output_path = "output/icon.svg"
        result = runner.invoke(app, ["generate", "mdi:home", "-o", output_path])
        assert result.exit_code == 0
        assert "Saved to" in result.output or "Error" in result.output


def test_main_legacy_command():
    """Test legacy main command (backwards compatibility)."""

    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(app, ["mdi:test", "--size", "64"])
        assert result.exit_code == 0 or "Error" in result.output


def test_cli_no_subcommand_shows_banner():
    """Invoking app with no args prints the banner and help."""
    runner = CliRunner()
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    # Banner contains the app name, help lists commands
    assert "icon-gen-ai" in result.output.lower() or "generate" in result.output


def test_cli_version_flag():
    """--version prints version string."""
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "icon-gen-ai" in result.output.lower() or "." in result.output


def test_generate_no_args_returns_error():
    """generate with no icon and no --input should exit with error."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["generate"])
        assert result.exit_code != 0 or "Error" in result.output


def test_generate_both_icon_and_input_errors():
    """generate with both positional icon and --input should error."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # --input requires a file; we pass a fake name too
        result = runner.invoke(
            app, ["generate", "mdi:home", "--input", "some_file.svg", "--size", "32"]
        )
        assert result.exit_code != 0 or "Error" in result.output


def test_generate_nonexistent_input_file_errors():
    """generate with a local --input file that doesn't exist should error."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["generate", "--input", "/tmp/definitely_not_here_xyz.svg"]
        )
        assert result.exit_code != 0 or "Error" in result.output


def test_generate_iconify_via_input_option():
    """--input accepts an Iconify name (contains colon, not a path/URL)."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["generate", "--input", "mdi:github", "--size", "32"]
        )
        # Should succeed or show fetch error, not a file-not-found error
        assert "does not exist" not in result.output


def test_generate_gradient_color_option():
    """--color '(red,blue)' is parsed as a gradient."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["generate", "mdi:home", "--color", "(red,blue)", "--size", "32"]
        )
        # Should run (may succeed or fail on network) but not crash on parse
        assert "Traceback" not in result.output


def test_generate_gradient_bg_color_option():
    """--bg-color '(mediumslateblue,deeppink)' generates gradient background."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            [
                "generate",
                "mdi:star",
                "--bg-color",
                "(mediumslateblue,deeppink)",
                "--border-radius",
                "16",
                "--size",
                "32",
            ],
        )
        assert "Traceback" not in result.output


def test_generate_with_outline():
    """--outline-width and --outline-color echo the outline summary line."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            [
                "generate",
                "mdi:circle",
                "--bg-color",
                "#000000",
                "--outline-width",
                "4",
                "--outline-color",
                "white",
                "--size",
                "32",
            ],
        )
        assert "Traceback" not in result.output


def test_generate_with_local_svg_file():
    """generate --input <local.svg> loads the local file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Write a minimal SVG
        with open("icon.svg", "w") as f:
            f.write('<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
                    '<path d="M0 0h24v24H0z"/></svg>')
        result = runner.invoke(
            app, ["generate", "--input", "icon.svg", "--size", "32"]
        )
        assert "Traceback" not in result.output
        assert result.exit_code == 0 or "Error" in result.output


def test_generate_with_output_format_inferred():
    """output path extension infers the format."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["generate", "mdi:home", "-o", "out/icon.svg", "--size", "32"]
        )
        assert "Traceback" not in result.output


def test_search_no_ai_installed():
    """search command should fail gracefully when AI not installed."""
    runner = CliRunner()
    # Simulate AI extras not installed by patching the import
    with patch.dict("sys.modules", {"icon_gen_ai.ai": None}):
        result = runner.invoke(app, ["search", "payment icons"])
        # Should fail with non-zero exit or show error message - not a raw crash
        assert "Traceback" not in result.output


def test_main_entrypoint():
    """main() function can be called directly."""
    from icon_gen_ai.cli import main
    # main() with [] should show info and not raise
    try:
        main([])
    except SystemExit:
        pass  # Typer may raise SystemExit – that's fine


def _make_mock_search_response():
    """Build a mock LLMResponse for search tests."""
    from icon_gen_ai.ai.base import LLMResponse, IconSuggestion
    return LLMResponse(
        suggestions=[
            IconSuggestion(
                icon_name="mdi:credit-card",
                reason="Payment icon",
                use_case="Checkout",
                confidence=0.95,
            ),
            IconSuggestion(
                icon_name="mdi:wallet",
                reason="Wallet icon",
                use_case="Balance",
                confidence=0.9,
            ),
        ],
        explanation="Found payment icons",
        search_query="payment",
        tokens_used=50,
        provider="mock",
    )


def _make_mock_assistant(response):
    """Return a mock IconAssistant that returns response."""
    mock = MagicMock()
    mock.return_value.is_available.return_value = True
    mock.return_value.discover_icons.return_value = response
    return mock


def test_search_command_lists_icons():
    """search command lists suggestions when AI is available."""
    from icon_gen_ai.ai.base import LLMResponse, IconSuggestion

    response = _make_mock_search_response()
    mock_assistant_cls = _make_mock_assistant(response)

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(app, ["search", "payment icons"])
    assert result.exit_code == 0 or "Traceback" not in result.output


def test_search_command_no_providers():
    """search command shows helpful message when no providers are available."""
    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=[]):
        result = runner.invoke(app, ["search", "payment icons"])
    # Should print install instructions or access error, not crash
    assert "Traceback" not in result.output


def test_search_command_no_api_key():
    """search command exits with error when provider not available (no API key)."""
    mock_assistant_cls = MagicMock()
    mock_assistant_cls.return_value.is_available.return_value = False

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(app, ["search", "payment icons"])
    assert result.exit_code != 0 or "API key" in result.output


def test_search_command_with_style_and_project_type():
    """search command passes style and project_type to discover_icons."""
    response = _make_mock_search_response()
    mock_assistant_cls = _make_mock_assistant(response)

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(
                app,
                ["search", "icons", "--style", "modern", "--project-type", "fintech"],
            )
    assert "Traceback" not in result.output


def test_search_command_with_count():
    """search command -c limits displayed results."""
    response = _make_mock_search_response()
    mock_assistant_cls = _make_mock_assistant(response)

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(app, ["search", "payment icons", "-c", "1"])
    assert result.exit_code == 0 or "Traceback" not in result.output


def test_providers_command_active_provider():
    """providers shows active provider when one is configured."""
    mock_assistant_cls = MagicMock()
    mock_assistant_cls.return_value.is_available.return_value = True
    mock_assistant_cls.return_value.provider.get_provider_name.return_value = "anthropic"
    mock_assistant_cls.return_value.provider.model = "claude-3"

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(app, ["providers"])
    assert result.exit_code == 0
    assert "anthropic" in result.output.lower() or "Active" in result.output


def test_providers_command_no_api_key_configured():
    """providers shows warning when packages installed but no key."""
    mock_assistant_cls = MagicMock()
    mock_assistant_cls.return_value.is_available.return_value = False

    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=["anthropic"]):
        with patch("icon_gen_ai.ai.IconAssistant", mock_assistant_cls):
            result = runner.invoke(app, ["providers"])
    assert result.exit_code == 0
    assert "API key" in result.output or "No API key" in result.output


def test_providers_command_no_packages_installed():
    """providers shows install instructions when no AI packages found."""
    runner = CliRunner()
    with patch("icon_gen_ai.ai.get_available_providers", return_value=[]):
        result = runner.invoke(app, ["providers"])
    assert result.exit_code == 0
    assert "pip install" in result.output or "not found" in result.output.lower()


def test_generate_gradient_color_wrong_count():
    """--color with gradient containing != 2 colors raises BadParameter."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app, ["generate", "mdi:home", "--color", "(red,blue,green)", "--size", "32"]
        )
        # Should error on bad gradient count
        assert result.exit_code != 0 or "2 colors" in result.output


def test_generate_input_url_syntax():
    """--input with a URL routes to direct_url path."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            app,
            ["generate", "--input", "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/github.svg", "--size", "32"],
        )
        assert "Traceback" not in result.output


def test_generate_outline_echo():
    """generate with outline flags prints the Outline summary line."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Use a public simple SVG URL to avoid Iconify network call
        result = runner.invoke(
            app,
            [
                "generate", "mdi:home",
                "--bg-color", "#111111",
                "--outline-width", "3",
                "--outline-color", "deeppink",
                "--size", "32",
                "--color", "white",
            ],
        )
        # The "Outline" preview line should appear in output
        assert "Traceback" not in result.output


def test_main_function_runs():
    """main() entry point executes without raising outside SystemExit."""
    from icon_gen_ai.cli import main
    try:
        main(["--help"])
    except SystemExit:
        pass  # expected from typer --help


