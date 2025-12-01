# Contributing to Simple Print Server

Thank you for your interest in contributing to Simple Print Server! This document provides guidelines and instructions for contributing.

> 📖 **Other Documentation:**
> - [README.md](README.md) - Installation, usage, and quick start guide
> - [API.md](API.md) - Complete API reference
> - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Code Style](#code-style)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Areas for Contribution](#areas-for-contribution)

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior vs actual behavior
- Your operating system and Python version
- Any relevant error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and examples
- Why this feature would be useful

### Pull Requests

1. **Fork the repository** and clone your fork
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style
4. **Test your changes** thoroughly
5. **Commit your changes** with clear commit messages:
   ```bash
   git commit -m "Add: Description of your change"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with a clear description of your changes

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small
- Add docstrings to functions and classes

## Testing

Before submitting a PR, please:
- Test on your operating system (Windows/Linux/macOS)
- Test with different printer types if possible
- Ensure the example page (`example.html`) still works
- Check that no new errors appear in the console

## Project Structure

```
print-program/
├── server.py              # Main Flask server
├── server-tray.py         # System tray version
├── print-client.js        # JavaScript client library
├── example.html           # Example/demo page
├── requirements.txt       # Core dependencies
├── requirements-tray.txt  # Optional tray dependencies
├── install.py             # Cross-platform installer
├── *.bat / *.ps1          # Windows scripts
├── API.md                 # API documentation
├── TROUBLESHOOTING.md     # Troubleshooting guide
└── README.md              # Main documentation
```

## Areas for Contribution

- **Cross-platform improvements**: Better Linux/macOS support
- **Printer drivers**: Support for more printer models
- **Documentation**: Examples, tutorials, translations
- **Testing**: Unit tests, integration tests
- **UI/UX**: Improvements to the example page
- **Performance**: Optimizations and caching

## Questions?

If you have questions, feel free to open an issue with the `question` label.

## Additional Resources

- [README.md](README.md) - Project overview and installation
- [API.md](API.md) - API documentation and examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

Thank you for contributing! 🎉

