"""
Generator module tests.
Tests README generation logic and template rendering.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from readme_generator.generator import (
    generate_readme,
    prepare_template_context,
    detect_project_type
)
from readme_generator.cli import get_smart_defaults
from readme_generator.templates import render_template


class TestGenerator:
    """Test README generation functionality."""

    def test_prepare_template_context(self):
        """Test template context preparation."""
        project_info = {
            "project_name": "TestProject",
            "description": "A test project",
            "features": ["Feature 1", "Feature 2"],
            "license": "MIT",
            "usage_example": "python main.py",
        }

        context = prepare_template_context(project_info)

        assert context["project_name"] == "TestProject"
        assert context["description"] == "A test project"
        assert context["features"] == ["Feature 1", "Feature 2"]
        assert context["license"] == "MIT"
        assert context["usage_example"] == "python main.py"
        assert context["ai_enabled"] is False
        assert context["github_enabled"] is False

    def test_prepare_template_context_with_ai_enabled(self):
        """Test template context with AI enabled."""
        project_info = {
            "project_name": "TestProject",
            "description": "A test project",
            "features": ["Feature 1"],
        }

        with patch('readme_generator.generator.enhance_content_with_ai') as mock_ai:
            mock_ai.return_value = {
                "enhanced_description": "Enhanced description",
                "suggested_features": ["AI Feature"],
                "ai_enhanced": True
            }

            context = prepare_template_context(project_info, ai_enabled=True)

            assert context["ai_enabled"] is True
            assert context["enhanced_description"] == "Enhanced description"
            assert context["ai_enhanced"] is True

    def test_generate_readme_basic(self, tmp_path):
        """Test basic README generation."""
        output_path = tmp_path / "README.md"
        project_info = {
            "project_name": "TestProject",
            "description": "A test project",
            "features": ["Feature 1"],
            "license": "MIT",
            "usage_example": "",
        }

        result = generate_readme(project_info, "minimal", output_path)

        assert result is True
        assert output_path.exists()

        content = output_path.read_text()
        assert "# TestProject" in content
        assert "A test project" in content

    def test_generate_readme_invalid_template(self, tmp_path):
        """Test README generation with invalid template."""
        output_path = tmp_path / "README.md"
        project_info = {
            "project_name": "TestProject",
            "description": "A test project",
        }

        with pytest.raises(ValueError, match="Failed to render template"):
            generate_readme(project_info, "nonexistent", output_path)

    def test_invalid_template(self):
        """Test handling of invalid template names."""
        result = render_template("nonexistent", {})
        assert result is None

    def test_empty_project_info(self):
        """Test generation with minimal project info."""
        context = prepare_template_context({})
        assert context["project_name"] == ""
        assert context["description"] == ""
        assert context["features"] == []


class TestDetection:
    """Test project type detection."""

    def test_detect_project_type_python(self):
        """Test Python project detection."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda self: "requirements.txt" in str(self) or "pyproject.toml" in str(self)
            assert detect_project_type(Path("/fake/path")) == "python"

    def test_detect_project_type_javascript(self):
        """Test JavaScript project detection."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda self: "package.json" in str(self)
            assert detect_project_type(Path("/fake/path")) == "javascript"

    def test_detect_project_type_rust(self):
        """Test Rust project detection."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda self: "Cargo.toml" in str(self)
            assert detect_project_type(Path("/fake/path")) == "rust"

    def test_detect_project_type_go(self):
        """Test Go project detection."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda self: "go.mod" in str(self)
            assert detect_project_type(Path("/fake/path")) == "go"

    def test_detect_project_type_java(self):
        """Test Java project detection."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda self: "pom.xml" in str(self) or "build.gradle" in str(self)
            assert detect_project_type(Path("/fake/path")) == "java"

    def test_detect_project_type_generic(self):
        """Test generic project type fallback."""
        with patch('pathlib.Path.exists', return_value=False):
            assert detect_project_type(Path("/fake/path")) == "generic"


class TestIntegration:
    """Test integration scenarios."""

    def test_smart_defaults_integration(self):
        """Test smart defaults work end-to-end."""
        with patch('readme_generator.generator.detect_description', return_value="Smart description"), \
             patch('readme_generator.generator.detect_license', return_value="MIT"), \
             patch('readme_generator.generator.detect_features', return_value=["Smart feature"]), \
             patch('readme_generator.generator.suggest_template', return_value="standard"), \
             patch('pathlib.Path.cwd', return_value=Path("/fake/project")):

            defaults = get_smart_defaults()

            assert defaults["project_name"] == "project"
            assert defaults["description"] == "Smart description"
            assert defaults["license"] == "MIT"
            assert defaults["features"] == ["Smart feature"]
            assert defaults["template"] == "standard"
