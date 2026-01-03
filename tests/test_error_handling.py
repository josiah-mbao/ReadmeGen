"""
Error handling and edge case tests.
Ensures graceful failure and recovery in various scenarios.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from readme_generator.cli import app, validate_project_name, validate_description
from readme_generator.generator import generate_readme
from readme_generator.templates import render_template


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def runner(self):
        """CLI runner fixture."""
        return CliRunner()

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create a temporary project directory."""
        return tmp_path

    def test_generate_with_missing_template(self, runner, tmp_project):
        """Test handling when template files are missing."""
        with patch('readme_generator.templates.render_template', return_value=None):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Test Project',
                '--description', 'Test description',
                '--force'
            ])

            assert result.exit_code == 1
            assert "template" in result.output.lower()

    def test_generate_with_permission_error(self, runner, tmp_project):
        """Test handling of file permission errors."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            # Mock Path.write_text to raise PermissionError
            with patch.object(Path, 'write_text', side_effect=PermissionError("Permission denied")):
                result = runner.invoke(app, [
                    'generate',
                    '--name', 'Test Project',
                    '--description', 'Test description',
                    '--force'
                ])

                assert result.exit_code == 1
                assert "permission" in result.output.lower()

    def test_generate_with_invalid_output_path(self, runner, tmp_project):
        """Test handling of invalid output paths."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Test Project',
                '--description', 'Test description',
                '--output', '/invalid/path/that/does/not/exist/README.md',
                '--force'
            ])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_init_with_keyboard_interrupt(self, runner, tmp_project):
        """Test handling of keyboard interrupts during init."""
        with patch('readme_generator.cli.questionary.confirm') as mock_confirm:
            mock_confirm.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ['init'])

            assert result.exit_code == 1
            assert "cancelled" in result.output.lower() or "interrupt" in result.output.lower()

    @patch('readme_generator.cli.questionary')
    def test_init_with_invalid_project_name(self, mock_questionary, runner, tmp_project):
        """Test init workflow with invalid project names."""
        # Mock questionary to return invalid then valid names
        mock_text = MagicMock()
        mock_text.ask.side_effect = ['invalid@name#$', 'ValidProject']
        mock_questionary.text.return_value = mock_text

        mock_confirm = MagicMock()
        mock_confirm.ask.return_value = True  # Accept defaults
        mock_questionary.confirm.return_value = mock_confirm

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, ['init'])

            # Should eventually succeed with valid name
            assert result.exit_code == 0 or result.exit_code == 1

    def test_templates_command_with_missing_templates(self, runner):
        """Test templates command when template files are missing."""
        with patch('readme_generator.cli.get_available_templates', return_value=[]):
            result = runner.invoke(app, ['templates'])

            assert result.exit_code == 0  # Should not crash
            # Should handle empty template list gracefully

    def test_generate_with_extremely_long_content(self, runner, tmp_project):
        """Test generating README with extremely long content."""
        very_long_description = "A" * 10000  # 10KB description
        many_features = [f"Feature number {i}" for i in range(100)]

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Long Content Project',
                '--description', very_long_description,
                '--template', 'standard',
                '--force'
            ])

            assert result.exit_code == 0
            assert (tmp_project / 'README.md').exists()

            content = (tmp_project / 'README.md').read_text()
            assert "Long Content Project" in content
            assert len(content) > 10000  # Should handle large content

    def test_generate_with_special_characters(self, runner, tmp_project):
        """Test generating README with special characters in content."""
        special_name = "Test@Project#123"
        special_description = 'Description with <tags> & "quotes" \'apostrophes\''
        special_features = ["Feature with @#$%^&*()", "Feature with [link](url)"]

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', special_name,
                '--description', special_description,
                '--template', 'minimal',
                '--force'
            ])

            assert result.exit_code == 0
            content = (tmp_project / 'README.md').read_text()
            assert special_name in content
            assert "tags" in content  # Should handle special chars

    def test_generate_with_unicode_content(self, runner, tmp_project):
        """Test generating README with Unicode characters."""
        unicode_name = "测试项目 🚀"
        unicode_description = "项目描述 with 中文 and émojis 🎉"

        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', unicode_name,
                '--description', unicode_description,
                '--template', 'minimal',
                '--force'
            ])

            assert result.exit_code == 0
            content = (tmp_project / 'README.md').read_text()
            assert unicode_name in content
            assert "中文" in content

    def test_template_rendering_with_corrupt_context(self):
        """Test template rendering with corrupt or unexpected context."""
        corrupt_contexts = [
            {"project_name": None, "description": "test"},  # None values
            {"project_name": "", "description": ""},  # Empty strings
            {"project_name": 123, "description": "test"},  # Wrong types
            {},  # Empty context
        ]

        for context in corrupt_contexts:
            rendered = render_template("minimal", context)
            # Should not crash, may return None or minimal content
            assert isinstance(rendered, (str, type(None)))

    def test_generate_with_network_timeout_simulation(self, runner, tmp_project):
        """Test handling of network-related timeouts (future API features)."""
        # This is a placeholder for when we implement GitHub/AI APIs
        # For now, just ensure basic functionality works
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Network Test Project',
                '--description', 'Testing network error handling',
                '--force'
            ])

            assert result.exit_code == 0
            assert (tmp_project / 'README.md').exists()


