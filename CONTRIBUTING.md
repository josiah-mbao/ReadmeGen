# Contributing to ReadmeGen

Thank you for considering contributing to ReadmeGen! This guide will help you get started quickly and understand our contribution process.

## 🚀 Quick Start (60 Seconds)

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/ReadmeGen.git
cd ReadmeGen
```

### 2. Setup Development Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

### 3. Verify Setup
```bash
readmegen --help
pytest  # All tests should pass (7/7)
```

That's it! You're ready to contribute.

## 🎯 Our Philosophy

ReadmeGen follows a **zero-friction adoption** philosophy:

- **Users should install and succeed in under 60 seconds**
- **No configuration needed** - works out of the box
- **Professional results every time** - consistent, reliable output
- **Respect developer time** - minimal cognitive load

**Before contributing, ask yourself: Does this make ReadmeGen easier to use?**

## 📋 Contribution Guidelines

### What We Accept

#### ✅ Phase C Features (Optional Enhancements)
- AI content enhancement (opt-in only)
- GitHub metadata fetching (opt-in only)
- Configuration persistence
- Performance improvements

#### ✅ Reliability & Quality
- Bug fixes with clear reproduction steps
- Enhanced error messages
- Improved test coverage
- Documentation improvements

#### ✅ User Experience
- Better CLI prompts and feedback
- Enhanced template quality
- Accessibility improvements

### What We Don't Accept

#### ❌ Phase A/B Rebuilds
- Core CLI functionality changes
- Template system overhauls
- Error handling system changes
- Basic installation/usage changes

**Reason**: Phase A and B are complete and production-ready. The core functionality delivers exactly what users need.

#### ❌ Complexity Without Clear Value
- Features that require configuration
- Changes that increase cognitive load
- Dependencies that slow down installation
- Breaking changes to existing behavior

## 🔄 Development Workflow

### 1. Choose an Issue
- Look for issues labeled `good first issue` or `help wanted`
- Check that no one else is working on it
- Comment to claim the issue

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow existing code patterns
- Maintain error handling quality
- Keep CLI user-friendly and consistent
- Write clear, descriptive commit messages

### 4. Test Your Changes
```bash
# Run all tests
pytest

# Test deterministic output
python test_deterministic_output.py

# Test CLI manually
readmegen init  # Should work flawlessly
```

### 5. Submit Pull Request
- Include a clear PR description
- Reference the issue number
- Ensure all tests pass
- Follow our code style

## 🧪 Testing Requirements

### All Tests Must Pass
```bash
pytest  # Should show: 7 passed
```

### New Features Need Tests
- Unit tests for new functions
- Integration tests for CLI changes
- Error handling tests for edge cases

### Deterministic Output
- Same inputs must always produce same outputs
- Use `test_deterministic_output.py` to verify

## 📝 Code Standards

### Follow Existing Patterns
- Use `typer` for CLI commands
- Use `questionary` for interactive prompts
- Use `rich` for user feedback
- Maintain consistent error handling

### Error Messages
- User-friendly and actionable
- Include specific guidance for resolution
- Maintain consistent tone and formatting

### CLI Design
- Interactive prompts with smart defaults
- Clear help text and examples
- Graceful handling of edge cases

## 🐛 Bug Reports

### Required Information
- **Steps to reproduce** (exact commands)
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Python version, ReadmeGen version)
- **Error messages** (full traceback if available)

### Example Bug Report
```markdown
## Bug Description
When running `readmegen init` with a project name containing special characters, the CLI crashes.

## Steps to Reproduce
1. Create directory with special characters: `mkdir "my-project@2025"`
2. Run: `readmegen init`
3. Enter project name: `My Project@2025`

## Expected Behavior
CLI should accept the project name or provide clear validation error.

## Actual Behavior
CLI crashes with ValueError.

## Environment
- OS: macOS 14.5
- Python: 3.13.7
- ReadmeGen: 0.1.0
```

## ✨ Feature Requests

### Before Submitting
1. **Check Phase C roadmap** - Is this an optional enhancement?
2. **Validate user need** - Would this help users in under 60 seconds?
3. **Consider complexity** - Does this add configuration or cognitive load?

### Required Information
- **Clear use case** with user scenario
- **Implementation approach** (opt-in, configuration-free)
- **Alternative solutions** considered
- **Impact on zero-friction philosophy**

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Focus on constructive feedback

### Focus on User Value
- Prioritize features that help users succeed quickly
- Maintain the zero-friction experience
- Document changes clearly

### Communication
- Be clear and concise in PR descriptions
- Respond to feedback in a timely manner
- Help maintain the project's quality standards

## 📚 Documentation

### Keep Documentation Minimal and Actionable
- Focus on getting started, not feature lists
- Use clear examples and commands
- Maintain consistency with existing docs

### Update Documentation for:
- New CLI options
- Changed behavior
- New error messages
- Installation instructions

## 🚀 Submitting Your Contribution

### Pull Request Checklist
- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Code follows existing patterns
- [ ] Documentation updated (if needed)
- [ ] PR description is clear and helpful
- [ ] No breaking changes to existing functionality

### PR Description Template
```markdown
## Summary
Brief description of changes

## Test plan
- [ ] All existing tests pass
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Documentation
- [ ] Documentation updated (if needed)
- [ ] Examples updated (if needed)

## Breaking Changes
- [ ] No breaking changes
```

## 🙏 Thank You!

Your contributions help make ReadmeGen better for thousands of developers. By following these guidelines, you help maintain the quality and user experience that makes ReadmeGen special.

**Remember: Every contribution should make ReadmeGen easier to use, not more complex.**

---

*This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.*
