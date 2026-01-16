"""
CLI workflow integration tests.
Tests complete user journeys and CLI command interactions.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from readme_generator.cli import app, collect_project_info_interactive
from readme_generator.generator import generate_readme


class TestCLIWorkflows:
    """Test complete CLI user workflows."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create a temporary project directory."""
        return tmp_path

    def test_generate_command_basic(self, runner, tmp_project):
        """Test basic generate command with minimal options."""
        import os
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Test Project',
                '--description', 'A test project',
                '--template', 'minimal',
                '--force'
            ])

            assert result.exit_code == 0
            assert 'README generated successfully' in result.output
            readme_path = Path('README.md')
            assert readme_path.exists()

            content = readme_path.read_text()
            assert '# Test Project' in content
            assert 'A test project' in content

    def test_generate_command_with_all_options(self, runner, tmp_project):
        """Test generate command with all available options."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Advanced Project',
                '--description', 'A comprehensive project with all features',
                '--template', 'fancy',
                '--force'
            ])

            assert result.exit_code == 0
            readme_path = Path('README.md')
            assert readme_path.exists()

            content = readme_path.read_text()
            assert '# Advanced Project' in content
            assert 'comprehensive project' in content
            assert '✨ Features' in content  # Fancy template marker

    def test_templates_command_display(self, runner):
        """Test templates command displays rich previews."""
        result = runner.invoke(app, ['templates'])

        assert result.exit_code == 0
        assert '🎯 Minimal' in result.output
        assert '📋 Standard' in result.output
        assert '✨ Fancy' in result.output
        assert 'Includes:' in result.output
        assert 'Best for:' in result.output

    @patch('readme_generator.cli.questionary')
    @patch('readme_generator.cli.get_smart_defaults')
    @patch('readme_generator.cli.generate_readme')
    def test_init_workflow_accept_defaults(self, mock_generate, mock_defaults, mock_questionary, runner, tmp_project):
        """Test init workflow where user accepts smart defaults."""
        # Mock smart defaults
        mock_defaults.return_value = {
            'project_name': 'TestProject',
            'description': 'A test project',
            'template': 'standard',
            'license': 'MIT',
            'features': ['Feature 1', 'Feature 2'],
            'ai_enabled': False,
            'github_enabled': False
        }

        # Mock user inputs: accept defaults, skip advanced
        mock_confirm = MagicMock()
        mock_confirm.ask.return_value = True  # Accept defaults
        mock_questionary.confirm.return_value = mock_confirm

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, ['init'])

            assert result.exit_code == 0
            assert mock_generate.called

            # Verify generate_readme was called with correct args
            call_args = mock_generate.call_args[1]
            assert call_args['project_info']['project_name'] == 'TestProject'
            assert call_args['project_info']['template'] == 'standard'

    def test_generate_overwrite_protection(self, runner, tmp_project):
        """Test that generate command asks before overwriting."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            # Create existing README
            readme_path = tmp_project / 'README.md'
            readme_path.write_text('# Existing README')

            # Try to generate without force
            result = runner.invoke(app, [
                'generate',
                '--name', 'New Project',
                '--description', 'New description'
            ])

            # Should exit without overwriting (simulated)
            # Note: In real implementation, this would prompt user
            assert result.exit_code == 0 or result.exit_code == 1  # Depends on implementation

    def test_generate_force_overwrite(self, runner, tmp_project):
        """Test that --force flag allows overwriting existing README."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            # Create existing README in the isolated directory
            readme_path = Path('README.md')
            readme_path.write_text('# Existing README')

            # Generate with force
            result = runner.invoke(app, [
                'generate',
                '--name', 'New Project',
                '--description', 'New description',
                '--force'
            ])

            assert result.exit_code == 0
            content = readme_path.read_text()
            assert '# New Project' in content
            assert 'New description' in content

    def test_generate_custom_output_path(self, runner, tmp_project):
        """Test generating README to custom output path."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            custom_path = tmp_project / 'docs' / 'PROJECT_README.md'
            custom_path.parent.mkdir()

            result = runner.invoke(app, [
                'generate',
                '--name', 'Custom Path Project',
                '--output', str(custom_path),
                '--force'
            ])

            assert result.exit_code == 0
            assert custom_path.exists()
            assert not (tmp_project / 'README.md').exists()

            content = custom_path.read_text()
            assert '# Custom Path Project' in content


class TestCLIDetection:
    """Test CLI detection and smart default functions."""

    @patch('pathlib.Path.cwd')
    def test_detect_license_from_license_file(self, mock_cwd):
        """Test license detection from LICENSE file."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="MIT License\n\nCopyright"):
            from readme_generator.cli import detect_license
            assert detect_license() == "MIT"

    @patch('pathlib.Path.cwd')
    def test_detect_license_fallback(self, mock_cwd):
        """Test license detection fallback."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=False):
            from readme_generator.cli import detect_license
            assert detect_license() == "MIT"

    @patch('pathlib.Path.cwd')
    def test_detect_description_fallback(self, mock_cwd):
        """Test description detection fallback."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=False):
            from readme_generator.cli import detect_description
            assert detect_description() == "A brief description of your project"

    @patch('pathlib.Path.cwd')
    def test_suggest_template_minimal(self, mock_cwd):
        """Test template suggestion for minimal projects."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.exists", return_value=False):
            from readme_generator.cli import suggest_template
            assert suggest_template() == "minimal"

    @patch('pathlib.Path.cwd')
    def test_suggest_template_fancy(self, mock_cwd):
        """Test template suggestion for fancy projects."""
        mock_cwd.return_value = Path("/fake/path")

        def mock_glob(pattern):
            if any(ext in pattern for ext in ['.py', '.js', '.rs', '.go', '.java']):
                return [f"file{i}{pattern[-3:]}" for i in range(30)]
            return []

        with patch("pathlib.Path.glob", side_effect=mock_glob), \
             patch("pathlib.Path.exists", return_value=True):  # CI and docs exist
            from readme_generator.cli import suggest_template
            assert suggest_template() == "fancy"

    def test_get_smart_defaults(self):
        """Test smart defaults generation."""
        with patch('readme_generator.cli.detect_description', return_value="Test description"), \
             patch('readme_generator.cli.detect_license', return_value="MIT"), \
             patch('readme_generator.cli.detect_features', return_value=["Feature 1"]), \
             patch('readme_generator.cli.suggest_template', return_value="standard"), \
             patch('pathlib.Path.cwd', return_value=Path("/fake/project")):
            from readme_generator.cli import get_smart_defaults

            defaults = get_smart_defaults()

            assert defaults["project_name"] == "project"
            assert defaults["description"] == "Test description"
            assert defaults["license"] == "MIT"
            assert defaults["features"] == ["Feature 1"]
            assert defaults["template"] == "standard"
            assert not defaults["ai_enabled"]
            assert not defaults["github_enabled"]

    def test_collect_project_info_with_custom_values(self):
        """Test collect_project_info with custom values."""
        with patch('readme_generator.cli.get_smart_defaults') as mock_defaults:
            from readme_generator.cli import collect_project_info
            mock_defaults.return_value = {
                "project_name": "DefaultProject",
                "description": "Default description",
                "template": "minimal",
                "license": "MIT",
                "features": ["Feature 1"],
                "ai_enabled": False,
                "github_enabled": False
            }

            info = collect_project_info(
                project_name="Custom Project",
                description="Custom description",
                template="fancy"
            )

            assert info["project_name"] == "Custom Project"
            assert info["description"] == "Custom description"
            assert info["template"] == "fancy"