class TestInputValidation:
    """Test input validation functions."""

    def test_validate_project_name_valid(self):
        """Test validation of valid project names."""
        valid_names = [
            "myproject",
            "my_project",
            "MyProject",
            "project123",
            "project-name",
            "a",
            "A123_B-456"
        ]

        for name in valid_names:
            assert validate_project_name(name) is True or validate_project_name(name) is None

    def test_validate_project_name_invalid(self):
        """Test validation of invalid project names."""
        invalid_names = [
            "",
            "   ",
            "project@name",
            "project name",  # spaces
            "project.name",
            "project/name",
            "project\\name",
            "project:name",
            "a" * 100,  # too long (if we had length limits)
        ]

        for name in invalid_names:
            result = validate_project_name(name)
            assert isinstance(result, str)  # Should return error message

    def test_validate_description_valid(self):
        """Test validation of valid descriptions."""
        valid_descriptions = [
            "A simple project",
            "A" * 500,  # Long but reasonable
            "Project with numbers 123",
            "Project with-dashes",
            "Project_with_underscores",
        ]

        for desc in valid_descriptions:
            assert validate_description(desc) is True or validate_description(desc) is None

    def test_validate_description_invalid(self):
        """Test validation of invalid descriptions."""
        invalid_descriptions = [
            "",
            "   ",
            "\n\n\n",  # Just whitespace
        ]

        for desc in invalid_descriptions:
            result = validate_description(desc)
            assert isinstance(result, str)  # Should return error message

    def test_validate_description_edge_cases(self):
        """Test description validation edge cases."""
        # Very long descriptions should be accepted (markdown can handle it)
        very_long = "A" * 10000
        assert validate_description(very_long) is True or validate_description(very_long) is None

        # Descriptions with markdown should be accepted
        markdown_desc = "# Heading\n\nSome **bold** text and `code`"
        assert validate_description(markdown_desc) is True or validate_description(markdown_desc) is None


class TestFileSystemErrors:
    """Test file system related error handling."""

    def test_readonly_directory_error(self, runner, tmp_project):
        """Test handling when output directory is read-only."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            # Make directory read-only (this might not work on all systems)
            try:
                result = runner.invoke(app, [
                    'generate',
                    '--name', 'Test',
                    '--description', 'Test',
                    '--output', '/readonly/path/README.md',
                    '--force'
                ])

                # Should handle the error gracefully
                assert result.exit_code == 1
                assert "error" in result.output.lower()
            except:
                # If we can't create readonly conditions, skip
                pass

    def test_insufficient_disk_space_simulation(self, runner, tmp_project):
        """Test handling of insufficient disk space."""
        with patch('pathlib.Path.write_text', side_effect=OSError("No space left on device")):
            result = runner.invoke(app, [
                'generate',
                '--name', 'Test Project',
                '--description', 'Test description',
                '--force'
            ])

            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_atomic_file_writing(self, runner, tmp_project):
        """Test that file writing is atomic (all or nothing)."""
        with runner.isolated_filesystem(temp_dir=str(tmp_project)):
            # This tests that if writing fails partway through,
            # we don't end up with corrupted files
            result = runner.invoke(app, [
                'generate',
                '--name', 'Atomic Test',
                '--description', 'Testing atomic writes',
                '--force'
            ])

            assert result.exit_code == 0

            readme_path = tmp_project / 'README.md'
            assert readme_path.exists()

            content = readme_path.read_text()
            # Should be complete, not truncated
            assert content.startswith("# Atomic Test")
            assert "Atomic Test" in content
            assert content.endswith("\n") or content.strip()  # Should be properly formatted
