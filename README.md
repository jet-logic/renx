# renx - Advanced File Renaming Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version fury.io](https://badge.fury.io/py/renx.svg)](https://pypi.python.org/pypi/renx/)

`renx` is a powerful command-line utility for batch renaming files and directories with advanced pattern matching and transformation capabilities.

## ☕ Support

If you find this project helpful, consider supporting me:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B01E8SY7)

## Features ✨

- **Pattern-based renaming** 🧩 - Use regex substitutions to transform filenames
- **Smart case conversion** 🔠 - Convert to lowercase (`--lower`) or uppercase (`--upper`)
- **URL-safe names** 🌐 - Clean filenames for web use (`--urlsafe`)
- **Precise file selection** 🎯:
  - Include/exclude files with `--includes`/`--excludes`
  - Control traversal depth with `--max-depth`
- **Safe operations** 🛡️:
  - Dry-run mode by default (`--act` to execute) preview changes before executing
  - Bottom-up or top-down processing

## 📦 Installation

```bash
pip install renx
```

## 🚀 Usage

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

## Regex Substitutions Format

The substitution pattern uses this format:

```
❗REGEX❗REPLACEMENT❗FLAGS
```

Where:

1. The first character (❗) after `-s` or `--subs` acts as the delimiter
2. The pattern is split into parts by this delimiter

## Examples

### Simple substitution

```
-s '/old/new/'
```

- Replaces first occurrence of "old" with "new" in each filename

### 3. Using different delimiters

```
-s '|old|new|'
```

- Uses `|` as delimiter instead of `/`

### 4. Case-insensitive substitution

```
-s ':old:new:i'
```

- Replaces "old", "Old", "OLD", etc. with "new"

### 5. Complex patterns

```
-s '/\d+/_/'
```

- Replaces one or more digits with an underscore

## Supported Flags

The tool supports these regex flags (see Python's `re` module for complete reference):

| Flag | Meaning                        |
| ---- | ------------------------------ |
| `i`  | Case-insensitive matching      |
| `m`  | Multi-line matching            |
| `s`  | Dot matches all (including \n) |
| `x`  | Verbose (ignore whitespace)    |

For example, with `-s '/foo/bar/i'`:

1. Delimiter = `/`
2. Regex = `foo`
3. Replacement = `bar`
4. Flags = `i` (case-insensitive)

## Important Notes

- The delimiter can be any character (but must not appear unescaped in the pattern)
- The tool compiles the regex with the specified flags before applying it

## Practical Examples

- **Replace spaces with underscores**:

  ```
  renx -s '/ /_/' /path/to/files
  ```

- **Remove special characters**:

  ```
  renx -s '/[^a-zA-Z0-9.]//' /path/to/files
  ```

- **Add prefix to numbered files**:

  ```
  renx -s '/(\d+)/image_\1/' *.jpg
  ```

- **Fix inconsistent extensions (case-insensitive)**:
  ```
  renx -s '/\.jpe?g$/.jpg/i' *
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
