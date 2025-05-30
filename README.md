# renx - Advanced File Renaming Tool

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version fury.io](https://badge.fury.io/py/renx.svg)](https://pypi.python.org/pypi/renx/)
[![Tests Status](https://github.com/jet-logic/renx/actions/workflows/build.yml/badge.svg)](https://github.com/jet-logic/renx/actions)

`renx` is a powerful command-line utility for batch renaming files and directories with advanced pattern matching and transformation capabilities.

## ☕ Support

If you find this project helpful, consider supporting me:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B01E8SY7)

## ✨ Features

- **Pattern-based renaming** 🧩 - Use regex substitutions to transform filenames
- **Case conversion**: lower, upper, title, swapcase, capitalize
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

## 🔁 Substitution Pattern Format

### 1. Simple Transformation Syntax

```
transform_name[:additional_flags]
```

- Applies a transformation to the entire input
- No search-replace pattern matching
- Example: `"upper"` or `"lower:ext"`

### 2. Search-Replace Syntax

```
❗search❗replacement❗[flags]
```

- Performs pattern-based substitution
- Example: `"/old/new/"` or `"@pattern@replacement@i"`
- The first character (❗) after `-s` or `--subs` acts as the delimiter

### Components

#### Separators

❗ Must be one of these special characters:

```
!"#$%&'*+,-./:;<=>?@\^_`|~
```

First character of string defines the separator for the entire pattern.

#### Transformation Names

Available transformations (can be used in both syntax forms):

| Name       | Description                           |
| ---------- | ------------------------------------- |
| upper      | Convert to uppercase                  |
| lower      | Convert to lowercase                  |
| title      | Title case                            |
| swapcase   | Swap case of all letters              |
| expandtabs | Replace tabs with spaces              |
| casefold   | Aggressive lowercase for matching     |
| capitalize | Capitalize first letter               |
| asciify    | Convert to ASCII (custom function)    |
| slugify    | Convert to URL slug (custom function) |
| urlsafe    | Make URL-safe (custom function)       |

#### Special Flags

Can be appended after colons (`:`):

| Flag | Description                   |
| ---- | ----------------------------- |
| ext  | Only apply to file extensions |
| stem | Only apply to filename stems  |

#### Regex Flags

Standard Python regex flags can be included:

- `i` - Case insensitive
- `m` - Multiline mode
- `s` - Dot matches all
- etc. (any valid regex flag)

#### Examples

Simple Transformations

- `"upper"` - Convert entire string to uppercase
- `"lower:ext"` - Convert file extension to lowercase
- `"slugify:stem"` - Convert filename stem to URL slug

Search-Replace Operations

- `"/old/new/"` - Basic replacement
- `"@[0-9]+@NUM@i"` - Replace all numbers with "NUM" (case insensitive)
- `"#cat#dog#ext"` - Replace "cat" with "dog" only in file extensions
- `"!([A-Z])!\1_!stem:lower"` - Add underscore after capitals in stems and lowercase all

### Usage Notes

- When using the search-replace syntax, the first character must be from the separator set
- Multiple flags can be combined with colons (`:`)
- The "ext" and "stem" flags are mutually exclusive

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
   python -m renx --depth ..2 /path/to/files
   ```

## Multiple substitution

When your downloaded files look like they were named by a cat walking on a keyboard 😉:

```bash
python -m renx --act \
    -s '#(?:(YTS(?:.?\w+)|YIFY|GloDLS|RARBG|ExTrEmE|EZTVx.to|MeGusta|Lama))##ix' \
    -s '!(2160p|1080p|720p|x264|x265|HEVC|AAC|AC3)!!i' \
    -s '!(HDRip|BluRay|WEB-DL|DVDrip|BRrip|WEBRip|HDRip|DTS)!!i' \
    -s '!\[(|\w+)\]!\1!' \
    -s '/[\._-]+/./' \
    -s '/\.+/ /stem' \
    -s /.+//ext:lower \
    -s '/.+//stem:title' \
    --include "*.m*" \
    .
# Before: "the.matrix.[1999].1080p.[YTS.AM].BRRip.x264-[GloDLS].ExTrEmE.mKV"
# After: "The Matrix 1999.mkv" 🎬✨
```
