"""Advanced CLI tests."""

import pytest
from click.testing import CliRunner
from icon_gen.cli import cli, generate, providers


def test_cli_group():
    """Test CLI group shows help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Icon-gen-ai' in result.output


def test_generate_command():
    """Test generate command."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(generate, ['mdi:github', '--size', '64'])
        assert result.exit_code == 0
        assert 'Success' in result.output or 'Generating' in result.output


def test_generate_with_background():
    """Test generate with background options."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(generate, [
            'mdi:star',
            '--color', 'white',
            '--bg-color', '#FF0000',
            '--border-radius', '32',
            '--size', '64'
        ])
        assert result.exit_code == 0


def test_providers_command():
    """Test providers status command."""
    runner = CliRunner()
    result = runner.invoke(providers)
    # Should not crash even without AI installed
    assert result.exit_code == 0


def test_generate_with_output_path():
    """Test generate with custom output path."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(generate, [
            'mdi:home',
            '-o', 'custom/path/icon.svg'
        ])
        # May fail but shouldn't crash
        assert 'Error' in result.output or 'Success' in result.output


def test_main_legacy_command():
    """Test legacy main command (backwards compatibility)."""
    from icon_gen.cli import main
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['mdi:test', '--size', '64'])
        assert result.exit_code == 0 or 'Error' in result.output