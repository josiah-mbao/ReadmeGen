"""
CLI interface for the AI-Powered GitHub README Generator.

This module provides the command-line interface using typer, with interactive
prompts for project details and template selection.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from .generator import generate_readme
from .templates import get_available_templates, get_template_description
from .utils import validate_project_name, validate_description

app = typer.Typer(
    help="AI-Powered GitHub README Generator", rich_markup_mode="rich"
)


console = Console()

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
    
    # Show welcome message
    console.print(
        Panel.fit(
            "[bold blue]AI-Powered GitHub README Generator[/bold blue]\n"
            "Create professional README files in seconds!",
            border_style="blue",
        )
    )
    
    # Collect project information
    project_info = collect_project_info(project_name, description, template)
    
    # Set output path
    if output is None:
        output = Path("README.md")
    
    # Check if file exists and handle overwrite
    if output.exists() and not force:
        if not Confirm.ask("README.md already exists. Overwrite?", default=False):
            console.print("[yellow]Generation cancelled.[/yellow]")
            raise typer.Exit()
    
    # Generate README
    try:
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
    """List available README templates."""
    templates = get_available_templates()

    console.print("\n[bold]Available Templates:[/bold]\n")

    for template_name in templates:
        description = get_template_description(template_name)
        console.print(f"• [bold]{template_name}[/bold]: {description}")

@app.command()
def init():
    """Initialize a new project with a README."""
    console.print(
        Panel.fit(
            "[bold blue]Project Initialization[/bold blue]\n"
            "Let's set up your project with a professional README!",
            border_style="blue"
        )
    )
    
    # Collect project information interactively
    project_info = collect_project_info()
    
    # Generate README
    try:
        generate_readme(
            project_info=project_info,
            template_name=project_info["template"],
            output_path=Path("README.md"),
            ai_enabled=False,  # Start with basic generation
            github_enabled=False
        )
        
        console.print("\n[green]✅ Project initialized successfully![/green]")
        console.print("📁 README.md has been created")
        console.print("\n💡 Tip: Use 'readmegenerator generate --ai' to enhance your README with AI!")
        
    except Exception as e:
        console.print(f"[red]❌ Error initializing project: {e}[/red]")
        raise typer.Exit(code=1)

def collect_project_info(
    project_name: Optional[str] = None,
    description: Optional[str] = None,
    template: Optional[str] = None
) -> dict:
    """Collect project information through interactive prompts."""
    
    # Project name
    if not project_name:
        project_name = Prompt.ask("Project name", default=Path.cwd().name)

    while not validate_project_name(project_name):
        console.print(
            "[red]Invalid project name. Please use alphanumeric characters, "
            "spaces, hyphens, or underscores.[/red]"
        )
        project_name = Prompt.ask("Project name")

    # Project description
    if not description:
        description = Prompt.ask(
            "Brief project description", default="A brief description of your project"
        )

    while not validate_description(description):
        console.print("[red]Description cannot be empty.[/red]")
        description = Prompt.ask("Brief project description")
    
    # Template selection
    available_templates = get_available_templates()
    if not template:
        console.print(
            f"\nAvailable templates: {', '.join(available_templates)}"
        )
        template = Prompt.ask(
            "Template to use", choices=available_templates, default="standard"
        )
    
    # Additional project details
    features = []
    if Confirm.ask("Would you like to add project features?", default=True):
        while True:
            feature = Prompt.ask("Feature (or press Enter to skip)")
            if not feature:
                break
            features.append(feature)

    usage_example = ""
    if Confirm.ask("Would you like to add a usage example?", default=False):
        usage_example = Prompt.ask("Usage example")

    # License selection
    licenses = ["MIT", "Apache 2.0", "GPL 3.0", "BSD 3-Clause", "None"]
    license_choice = Prompt.ask("License", choices=licenses, default="MIT")
    
    return {
        "project_name": project_name,
        "description": description,
        "template": template,
        "features": features,
        "usage_example": usage_example,
        "license": license_choice if license_choice != "None" else None
    }

if __name__ == "__main__":
    app()
