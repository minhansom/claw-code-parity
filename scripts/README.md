# Scripts

This directory contains standalone utility scripts.

## scrape_cheatsheets.py

A web scraper that extracts cheatsheet names from the RStudio cheatsheets webpage, with automatic pagination support.

### Requirements

```bash
pip install requests beautifulsoup4
```

### Usage

Basic usage:
```bash
python3 scripts/scrape_cheatsheets.py
```

Custom URL:
```bash
python3 scripts/scrape_cheatsheets.py --url "https://rstudio.github.io/cheatsheets/"
```

Specify output file:
```bash
python3 scripts/scrape_cheatsheets.py --output my_cheatsheets.json
```

Limit number of pages:
```bash
python3 scripts/scrape_cheatsheets.py --max-pages 10
```

### Features

- **Automatic pagination**: Automatically follows "Next" links to scrape all pages
- **Multiple selector strategies**: Tries various CSS selectors to find cheatsheet items
- **Duplicate removal**: Removes duplicate entries while preserving order
- **JSON output**: Saves results in a structured JSON format
- **Console output**: Displays a formatted list of all found cheatsheets
- **Polite scraping**: Includes delays between requests to avoid overwhelming the server
- **Error handling**: Gracefully handles network errors and timeouts

### Output Format

The script generates a JSON file containing an array of cheatsheet objects:

```json
[
  {
    "name": "Cheatsheet Name",
    "link": "https://example.com/cheatsheet.pdf"
  },
  ...
]
```

### Command Line Options

- `--url`: Base URL to scrape (default: https://rstudio.github.io/cheatsheets/)
- `--output`: Output JSON filename (default: cheatsheets.json)
- `--max-pages`: Maximum number of pages to scrape (default: 50)
