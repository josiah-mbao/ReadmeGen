# AI-Powered GitHub README Generator

A Python CLI tool designed to streamline README creation for developers. Generate professional README files with template-driven generation and optional AI-assisted content enhancement.

## 🚀 Features

### MVP Features (Phase 1)
- **Interactive CLI**: Step-by-step prompts for project details
- **Template System**: Multiple README templates (minimal, standard, fancy) using Jinja2
- **Markdown Output**: Clean README.md ready for GitHub
- **Basic Feature Input**: Manual feature listing

### Phase 2 Enhancements
- **AI-assisted Content**: Expands short descriptions into detailed paragraphs
- **AI Feature Suggestion**: Suggests key project features if not provided
- **GitHub API Integration**: Automatically fetch repo details (URL, license, contributors)
- **Optional Live Markdown Preview**: Preview in CLI

### Phase 3 Advanced Features
- **Web UI**: Lightweight Flask/FastAPI interface for non-CLI users
- **Badge Auto-generation**: Build, license, coverage, or Python/Rust version badges
- **Multi-language Support**: Generate READMEs in multiple languages
- **GitHub Action Integration**: Auto-generate or update README on repo creation or commit
- **Custom AI Prompts/Templates**: Users can define custom content styles

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/ReadmeGen.git
cd ReadmeGen

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## 🎯 Usage

### Quick Start

#### 1. Initialize a New Project
```bash
readmegenerator init
```
This will guide you through an interactive setup to create a README for your project.

#### 2. Generate README with Options
```bash
readmegenerator generate --name "My Project" --description "A great project" --template standard
```

#### 3. List Available Templates
```bash
readmegenerator templates
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name, -n` | Project name | Current directory name |
| `--description, -d` | Project description | "A brief description" |
| `--template, -t` | Template to use (minimal, standard, fancy) | standard |
| `--output, -o` | Output file path | README.md |
| `--ai` | Enable AI content enhancement | false |
| `--github` | Enable GitHub metadata fetching | false |
| `--force, -f` | Overwrite existing README.md | false |

### Templates

#### Minimal Template
A clean, minimal README with essential sections only:
- Project title and description
- Features list
- Usage section
- License information

#### Standard Template
A comprehensive README with all common sections:
- Table of contents
- Features
- Installation instructions
- Usage examples
- Contributing guidelines
- License

#### Fancy Template
A rich README with badges, tables, and advanced formatting:
- GitHub badges and status indicators
- Detailed table of contents
- Advanced formatting with emojis
- Comprehensive documentation sections
- Support and acknowledgment sections

## 🧪 Examples

### Basic Usage
```bash
# Interactive setup
readmegenerator init

# Generate with specific options
readmegenerator generate \
  --name "Awesome Project" \
  --description "An awesome Python project" \
  --template fancy \
  --features "Feature 1" "Feature 2" "Feature 3"
```

### Advanced Usage with AI
```bash
# Enable AI content enhancement
readmegenerator generate \
  --name "My AI Project" \
  --description "A project using AI" \
  --ai \
  --github
```

## 🏗️ Project Structure

```
readme_generator/
├── readme_generator/            # Core package
│   ├── __init__.py
│   ├── cli.py                   # CLI interface and prompts
│   ├── generator.py             # Core logic to generate README from templates
│   ├── templates.py             # Manage available README templates
│   ├── ai.py                    # AI integration for description & feature enhancement
│   ├── github_api.py            # Optional: fetch repo metadata from GitHub
│   └── utils.py                 # Helper functions
├── templates/                   # Jinja2 README templates
│   ├── minimal.md.j2
│   ├── standard.md.j2
│   └── fancy.md.j2
├── tests/                       # Unit & integration tests
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_generator.py
```

## 🔧 Development

### Setting up Development Environment

1. **Clone and Install**
   ```bash
   git clone https://github.com/your-username/ReadmeGen.git
   cd ReadmeGen
   python -m venv venv
   source venv/bin/activate
   pip install -e .[dev]
   ```

2. **Code Style**
   ```bash
   # Format code with black
   black readme_generator/ tests/
   
   # Check code style with ruff
   ruff check readme_generator/ tests/
   ```

3. **Run Tests**
   ```bash
   pytest
   ```

### Adding New Templates

1. Create a new Jinja2 template in `templates/` directory
2. Add template description to `TEMPLATE_DESCRIPTIONS` in `templates.py`
3. Test the template with sample data

### Adding New Features

1. Implement the feature in the appropriate module
2. Add CLI options if needed in `cli.py`
3. Write tests in `tests/` directory
4. Update documentation

## 🤖 AI Integration (Future)

The AI integration will be implemented in Phase 2 and will include:

- **Content Enhancement**: Expand short descriptions into detailed paragraphs
- **Feature Suggestions**: Suggest key project features using AI analysis
- **Usage Examples**: Generate realistic usage examples
- **Multi-language Support**: Translate README content to different languages

## 🔗 GitHub Integration (Future)

GitHub integration will be implemented in Phase 2 and will include:

- **Repository Metadata**: Fetch repo URL, license, contributors automatically
- **Badge Generation**: Generate GitHub-specific badges
- **Issue Tracking**: Link to issues and pull requests
- **Release Information**: Include latest release information

## 🌐 Web Interface (Future)

A web interface will be implemented in Phase 3 using Flask or FastAPI, providing:

- **Template Preview**: See how templates will look before generation
- **Form-based Input**: Fill forms instead of using CLI
- **Real-time Preview**: See README changes in real-time
- **Export Options**: Download README or copy to clipboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/ReadmeGen.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -e .[dev]`
6. Make your changes
7. Run tests: `pytest`
8. Submit a pull request

## 📞 Support

If you have any questions or need help, please:

- 📖 Read our [FAQ](docs/FAQ.md)
- 🐛 Report bugs by [opening an issue](https://github.com/your-username/ReadmeGen/issues/new)
- 💬 Join our [Discord community](#)
- 📧 Email us at support@example.com

## 🙏 Acknowledgments

- Thanks to all contributors
- Inspired by similar projects in the community
- Built with ❤️ using Python and modern development tools

## 📋 Roadmap

### Phase 1: MVP (Current)
- [x] Project structure setup
- [x] CLI interface with typer
- [x] Template system with Jinja2
- [x] Core generator logic
- [x] Three initial templates (minimal, standard, fancy)
- [x] Basic file I/O and validation
- [x] Unit tests for core functionality

### Phase 2: AI Integration
- [ ] AI content enhancement
- [ ] GitHub API integration
- [ ] Badge auto-generation
- [ ] Enhanced templates

### Phase 3: Advanced Features
- [ ] Web UI interface
- [ ] Multi-language support
- [ ] GitHub Action integration
- [ ] Custom AI prompts/templates

---

**Made with** ❤️ **by the community, for the community**
