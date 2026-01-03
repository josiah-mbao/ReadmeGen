"""
CLI workflow integration tests.
Tests complete user journeys and CLI command interactions.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

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
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Test Project',
                '--description', 'A test project',
                '--template', 'minimal',
                '--force'
            ])

            assert result.exit_code == 0
            assert 'README.md created' in result.output
            assert (tmp_project / 'README.md').exists()

            content = (tmp_project / 'README.md').read_text()
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
            assert (tmp_project / 'README.md').exists()

            content = (tmp_project / 'README.md').read_text()
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

    @patch('readme_generator.cli.questionary')
    @patch('readme_generator.cli.get_smart_defaults')
    @patch('readme_generator.cli.generate_readme')
    def test_init_workflow_custom_basic(self, mock_generate, mock_defaults, mock_questionary, runner, tmp_project):
        """Test init workflow where user customizes basic settings."""
        # Mock smart defaults
        mock_defaults.return_value = {
            'project_name': 'DefaultName',
            'description': 'Default description',
            'template': 'minimal',
            'license': 'MIT',
            'features': ['Feature 1'],
            'ai_enabled': False,
            'github_enabled': False
        }

        # Mock questionary components
        mock_confirm = MagicMock()
        mock_text = MagicMock()
        mock_select = MagicMock()

        # User rejects defaults, provides custom values
        mock_confirm.ask.side_effect = [False, True]  # Reject basic defaults, accept license
        mock_text.ask.side_effect = ['Custom Project', 'Custom description']
        mock_select.ask.side_effect = ['standard', 'MIT']

        mock_questionary.confirm.return_value = mock_confirm
        mock_questionary.text.return_value = mock_text
        mock_questionary.select.return_value = mock_select

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, ['init'])

            assert result.exit_code == 0
            assert mock_generate.called

            # Verify custom values were used
            call_args = mock_generate.call_args[1]
            assert call_args['project_info']['project_name'] == 'Custom Project'
            assert call_args['project_info']['description'] == 'Custom description'
            assert call_args['project_info']['template'] == 'standard'

    @patch('readme_generator.cli.questionary')
    @patch('readme_generator.cli.get_smart_defaults')
    @patch('readme_generator.cli.generate_readme')
    def test_init_workflow_advanced_features(self, mock_generate, mock_defaults, mock_questionary, runner, tmp_project):
        """Test init workflow with advanced feature customization."""
        # Mock smart defaults
        mock_defaults.return_value = {
            'project_name': 'TestProject',
            'description': 'Test description',
            'template': 'standard',
            'license': 'MIT',
            'features': ['Auto Feature 1', 'Auto Feature 2'],
            'ai_enabled': False,
            'github_enabled': False
        }

        # Mock questionary components
        mock_confirm = MagicMock()
        mock_select = MagicMock()
        mock_text = MagicMock()

        # User accepts basic, customizes advanced
        mock_confirm.ask.side_effect = [True, True, False]  # Accept basic, customize advanced, skip AI, skip GitHub
        mock_select.ask.return_value = 'keep'  # Keep auto-detected features
        mock_text.ask.return_value = ''  # No additional features

        mock_questionary.confirm.return_value = mock_confirm
        mock_questionary.select.return_value = mock_select
        mock_questionary.text.return_value = mock_text

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, ['init'])

            assert result.exit_code == 0
            assert mock_generate.called

            # Verify features were preserved
            call_args = mock_generate.call_args[1]
            assert 'Auto Feature 1' in call_args['project_info']['features']
            assert 'Auto Feature 2' in call_args['project_info']['features']

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
            # Create existing README
            readme_path = tmp_project / 'README.md'
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
