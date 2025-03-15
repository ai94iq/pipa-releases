# ROM Release Tool Documentation

# ROM Release Tool

A command-line tool for creating GitHub releases for custom ROM files with automatic versioning.

## Overview

This tool simplifies the process of creating GitHub releases for ROM distribution by:
- Automatically detecting ZIP and IMG files
- Extracting version information from filenames
- Checking for duplicate tags and incrementing versions
- Providing both interactive and command-line interfaces
- Supporting multiple release types (all files, IMG only, ZIP only, custom selection)

## Installation Requirements

### Required Software
1. **Python 3.6+** - Download from [python.org](https://www.python.org/downloads/)
2. **GitHub CLI** - Download from [cli.github.com](https://cli.github.com/)

### Authentication
Before using the tool, authenticate with GitHub:
```bash
gh auth login
```

### Python Dependencies
All dependencies are standard Python libraries:
- argparse
- os
- re
- subprocess
- sys
- pathlib
- time

## Usage

### Interactive Mode
```bash
./release.sh
```
or
```bash
python release.py
```

This launches an interactive interface that guides you through:
1. Selecting files to include in the release
2. Setting a tag name (automatically extracted from ZIP filenames when possible)
3. Adding release notes
4. Confirming and executing the release

### Command-Line Options

For batch processing or automation:

```bash
./release.sh [OPTIONS]
```

Available options:
- `-a, --all`: Release all files without prompting
- `-i, --img`: Release only .img files
- `-z, --zip`: Release only .zip files
- `-n, --notes "text"`: Set release notes (can be used multiple times)
- `-y, --yes`: Auto-confirm release creation

Examples:
```bash
# Release all files with auto-confirmation
./release.sh --all --yes

# Release only ZIP files with custom notes
./release.sh --zip --notes "Fixed bugs" --notes "Improved performance" --yes
```

## File Naming Convention

The tool extracts release tag information from ZIP filenames using the pattern:
`name-version-date-VARIANT.zip`

For example, from axion-1.1-20250315-IQ-VANILLA-pipa.zip, it extracts:
- Tag: `axion-1.1-20250315`
- Title: The full filename

## Automatic Versioning

If a release with the same tag already exists, the tool will automatically generate a new tag with an incremented version number:
- First attempt: `axion-1.1-20250315`
- If exists: `axion-1.1-20250315-v2`
- If exists: `axion-1.1-20250315-v3`
- And so on...

## Cross-Platform Support

The tool works on:
- **Linux/macOS**: Use release.sh
- **Windows**: Use release.bat

Both scripts are wrappers that execute the Python script with appropriate environment settings.

## For Developers

The implementation uses a three-tiered architecture:
1. **Shell/Batch Scripts**: Platform-specific wrappers
2. **Python Core**: Implementation of all functionality
3. **GitHub CLI**: Handles the actual release creation

To modify the tool's behavior, edit the Python script (`release.py`).