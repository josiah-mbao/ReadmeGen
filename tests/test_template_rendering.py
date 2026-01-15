"""
Comprehensive template rendering tests.
Validates all template variations and context handling.
"""

import pytest
from readme_generator.templates import render_template


class TestTemplateRendering:
    """Comprehensive template rendering tests."""

    @pytest.fixture
    def sample_context(self):
        """Provide comprehensive sample template context."""
        return {
            "project_name": "TestProject",
            "description": "A comprehensive test project for validating template rendering",
            "license": "MIT",
            "features": ["Feature 1", "Feature 2", "Feature 3"],
            "usage_example": "import testproject; testproject.run()",
            "project_type": "python",
            "ai_enabled": False,
            "github_enabled": False
        }

    @pytest.mark.parametrize("template_name", ["minimal", "standard", "fancy"])
    def test_template_renders_with_complete_context(self, template_name, sample_context):
        """Test that all templates render successfully with complete context."""
        rendered = render_template(template_name, sample_context)

        assert rendered is not None
        assert isinstance(rendered, str)
        assert len(rendered) > 100  # Should be substantial content

        # Verify essential content is present
        assert sample_context["project_name"] in rendered
        assert sample_context["description"] in rendered
        assert sample_context["license"] in rendered

    def test_minimal_template_renders(self, sample_context):
        """Test minimal template renders correctly."""
        rendered = render_template("minimal", sample_context)

        assert rendered is not None
        assert "# TestProject" in rendered
        assert "## Installation" in rendered
        assert "## Features" in rendered
        assert "## Usage" in rendered
        assert "## License" in rendered

        # Check project-type specific content
        assert "pip install" in rendered  # Python-specific

    def test_standard_template_renders(self, sample_context):
        """Test standard template renders correctly."""
        rendered = render_template("standard", sample_context)

        assert rendered is not None
        assert "# TestProject" in rendered
        assert "## Table of Contents" in rendered
        assert "## Prerequisites" in rendered
        assert "## Installation" in rendered
        assert "## Features" in rendered
        assert "## Usage" in rendered
        assert "## Contributing" in rendered
        assert "## License" in rendered

        # Check TOC links
        assert "- [Prerequisites]" in rendered
        assert "- [Installation]" in rendered
        assert "- [Contributing]" in rendered

    def test_fancy_template_renders(self, sample_context):
        """Test fancy template renders correctly."""
        rendered = render_template("fancy", sample_context)

        assert rendered is not None
        assert "# TestProject" in rendered
        assert "✨ Features" in rendered
        assert "🚀 Quick Start" in rendered
        assert "🛠️ Installation" in rendered
        assert "💻 Usage" in rendered
        assert "## 🧪 Testing" in rendered
        assert "## 🤝 Contributing" in rendered
        assert "## 📜 License" in rendered

    def test_template_handles_missing_context(self):
        """Test templates handle missing or minimal context gracefully."""
        minimal_context = {
            "project_name": "TestProject",
            "description": "Test description"
        }

        for template_name in ["minimal", "standard", "fancy"]:
            rendered = render_template(template_name, minimal_context)
            assert rendered is not None
            assert "TestProject" in rendered
            assert "Test description" in rendered

    def test_template_handles_empty_features(self):
        """Test templates handle empty or missing features."""
        context = {
            "project_name": "TestProject",
            "description": "Test description",
            "license": "MIT",
            "features": [],  # Empty features
            "usage_example": "",
            "project_type": "python"
        }

        rendered = render_template("standard", context)
        assert rendered is not None
        assert "TestProject" in rendered
        # Should still render but may use default features

    def test_template_handles_long_content(self):
        """Test templates handle very long content gracefully."""
        long_description = "A" * 500
        many_features = [f"Feature {i}" for i in range(20)]

        context = {
            "project_name": "TestProject",
            "description": long_description,
            "license": "MIT",
            "features": many_features,
            "usage_example": "",
            "project_type": "python"
        }

        rendered = render_template("standard", context)
        assert rendered is not None
        assert len(rendered) > 1000  # Should handle long content
        assert long_description[:100] in rendered  # At least part of long description

    def test_template_invalid_name(self):
        """Test handling of invalid template names."""
        context = {"project_name": "Test", "description": "Test"}

        rendered = render_template("nonexistent_template", context)
        assert rendered is None

    def test_template_special_characters(self):
        """Test templates handle special characters in content."""
        context = {
            "project_name": "Test-Project_123",
            "description": "Description with & < > \" ' symbols",
            "license": "MIT",
            "features": ["Feature with @#$%^&*()"],
            "usage_example": "code with `backticks` and <tags>",
            "project_type": "python"
        }

        rendered = render_template("minimal", context)
        assert rendered is not None
        assert "Test-Project_123" in rendered
        assert "symbols" in rendered  # Should handle special chars

    def test_template_markdown_escaping(self):
        """Test that templates properly handle markdown-sensitive content."""
        context = {
            "project_name": "Test[Project]",
            "description": "Description with *emphasis* and **strong** text",
            "license": "MIT",
            "features": ["Feature with [link](url) and `code`"],
            "usage_example": "",
            "project_type": "python"
        }

        rendered = render_template("minimal", context)
        assert rendered is not None
        assert "Test[Project]" in rendered  # Should preserve brackets
        assert "*emphasis*" in rendered  # Should preserve markdown

    def test_template_license_badge_generation(self):
        """Test license badge generation in templates."""
        licenses = ["MIT", "Apache 2.0", "GPL 3.0", "BSD 3-Clause"]

        for license_name in licenses:
            context = {
                "project_name": "TestProject",
                "description": "Test",
                "license": license_name,
                "features": ["Feature 1"],
                "usage_example": "",
                "project_type": "python"
            }

            rendered = render_template("minimal", context)
            assert rendered is not None
            assert f"License: {license_name}" in rendered

            # Fancy template should have badge
            fancy_rendered = render_template("fancy", context)
            assert fancy_rendered is not None
            assert "shields.io" in fancy_rendered

    def test_template_feature_formatting(self):
        """Test feature list formatting across templates."""
        features = [
            "Short feature",
            "A very long feature description that should wrap properly in the template",
            "Feature with special chars: @#$%^&*()",
            "Feature with [link](url)"
        ]

        context = {
            "project_name": "TestProject",
            "description": "Test",
            "license": "MIT",
            "features": features,
            "usage_example": "",
            "project_type": "python"
        }

        for template_name in ["minimal", "standard", "fancy"]:
            rendered = render_template(template_name, context)
            assert rendered is not None

            for feature in features:
                assert feature in rendered
