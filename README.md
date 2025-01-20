# Filesystem Search Engine

A command-line search tool that creates an in-memory index of text files and enables complex search queries.

## Features

- Recursive directory scanning
- In-memory indexing
- Complex query support:
  - Required terms (`+term`)
  - OR groups (`+(term1 term2)`)
  - Optional terms for ranking
- Results sorted by match relevance

## Installation

# Clone repository
git clone https://github.com/yourusername/filesystem-searchengine.git
cd filesystem-searchengine

# Create virtual environment (optional)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install pytest

## Usage
python search.py --dir <directory_to_search>

# Example Query
> biz +foo +bar +(bat baz) bop

This searches for:

Required: "foo" AND "bar"
Required: either "bat" OR "baz"
Optional: "biz" and "bop" (affect ranking)

# Example Output

/path/to/file.txt 12 "Foo is the bar best way to bat my biz bop!"
/path/to/other.txt 1 "foo bar does not baz bop at all"

## Run Tests

pytest tests/ -v

# Run specific test file
pytest tests/test_search.py -v