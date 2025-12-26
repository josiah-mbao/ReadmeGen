# ReadmeGen Documentation

Minimal documentation focused on getting started quickly.

## Quick Start

### Installation
```bash
pip install readmegen-oss
```

### Basic Usage
```bash
# Initialize a new project (recommended)
readmegen init

# Generate README with options
readmegen generate --name "My Project" --description "A great project"

# List available templates
readmegen templates
```

## CLI Commands

### `readmegen init`
Initialize a new project with interactive prompts.

**What it does:**
- Prompts for project name (auto-detected from directory)
- Shows template previews before selection
- Asks for license, features, usage examples
- Generates professional README in 60 seconds

**Example:**
```bash
$ readmegen init
🚀 ReadmeGen 🚀
Let's set up your project with a professional README!

Project Name: [MyProject] (auto-detected)
Select Template: ▸ Minimal  Standard  Fancy
Choose License: ▸ MIT  Apache  GPL  BSD
Enable AI enhancements? No ▸ Yes
Enable GitHub metadata? No ▸ Yes

Generating README... ⠏ Setting up project info
✅ README.md created successfully!
📁 README.md has been created
```

### `readmegen generate`
Generate README with command-line options.

**Options:**
- `--name, -n`: Project name (auto-detected from directory)
- `--description, -d`: Project description
- `--template, -t`: Template (minimal, standard, fancy) - default: standard
- `--output, -o`: Output file path - default: README.md
- `--ai`: Enable AI content enhancement (optional)
- `--github`: Enable GitHub metadata fetching (optional)
- `--force, -f`: Overwrite existing README.md

**Examples:**
```bash
# Generate with specific options
readmegen generate --name "My Project" --description "A great project" --template standard

# Generate with AI enhancement
readmegen generate --name "My AI Project" --ai

# Generate to custom location
readmegen generate --output docs/README.md
```

### `readmegen templates`
List available README templates with previews.

**Example:**
```bash
$ readmegen templates

Available Templates:

• minimal: A clean, minimal README with essential sections only
  Preview: # Project Name

Brief description

## Features
- Feature 1
-...

• standard: A comprehensive README with all common sections
  Preview: # Project Name

Brief description

## Table of Contents
## F...

• fancy: A rich README with badges, tables, and advanced formatting
  Preview: # Project Name

[![Badge]]()

Brief description

## ✨ Featur...
```

## Templates

### Minimal
Perfect for simple projects that need just the essentials.

**Sections:** Project title, description, features, usage, license

### Standard
Comprehensive template with all common sections.

**Sections:** Table of contents, features, installation, usage, contributing, license

### Fancy
Rich template with badges, tables, and advanced formatting.

**Sections:** Badges, emojis, detailed sections, professional formatting

## Error Handling

ReadmeGen provides clear error messages for common issues:

- **File Error**: Template files not found → Check templates/ directory
- **Permission Error**: Cannot write to output file → Check file permissions
- **Input Error**: Invalid input provided → Check your input and try again
- **Configuration Error**: Missing template → System configuration issue

For debugging, use `--debug` or `-v` flags to see full tracebacks.

## Troubleshooting

### "Template files not found"
Make sure you installed ReadmeGen properly:
```bash
pip install readmegen
```

### "Cannot write to output file"
Check file permissions in your project directory.

### "Invalid input provided"
Ensure project names contain only alphanumeric characters, spaces, hyphens, or underscores.

### Need Help?
- Check this documentation
- Run `readmegen --help` for CLI reference
- Report issues at https://github.com/your-username/ReadmeGen/issues

## Next Steps

After generating your README:
1. Review the generated content
2. Customize sections as needed
3. Add project-specific details
4. Commit the README to your repository

That's it! You now have a professional README for your project.
