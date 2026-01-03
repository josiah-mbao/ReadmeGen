"""
Tests for the README generator functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from readme_generator.generator import (
    generate_readme,
    prepare_template_context,
    detect_project_type
)
from readme_generator.templates import render_template
from readme_generator.cli import (
    detect_license,
    detect_description,
    detect_features,
    suggest_template,
    get_feature_suggestions,
    get_smart_defaults
)


class TestDetection:
    """Test cases for project detection and auto-configuration."""

    @patch('pathlib.Path.cwd')
    def test_detect_license_from_license_file(self, mock_cwd):
        """Test license detection from LICENSE file."""
        mock_cwd.return_value = Path("/fake/path")

        # Test MIT license
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="MIT License\n\nCopyright"):
            assert detect_license() == "MIT"

        # Test Apache license
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="Apache License\nVersion 2.0"):
            assert detect_license() == "Apache 2.0"

    @patch('pathlib.Path.cwd')
    def test_detect_license_from_package_json(self, mock_cwd):
        """Test license detection from package.json."""
        mock_cwd.return_value = Path("/fake/path")

        # Test package.json license field
        package_json_data = {"license": "MIT"}
        with patch("pathlib.Path.exists", side_effect=lambda: self._mock_exists("package.json")), \
             patch("builtins.open", mock_open(read_data=json.dumps(package_json_data))):
            assert detect_license() == "MIT"

    def _mock_exists(self, filename):
        """Mock exists method for specific files."""
        return filename in ["package.json"]

    @patch('pathlib.Path.cwd')
    def test_detect_license_fallback(self, mock_cwd):
        """Test license detection fallback to MIT."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=False):
            assert detect_license() == "MIT"

    @patch('pathlib.Path.cwd')
    def test_detect_description_from_package_json(self, mock_cwd):
        """Test description detection from package.json."""
        mock_cwd.return_value = Path("/fake/path")

        package_json_data = {"description": "A great package for testing"}
        with patch("pathlib.Path.exists", side_effect=lambda: self._mock_exists("package.json")), \
             patch("builtins.open", mock_open(read_data=json.dumps(package_json_data))):
            assert detect_description() == "A great package for testing"

    @patch('pathlib.Path.cwd')
    def test_detect_description_from_setup_py(self, mock_cwd):
        """Test description detection from setup.py."""
        mock_cwd.return_value = Path("/fake/path")

        setup_py_content = '''
from setuptools import setup
setup(
    name="test-package",
    description="A package from setup.py",
    version="1.0.0"
)
'''
        with patch("pathlib.Path.exists", side_effect=lambda: self._mock_exists("setup.py")), \
             patch("pathlib.Path.read_text", return_value=setup_py_content):
            assert detect_description() == "A package from setup.py"

    @patch('pathlib.Path.cwd')
    def test_detect_description_fallback(self, mock_cwd):
        """Test description detection fallback."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=False):
            assert detect_description() == "A brief description of your project"

    @patch('pathlib.Path.cwd')
    def test_detect_features_from_package_json(self, mock_cwd):
        """Test feature detection from package.json keywords."""
        mock_cwd.return_value = Path("/fake/path")

        package_json_data = {"keywords": ["testing", "automation"]}
        with patch("pathlib.Path.exists", side_effect=self._mock_exists), \
             patch("builtins.open", mock_open(read_data=json.dumps(package_json_data))):
            features = detect_features()
            assert "Supports testing" in features
            assert "Supports automation" in features

    @patch('pathlib.Path.cwd')
    def test_detect_features_from_project_structure(self, mock_cwd):
        """Test feature detection from project structure."""
        mock_cwd.return_value = Path("/fake/path")

        def mock_exists(path):
            return str(path) in ["/fake/path/tests", "/fake/path/docs", "/fake/path/Dockerfile"]

        with patch("pathlib.Path.exists", side_effect=mock_exists):
            features = detect_features()
            assert "Well tested" in features
            assert "Comprehensive documentation" in features
            assert "Docker support" in features

    @patch('pathlib.Path.cwd')
    def test_detect_features_fallback(self, mock_cwd):
        """Test feature detection fallback."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.exists", return_value=False):
            features = detect_features()
            assert "Easy to use" in features
            assert "Well documented" in features
            assert "Actively maintained" in features

    @patch('pathlib.Path.cwd')
    def test_suggest_template_minimal(self, mock_cwd):
        """Test template suggestion for minimal projects."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.exists", return_value=False):
            assert suggest_template() == "minimal"

    @patch('pathlib.Path.cwd')
    def test_suggest_template_standard(self, mock_cwd):
        """Test template suggestion for standard projects."""
        mock_cwd.return_value = Path("/fake/path")

        def mock_glob(pattern):
            # Simulate 10 Python files
            if pattern == "**/*.py":
                return [f"file{i}.py" for i in range(10)]
            return []

        with patch("pathlib.Path.glob", side_effect=mock_glob), \
             patch("pathlib.Path.exists", return_value=False):
            assert suggest_template() == "standard"

    @patch('pathlib.Path.cwd')
    def test_suggest_template_fancy(self, mock_cwd):
        """Test template suggestion for fancy projects."""
        mock_cwd.return_value = Path("/fake/path")

        def mock_glob(pattern):
            # Simulate many files and advanced features
            if any(ext in pattern for ext in ['.py', '.js', '.rs', '.go', '.java']):
                return [f"file{i}{pattern[-3:]}" for i in range(30)]
            return []

        with patch("pathlib.Path.glob", side_effect=mock_glob), \
             patch("pathlib.Path.exists", return_value=True):  # CI, Docker, docs exist
            assert suggest_template() == "fancy"

    def test_get_feature_suggestions_python(self):
        """Test feature suggestions for Python projects."""
        suggestions = get_feature_suggestions("python")
        assert len(suggestions) >= 5
        assert any("Python" in suggestion for suggestion in suggestions)
        assert any("pip" in suggestion for suggestion in suggestions)

    def test_get_feature_suggestions_javascript(self):
        """Test feature suggestions for JavaScript projects."""
        suggestions = get_feature_suggestions("javascript")
        assert len(suggestions) >= 5
        assert any("JavaScript" in suggestion for suggestion in suggestions)
        assert any("NPM" in suggestion for suggestion in suggestions)

    def test_get_feature_suggestions_unknown(self):
        """Test feature suggestions for unknown project types."""
        suggestions = get_feature_suggestions("unknown")
        generic_suggestions = get_feature_suggestions("generic")
        assert suggestions == generic_suggestions

    @patch('pathlib.Path.cwd')
    def test_get_smart_defaults(self, mock_cwd):
        """Test smart defaults generation."""
        mock_cwd.return_value = Path("/fake/path")

        with patch("readme_generator.cli.detect_description", return_value="Test description"), \
             patch("readme_generator.cli.detect_license", return_value="MIT"), \
             patch("readme_generator.cli.detect_features", return_value=["Feature 1"]), \
             patch("readme_generator.cli.suggest_template", return_value="standard"):

            defaults = get_smart_defaults()

            assert defaults["project_name"] == "fake"
            assert defaults["description"] == "Test description"
            assert defaults["license"] == "MIT"
            assert defaults["features"] == ["Feature 1"]
            assert defaults["template"] == "standard"
            assert not defaults["ai_enabled"]
            assert not defaults["github_enabled"]

    def test_detect_project_type_javascript(self):
        """Test project type detection for JavaScript."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "package.json").write_text("{}")

            assert detect_project_type(temp_path) == "javascript"

    def test_detect_project_type_python(self):
        """Test project type detection for Python."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "pyproject.toml").write_text("")

            assert detect_project_type(temp_path) == "python"

    def test_detect_project_type_rust(self):
        """Test project type detection for Rust."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "Cargo.toml").write_text("")

            assert detect_project_type(temp_path) == "rust"

    def test_detect_project_type_go(self):
        """Test project type detection for Go."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "go.mod").write_text("")

            assert detect_project_type(temp_path) == "go"

    def test_detect_project_type_java(self):
        """Test project type detection for Java."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "pom.xml").write_text("")

            assert detect_project_type(temp_path) == "java"

    def test_detect_project_type_generic(self):
        """Test project type detection fallback to generic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            assert detect_project_type(temp_path) == "generic"


class TestGenerator:
    """Test cases for the README generator."""
    
    def test_prepare_template_context(self):
        """Test template context preparation."""
        project_info = {
            "project_name": "Test Project",
            "description": "A test project",
            "features": ["Feature 1", "Feature 2"],
            "usage_example": "python main.py",
            "license": "MIT"
        }
        
        context = prepare_template_context(
            project_info, ai_enabled=False, github_enabled=False
        )
        
        assert context["project_name"] == "Test Project"
        assert context["description"] == "A test project"
        assert context["features"] == ["Feature 1", "Feature 2"]
        assert context["usage_example"] == "python main.py"
        assert context["license"] == "MIT"
        assert not context["ai_enabled"]
        assert not context["github_enabled"]
    
    def test_render_minimal_template(self):
        """Test rendering the minimal template."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for README generation",
            "features": ["Feature 1", "Feature 2"],
            "usage_example": "python main.py",
            "license": "MIT"
        }
        
        rendered = render_template("minimal", context)
        
        assert rendered is not None
        assert "# Test Project" in rendered
        assert "A test project for README generation" in rendered
        assert "## Features" in rendered
        assert "- Feature 1" in rendered
        assert "- Feature 2" in rendered
        assert "## Usage" in rendered
        assert "python main.py" in rendered
        assert "## License" in rendered
        assert "MIT" in rendered
    
    def test_render_standard_template(self):
        """Test rendering the standard template."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for README generation",
            "features": ["Feature 1", "Feature 2"],
            "usage_example": "python main.py",
            "license": "MIT"
        }
        
        rendered = render_template("standard", context)
        
        assert rendered is not None
        assert "# Test Project" in rendered
        assert "## Table of Contents" in rendered
        assert "## Features" in rendered
        assert "## Installation" in rendered
        assert "## Usage" in rendered
        assert "## Contributing" in rendered
        assert "## License" in rendered
    
    def test_render_fancy_template(self):
        """Test rendering the fancy template."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for README generation",
            "features": ["Feature 1", "Feature 2"],
            "usage_example": "python main.py",
            "license": "MIT",
            "github_enabled": True,
            "github_url": "https://github.com/username/test-project"
        }
        
        rendered = render_template("fancy", context)
        
        assert rendered is not None
        assert "# Test Project" in rendered
        assert "## ✨ Features" in rendered
        assert "## 🚀 Quick Start" in rendered
        assert "## 🛠️ Installation" in rendered
        assert "## 💻 Usage" in rendered
        assert "## 🧪 Testing" in rendered
        assert "## 🤝 Contributing" in rendered
        assert "## 📜 License" in rendered
    
    def test_generate_readme_to_file(self):
        """Test generating a README file."""
        project_info = {
            "project_name": "Test Project",
            "description": "A test project for README generation",
            "template": "minimal",
            "features": ["Feature 1", "Feature 2"],
            "usage_example": "python main.py",
            "license": "MIT"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "README.md"
            
            success = generate_readme(
                project_info=project_info,
                template_name="minimal",
                output_path=output_path,
                ai_enabled=False,
                github_enabled=False
            )
            
            assert success is True
            assert output_path.exists()
            
            content = output_path.read_text()
            assert "# Test Project" in content
            assert "A test project for README generation" in content
            assert "## Features" in content
    
    def test_invalid_template(self):
        """Test handling of invalid template."""
        context = {
            "project_name": "Test Project",
            "description": "A test project"
        }
        
        rendered = render_template("nonexistent", context)
        assert rendered is None
    
    def test_empty_project_info(self):
        """Test handling of empty project info."""
        project_info = {}
        
        context = prepare_template_context(project_info)
        
        assert context["project_name"] == ""
        assert context["description"] == ""
        assert context["features"] == []
        assert context["usage_example"] == ""
        assert context["license"] == ""


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_smart_defaults_integration(self):
        """Test that smart defaults work together end-to-end."""
        # This tests the integration of all detection functions
        defaults = get_smart_defaults()

        # Verify all expected keys are present
        expected_keys = ["project_name", "description", "template", "license", "features", "ai_enabled", "github_enabled"]
        for key in expected_keys:
            assert key in defaults

        # Verify data types
        assert isinstance(defaults["project_name"], str)
        assert isinstance(defaults["description"], str)
        assert isinstance(defaults["template"], str)
        assert isinstance(defaults["license"], str)
        assert isinstance(defaults["features"], list)
        assert isinstance(defaults["ai_enabled"], bool)
        assert isinstance(defaults["github_enabled"], bool)

        # Verify reasonable defaults
        assert defaults["template"] in ["minimal", "standard", "fancy"]
        assert len(defaults["description"]) > 0
        assert len(defaults["features"]) >= 3  # Should have fallback features

    def test_template_rendering_with_detected_data(self):
        """Test that templates render correctly with detected data."""
        # Create realistic project info using smart defaults
        defaults = get_smart_defaults()

        # Prepare context as the generator would
        context = prepare_template_context({
            "project_name": defaults["project_name"],
            "description": defaults["description"],
            "features": defaults["features"],
            "usage_example": "",
            "license": defaults["license"]
        })

        # Test that all templates can render with this context
        for template_name in ["minimal", "standard", "fancy"]:
            rendered = render_template(template_name, context)
            assert rendered is not None
            assert len(rendered) > 100  # Should be substantial content
            assert defaults["project_name"] in rendered
            assert "## Features" in rendered

    def test_project_type_detection_integration(self):
        """Test project type detection works with real project structures."""
        # Test different project types
        test_cases = [
            ("package.json", "javascript"),
            ("pyproject.toml", "python"),
            ("Cargo.toml", "rust"),
            ("go.mod", "go"),
            ("pom.xml", "java"),
        ]

        for filename, expected_type in test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                (temp_path / filename).write_text("{}")  # Minimal valid file

                detected_type = detect_project_type(temp_path)
                assert detected_type == expected_type, f"Expected {expected_type} for {filename}, got {detected_type}"

                # Clean up for next test
                (temp_path / filename).unlink()
