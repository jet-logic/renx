# renx - Advanced File Renaming Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

`renx` is a powerful command-line utility for batch renaming files and directories with advanced pattern matching and transformation capabilities.

## Features

- Recursive directory traversal (top-down or bottom-up)
- Multiple renaming transformations:
  - Case conversion (lowercase/uppercase)
  - URL-safe filename generation
  - Regular expression substitutions
- Flexible filtering:
  - Include/exclude by glob patterns or regex
  - Maximum depth control
- Safety features:
  - Dry-run mode by default
  - Preview changes before executing

## Installation

```bash
pip install renx
```

## Usage

```bash
python -m renx [OPTIONS] [PATHS...]
```

### Basic Examples

1. **Dry-run preview (default behavior)**:

   ```bash
   python -m renx /path/to/files
   ```

2. **Convert filenames to lowercase**:

   ```bash
   python -m renx --lower /path/to/files
   ```

3. **Actually perform renames (disable dry-run)**:

   ```bash
   python -m renx --act --lower /path/to/files
   ```

4. **Make filenames URL-safe**:
   ```bash
   python -m renx --urlsafe /path/to/files
   ```

### Regex Substitutions

The `--subs` (`-s`) option supports Perl-style regex substitutions:

Format: `/DELIMITER/PATTERN/DELIMITER/REPLACEMENT/DELIMITER/FLAGS`

Examples:

1. Replace spaces with underscores:

   ```bash
   python -m renx -s '/ /_/g' /path/to/files
   ```

2. Remove special characters:

   ```bash
   python -m renx -s '/[^a-zA-Z0-9.]//' /path/to/files
   ```

3. Add prefix to numbered files:

   ```bash
   python -m renx -s '/(\d+)/image_$1/' *.jpg
   ```

4. Case-insensitive extension fix:
   ```bash
   python -m renx -s '/\.jpe?g$/.jpg/i' *
   ```

### Filtering Options

1. **Process only matching files**:

   ```bash
   python -m renx --name '*.txt' --lower /path/to/files
   ```

2. **Exclude directories**:

   ```bash
   python -m renx --exclude 'temp/*' /path/to/files
   ```

3. **Limit recursion depth**:
   ```bash
   python -m renx --max-depth 2 /path/to/files
   ```
