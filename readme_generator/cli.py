"""
CLI interface for the AI-Powered GitHub README Generator.

This module provides the command-line interface using typer, with interactive
prompts for project details and template selection.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax
import questionary
import traceback
import sys

from .generator import generate_readme, detect_project_type
from .templates import get_available_templates, get_template_description
from .utils import validate_project_name, validate_description

app = typer.Typer(
    help="AI-Powered GitHub README Generator", rich_markup_mode="rich"
)


console = Console()


def handle_error(error: Exception, context: str = "operation"):
    """Handle errors with clear, user-friendly messages."""
    error_type = type(error).__name__
    
    # Provide specific error messages for common issues
    if isinstance(error, FileNotFoundError):
        console.print("[red]❌ File Error:[/red] Template files not found")
        console.print("💡 Check templates/ directory exists")
    elif isinstance(error, PermissionError):
        console.print("[red]❌ Permission Error:[/red] Cannot write to output file")
        console.print("💡 Check file permissions and try again")
    elif isinstance(error, ValueError):
        console.print("[red]❌ Input Error:[/red] Invalid input provided")
        console.print("💡 Please check your input and try again")
    elif isinstance(error, KeyError):
        console.print("[red]❌ Configuration Error:[/red] Missing template")
        console.print("💡 This appears to be a system configuration issue")
    else:
        # Generic error with context
        console.print(f"[red]❌ {context.title()} Failed:[/red] {error}")
        console.print(f"💡 {context} could not be completed due to an unexpected error")
    
    console.print("\n🔧 Debug Info:")
    console.print(f"   Error Type: {error_type}")
    console.print(f"   Context: {context}")
    
    # For development/debugging, show full traceback
    if "--debug" in sys.argv or "-v" in sys.argv:
        console.print("\n🐛 Full Traceback:")
        console.print(Syntax(traceback.format_exc(), "python", theme="monokai"))
    
    console.print("\n💡 If this problem persists, please report it at:")
    console.print("   https://github.com/your-username/ReadmeGen/issues")
    
    raise typer.Exit(code=1)

# Enhanced template previews with rich formatting and real examples
TEMPLATE_PREVIEWS = {
    "minimal": {
        "title": "🎯 Minimal",
        "description": "Clean and simple - perfect for basic projects",
        "includes": ["Title", "Description", "Features", "Installation", "Usage", "License"],
        "preview": """# MyProject

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A simple and elegant solution for everyday tasks.

## Installation

```bash
pip install myproject
```

## Features

- Easy to use
- Lightweight and fast
- Well documented

## Usage

```python
from myproject import main
main()
```

## License

This project is licensed under the MIT License.""",
        "best_for": "Tiny libraries, simple scripts, proof-of-concepts"
    },
    "standard": {
        "title": "📋 Standard",
        "description": "Professional and comprehensive - the sweet spot",
        "includes": ["Title + Badge", "TOC", "Prerequisites", "Installation", "Features", "Usage", "Contributing", "License"],
        "preview": """# MyProject

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A comprehensive solution with professional documentation and testing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

```bash
pip install myproject
```

## Features

- Comprehensive feature set
- Easy to use interface
- Well documented
- Actively maintained

## Usage

```python
from myproject import main
main()
```

## Contributing

We welcome contributions! See CONTRIBUTING.md for details.

## License

This project is licensed under the MIT License.""",
        "best_for": "Most projects, libraries, web apps, CLIs"
    },
    "fancy": {
        "title": "✨ Fancy",
        "description": "Rich and polished - for serious, professional projects",
        "includes": ["Badges", "TOC", "Prerequisites", "Installation", "Features", "Quick Start", "Usage", "Testing", "Contributing", "Support", "License"],
        "preview": """# MyProject

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

A powerful, enterprise-ready solution with comprehensive documentation.

## Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Installation](#️-installation)
- [💻 Usage](#-usage)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

## ✨ Features

- 🚀 **Fast**: Optimized performance
- 📦 **Modular**: Clean architecture
- 🧪 **Tested**: Comprehensive test suite
- 📖 **Documented**: Extensive docs

## 🚀 Quick Start

```bash
pip install myproject
python -c "import myproject; myproject.run()"
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### From PyPI
```bash
pip install myproject
```

## 💻 Usage

```python
from myproject import MyProject

app = MyProject()
app.run()
```

## 🤝 Contributing

We love contributions! See CONTRIBUTING.md for guidelines.

## 📜 License

Licensed under MIT License.""",
        "best_for": "Large projects, enterprise software, frameworks"
    }
}


def detect_license():
    """Detect project license from common files."""
    cwd = Path.cwd()

    # Check for LICENSE file
    license_file = cwd / "LICENSE"
    if license_file.exists():
        content = license_file.read_text().lower()
        if "mit" in content:
            return "MIT"
        elif "apache" in content and "2.0" in content:
            return "Apache 2.0"
        elif "gpl" in content and "3.0" in content:
            return "GPL 3.0"
        elif "bsd" in content:
            return "BSD 3-Clause"

    # Check package.json for license field
    package_json = cwd / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                data = json.load(f)
                license_field = data.get("license", "").upper()
                if license_field in ["MIT", "APACHE-2.0", "GPL-3.0", "BSD-3-CLAUSE"]:
                    return license_field.replace("-", " ").replace("APACHE-2.0", "Apache 2.0").replace("GPL-3.0", "GPL 3.0").replace("BSD-3-CLAUSE", "BSD 3-Clause")
        except:
            pass

    return "MIT"  # Default fallback


def detect_description():
    """Detect project description from various sources."""
    cwd = Path.cwd()

    # Check package.json
    package_json = cwd / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                data = json.load(f)
                desc = data.get("description")
                if desc and len(desc) > 10:
                    return desc
        except:
            pass

    # Check setup.py
    setup_py = cwd / "setup.py"
    if setup_py.exists():
        content = setup_py.read_text()
        # Look for description= in setup.py
        import re
        match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            desc = match.group(1)
            if len(desc) > 10:
                return desc

    # Check README.md first paragraph
    readme = cwd / "README.md"
    if readme.exists():
        content = readme.read_text()
        # Get first paragraph after title
        lines = content.split('\n')
        description_lines = []
        in_description = False
        for line in lines[1:]:  # Skip title
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('[') and not line.startswith('!'):
                description_lines.append(line)
                in_description = True
            elif in_description and not line:
                break
            elif in_description:
                break

        desc = ' '.join(description_lines).strip()
        if desc and len(desc) > 10 and len(desc) < 200:
            return desc

    return "A brief description of your project"


def detect_features():
    """Detect project features from various sources."""
    cwd = Path.cwd()
    features = []

    # Check package.json keywords
    package_json = cwd / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                data = json.load(f)
                keywords = data.get("keywords", [])
                if keywords:
                    # Convert keywords to feature statements
                    for keyword in keywords[:3]:  # Limit to 3
                        features.append(f"Supports {keyword}")
        except:
            pass

    # Check for common project patterns
    if (cwd / "tests").exists() or (cwd / "test").exists():
        features.append("Well tested")

    if (cwd / "docs").exists() or (cwd / "doc").exists():
        features.append("Comprehensive documentation")

    if (cwd / "examples").exists() or (cwd / "example").exists():
        features.append("Includes examples")

    if (cwd / "Dockerfile").exists():
        features.append("Docker support")

    if (cwd / ".github" / "workflows").exists():
        features.append("CI/CD integration")

    # If no features detected, provide generic ones
    if not features:
        features = ["Easy to use", "Well documented", "Actively maintained"]

    return features[:5]  # Limit to 5 features


def suggest_template():
    """Suggest appropriate template based on project characteristics."""
    cwd = Path.cwd()

    # Count source files
    source_files = 0
    for ext in ['.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp', '.c']:
        source_files += len(list(cwd.glob(f'**/*{ext}')))

    # Check for advanced project features
    has_ci = (cwd / ".github" / "workflows").exists()
    has_docker = (cwd / "Dockerfile").exists()
    has_docs = (cwd / "docs").exists()
    has_tests = (cwd / "tests").exists() or (cwd / "test").exists()
    has_contributing = (cwd / "CONTRIBUTING.md").exists()

    advanced_features = sum([has_ci, has_docker, has_docs, has_tests, has_contributing])

    # Template logic
    if source_files < 5 and advanced_features < 2:
        return "minimal"
    elif source_files < 20 and advanced_features < 4:
        return "standard"
    else:
        return "fancy"


def get_feature_suggestions(project_type: str) -> list:
    """Get project-type-specific feature suggestions."""
    suggestions = {
        "javascript": [
            "Fast and lightweight",
            "Browser and Node.js compatible",
            "ES6+ modern JavaScript",
            "NPM package ready",
            "TypeScript support optional",
            "React/Vue/Angular compatible",
            "Webpack/Rollup build tools",
            "Jest testing framework",
            "ESLint code quality",
            "Modular architecture"
        ],
        "python": [
            "Python 3.8+ compatible",
            "Pip package ready",
            "Comprehensive documentation",
            "Type hints included",
            "Async/await support",
            "Cross-platform compatibility",
            "Virtual environment ready",
            "pytest testing framework",
            "Black code formatting",
            "Comprehensive error handling"
        ],
        "rust": [
            "Memory safe and fast",
            "Zero-cost abstractions",
            "Cargo package manager",
            "Cross-platform compilation",
            "Comprehensive testing",
            "Documentation generation",
            "Benchmarking support",
            "No runtime overhead",
            "Thread safety guaranteed",
            "WebAssembly compatible"
        ],
        "go": [
            "Compiled and fast",
            "Simple and readable",
            "Cross-platform binaries",
            "Built-in concurrency",
            "Strong static typing",
            "Excellent testing support",
            "Go modules support",
            "Fast compilation",
            "Docker container ready",
            "Microservices friendly"
        ],
        "java": [
            "JVM compatible",
            "Maven/Gradle build tools",
            "Spring Boot ready",
            "Comprehensive testing",
            "Enterprise grade",
            "Multi-threading support",
            "JPA/Hibernate integration",
            "REST API capable",
            "Docker containerization",
            "Cloud deployment ready"
        ],
        "generic": [
            "Easy to use",
            "Well documented",
            "Cross-platform",
            "Actively maintained",
            "Open source",
            "Community supported",
            "Regular updates",
            "Issue tracking",
            "Feature requests welcome",
            "Contributing guidelines"
        ]
    }

    return suggestions.get(project_type, suggestions["generic"])


def get_smart_defaults():
    """Get enhanced smart defaults with auto-detection."""
    return {
        "project_name": Path.cwd().name,
        "description": detect_description(),
        "template": suggest_template(),
        "license": detect_license(),
        "features": detect_features(),
        "ai_enabled": False,
        "github_enabled": False
    }

@app.command()
def generate(
    project_name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Project name"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Project description"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template to use (minimal, standard, fancy)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (default: README.md)"
    ),
    ai_enabled: bool = typer.Option(False, "--ai", help="Enable AI content enhancement"),
    github_enabled: bool = typer.Option(
        False, "--github", help="Enable GitHub metadata fetching"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing README.md file")
):
    """
    Generate a professional README file for your project.
    
    Interactive prompts will guide you through the process if options are not provided.
    """
    
    # Show welcome message with ASCII art
    console.print(Panel.fit(
        "[bold magenta]ReadmeGen 🚀[/bold magenta]\n"
        "Zero-friction README generation for developers",
        border_style="magenta"
    ))
    
    # Collect project information with smart defaults
    defaults = get_smart_defaults()
    
    # Use provided values or smart defaults
    if not project_name:
        project_name = defaults["project_name"]
    if not template:
        template = defaults["template"]
    
    project_info = collect_project_info(
        project_name=project_name,
        description=description,
        template=template
    )
    
    # Set output path
    if output is None:
        output = Path("README.md")
    
    # Check if file exists and handle overwrite
    if output.exists() and not force:
        if not Confirm.ask("README.md already exists. Overwrite?", default=False):
            console.print("[yellow]Generation cancelled.[/yellow]")
            raise typer.Exit()
    
    # Generate README with progress tracking
    try:
        steps = ["Setting up project info", "Rendering template", "Writing README.md"]

        with console.status("[bold green]Generating README...") as status:
            for step in steps:
                status.update(
                    f"[bold green]Generating README...[/bold green] [dim]({step})[/dim]"
                )
                # Small delay to show progress
                import time

                time.sleep(0.1)
        
        generate_readme(
            project_info=project_info,
            template_name=project_info["template"],
            output_path=output,
            ai_enabled=ai_enabled,
            github_enabled=github_enabled,
        )
        
        console.print("\n[green]✅ README generated successfully![/green]")
        console.print(f"📁 Output: {output.absolute()}")

        if ai_enabled:
            console.print("🤖 AI content enhancement was enabled")
        if github_enabled:
            console.print("🔗 GitHub metadata fetching was enabled")
            
    except Exception as e:
        console.print(f"[red]❌ Error generating README: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def templates():
    """List available README templates with rich previews."""
    available_templates = get_available_templates()

    console.print("\n[bold blue]🎨 Available README Templates[/bold blue]")
    console.print("[dim]Choose the perfect template for your project:[/dim]\n")

    for template_name in available_templates:
        if template_name not in TEMPLATE_PREVIEWS:
            continue

        template_data = TEMPLATE_PREVIEWS[template_name]

        # Create a rich panel for each template
        panel_content = f"""[bold cyan]{template_data['title']}[/bold cyan]
[dim]{template_data['description']}[/dim]

[bold yellow]📋 Includes:[/bold yellow] {', '.join(template_data['includes'])}

[bold yellow]🎯 Best for:[/bold yellow] {template_data['best_for']}
"""

        # Add preview panel
        preview_panel = Panel(
            Syntax(template_data['preview'], "markdown", theme="github-dark", word_wrap=True),
            title=f"[bold]{template_name.title()} Template Preview[/bold]",
            border_style="blue",
            padding=(1, 2)
        )

        # Main template panel
        main_panel = Panel(
            panel_content,
            title=f"[bold]{template_name.title()}[/bold]",
            border_style="green",
            padding=(1, 2)
        )

        console.print(main_panel)
        console.print(preview_panel)
        console.print()  # Spacing between templates

    console.print("[dim]💡 Tip: Templates are auto-suggested based on your project structure![/dim]\n")

@app.command()
def init():
    """Initialize a new project with a README using interactive prompts."""
    console.print(Panel.fit(
        "[bold magenta]ReadmeGen 🚀[/bold magenta]\n"
        "Let's set up your project with a professional README!",
        border_style="magenta"
    ))

    # Collect project information interactively
    project_info = collect_project_info_interactive()

    # === STEP 4: GENERATION ===
    def show_progress(step: int, description: str):
        """Display progress indicator."""
        progress_bar = "█" * step + "░" * (4 - step)
        console.print(f"\n[dim][{progress_bar}] Step {step}/4: {description}[/dim]\n")

    show_progress(4, "Generating your README")

    # Generate README
    try:
        generate_readme(
            project_info=project_info,
            template_name=project_info["template"],
            output_path=Path("README.md"),
            ai_enabled=project_info.get("ai_enabled", False),
            github_enabled=project_info.get("github_enabled", False)
        )

        console.print("\n[green]✅ Project initialized successfully![/green]")
        console.print("📁 README.md has been created")
        console.print("\n💡 Tip: Use 'readmegen generate --ai' to enhance your README with AI!")

    except Exception as e:
        console.print(f"[red]❌ Error initializing project: {e}[/red]")
        raise typer.Exit(code=1)

def collect_project_info_interactive() -> dict:
    """Collect project information through two-tier interactive flow with progress indicators."""
    defaults = get_smart_defaults()

    console.print("\n[bold blue]🚀 Let's create your README![/bold blue]")
    console.print("[dim]I'll guide you through setup with smart defaults pre-filled.[/dim]\n")

    # Progress tracking
    total_steps = 4
    current_step = 1

    def show_progress(step: int, description: str):
        """Display progress indicator."""
        progress_bar = "█" * step + "░" * (total_steps - step)
        console.print(f"\n[dim][{progress_bar}] Step {step}/{total_steps}: {description}[/dim]\n")

    # === STEP 1: PROJECT ANALYSIS ===
    show_progress(1, "Analyzing your project")
    console.print("🔍 [bold]Project Analysis Complete![/bold]")
    console.print("I've detected your project details:\n")

    # Show detected defaults
    console.print(f"📁 [bold]Project:[/bold] {defaults['project_name']}")
    console.print(f"📝 [bold]Description:[/bold] {defaults['description']}")
    console.print(f"🎨 [bold]Suggested Template:[/bold] {defaults['template']}")
    console.print(f"📄 [bold]Detected License:[/bold] {defaults['license']}")
    console.print(f"✨ [bold]Auto-detected Features:[/bold] {', '.join(defaults['features'][:3])}{'...' if len(defaults['features']) > 3 else ''}")

    # === STEP 2: BASIC SETUP TIER ===
    show_progress(2, "Basic configuration")
    console.print("[bold cyan]📋 BASIC SETUP[/bold cyan]")
    console.print("These essentials are auto-detected for your convenience:\n")

    # Show detected defaults
    console.print(f"📁 [bold]Project:[/bold] {defaults['project_name']}")
    console.print(f"📝 [bold]Description:[/bold] {defaults['description']}")
    console.print(f"🎨 [bold]Template:[/bold] {defaults['template']} [dim](auto-suggested)[/dim]")
    console.print(f"📄 [bold]License:[/bold] {defaults['license']} [dim](auto-detected)[/dim]")

    # Quick accept for basic setup
    use_basic_defaults = questionary.confirm(
        "\n✅ Use these basic settings?", default=True
    ).ask()

    if use_basic_defaults:
        project_name = defaults["project_name"]
        description = defaults["description"]
        template = defaults["template"]
        license_choice = defaults["license"]
        console.print("\n[green]✓ Basic setup complete![/green]")
    else:
        console.print("\n[blue]Let's customize the basics:[/blue]\n")

        # Project name with smart default
        project_name_input = questionary.text(
            "Project Name:",
            default=defaults["project_name"],
            validate=lambda x: validate_project_name(x) or "Invalid project name",
        ).ask()
        project_name = project_name_input or defaults["project_name"]

        # Project description with smart default
        description_input = questionary.text(
            "Brief project description:",
            default=defaults["description"],
            validate=lambda x: validate_description(x) or "Description cannot be empty",
        ).ask()
        description = description_input or defaults["description"]

        # Template selection with smart default
        available_templates = get_available_templates()
        template_choices = [
            questionary.Choice("Minimal - Basic sections only", value="minimal"),
            questionary.Choice("Standard - Full professional README", value="standard"),
            questionary.Choice("Fancy - Rich formatting + badges", value="fancy"),
        ]

        template = questionary.select(
            "Choose a template:",
            choices=template_choices,
            default=defaults["template"]
        ).ask()

        # License selection with smart default
        license_choices = [
            questionary.Choice("MIT - Permissive (most common)", value="MIT"),
            questionary.Choice("Apache 2.0 - Business-friendly", value="Apache 2.0"),
            questionary.Choice("GPL 3.0 - Copyleft protection", value="GPL 3.0"),
            questionary.Choice("BSD 3-Clause - Simple permissive", value="BSD 3-Clause"),
            questionary.Choice("None - No license", value=None),
        ]

        license_choice = questionary.select(
            "Choose a license:",
            choices=license_choices,
            default=defaults["license"]
        ).ask()

    # === STEP 3: ADVANCED SETUP TIER ===
    show_progress(3, "Advanced options")
    console.print("[bold cyan]⚡ ADVANCED SETUP[/bold cyan]")
    console.print("[dim]Optional enhancements (skip for quick setup):[/dim]\n")

    # Show auto-detected features
    console.print(f"✨ [bold]Features auto-detected:[/bold] {', '.join(defaults['features'][:3])}{'...' if len(defaults['features']) > 3 else ''}")

    # Ask if user wants to customize advanced options
    customize_advanced = questionary.confirm(
        "\n🔧 Customize advanced options?", default=False
    ).ask()

    if customize_advanced:
        console.print("\n[blue]Advanced customization:[/blue]\n")

        # Features customization with improved UX
        features = defaults["features"]
        console.print(f"Current features: {', '.join(features)}")

        feature_action = questionary.select(
            "How would you like to modify features?",
            choices=[
                questionary.Choice("✅ Keep auto-detected features", value="keep"),
                questionary.Choice("➕ Add to auto-detected features", value="add"),
                questionary.Choice("📝 Replace with custom features", value="replace"),
                questionary.Choice("🎯 Choose from suggestions", value="suggest"),
            ],
            default="keep"
        ).ask()

        if feature_action == "add":
            console.print("\nAdd additional features (one per line, press Enter twice when done):")
            additional_features = []
            while True:
                feature_input = questionary.text("Additional feature:").ask()
                if not feature_input:
                    break
                additional_features.append(feature_input.strip())
            features.extend([f for f in additional_features if f])

        elif feature_action == "replace":
            console.print("\nEnter custom features (one per line, press Enter twice when done):")
            features = []
            while True:
                feature_input = questionary.text("Feature:").ask()
                if not feature_input:
                    break
                features.append(feature_input.strip())
            features = [f for f in features if f] or defaults["features"]  # Fallback

        elif feature_action == "suggest":
            # Project-type-specific feature suggestions
            project_type = detect_project_type(Path.cwd())
            suggested_features = get_feature_suggestions(project_type)

            console.print(f"\nSuggested features for {project_type} projects:")
            selected_suggestions = questionary.checkbox(
                "Select features to include:",
                choices=[questionary.Choice(feat, checked=True) for feat in suggested_features[:8]]
            ).ask()

            if selected_suggestions:
                features = selected_suggestions
                # Allow adding custom features too
                add_custom = questionary.confirm("Add any custom features?", default=False).ask()
                if add_custom:
                    console.print("Add custom features (one per line, press Enter twice when done):")
                    custom_features = []
                    while True:
                        feature_input = questionary.text("Custom feature:").ask()
                        if not feature_input:
                            break
                        custom_features.append(feature_input.strip())
                    features.extend([f for f in custom_features if f])
            else:
                features = defaults["features"]  # Fallback

        # elif feature_action == "keep": features remain as defaults

        # Usage example (optional)
        usage_example = ""
        add_usage = questionary.confirm("Add a usage example?", default=False).ask()
        if add_usage:
            usage_example = questionary.text("Usage example (code snippet):").ask() or ""

        # AI enhancement (de-emphasized)
        console.print("\n[dim]🤖 AI Enhancement (requires OpenAI API key)[/dim]")
        ai_enabled = questionary.confirm("Enable AI content enhancement?", default=False).ask()

        # GitHub metadata (de-emphasized)
        console.print("\n[dim]🔗 GitHub Integration (requires GitHub token)[/dim]")
        github_enabled = questionary.confirm("Enable GitHub metadata fetching?", default=False).ask()

    else:
        # Use all defaults for advanced options
        features = defaults["features"]
        usage_example = ""
        ai_enabled = False
        github_enabled = False
        console.print("\n[green]✓ Using smart defaults for advanced options![/green]")

    return {
        "project_name": project_name,
        "description": description,
        "template": template,
        "features": features,
        "usage_example": usage_example,
        "license": license_choice,
        "ai_enabled": ai_enabled,
        "github_enabled": github_enabled
    }


def collect_project_info(
    project_name: Optional[str] = None,
    description: Optional[str] = None,
    template: Optional[str] = None
) -> dict:
    """Collect project information - maintains backward compatibility with typer prompts."""
    
    # Use smart defaults when no values provided
    defaults = get_smart_defaults()
    if not project_name:
        project_name = defaults["project_name"]
    if not template:
        template = defaults["template"]

    # Project name validation
    while not validate_project_name(project_name):
        console.print(
            "[red]Invalid project name. Please use alphanumeric characters, "
            "spaces, hyphens, or underscores.[/red]"
        )
        project_name_input = questionary.text(
            "Project name:", default=project_name
        ).ask()
        project_name = project_name_input or project_name

    # Project description
    if not description:
        description = "A brief description of your project"

    while not validate_description(description):
        console.print("[red]Description cannot be empty.[/red]")
        description_input = questionary.text(
            "Brief project description:", default=description
        ).ask()
        description = description_input or description
    
    # Template selection
    available_templates = get_available_templates()
    if template not in available_templates:
        template = defaults["template"]
    
    # Additional project details (minimal for backward compatibility)
    features = []
    usage_example = ""
    license_choice = defaults["license"]
    
    return {
        "project_name": project_name,
        "description": description,
        "template": template,
        "features": features,
        "usage_example": usage_example,
        "license": license_choice
    }

if __name__ == "__main__":
    app()
