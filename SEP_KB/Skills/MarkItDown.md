# MarkItDown Skill

MarkItDown is a lightweight Python utility for converting various file formats to Markdown. It preserves important structure like headings, lists, and tables.

## Supported Formats
- PDF, PowerPoint (`.pptx`), Word (`.docx`), Excel (`.xlsx`)
- Images, Audio, HTML, ZIP, YouTube URLs.

## Installation
Requires Python 3.10+.
```bash
pip install 'markitdown[all]'
```

## Usage (CLI)
Standard conversion:
```bash
markitdown path-to-file.pdf -o document.md
```

## Usage (Python API)
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("test.xlsx")
print(result.text_content)
```

## Usage for Agents
When dealing with unreadable binary formats (like `.pdf` or `.pptx`), agents should install `markitdown` and use the CLI to generate a `.md` version, saving it to the `Sources/` directory in the Wiki.
