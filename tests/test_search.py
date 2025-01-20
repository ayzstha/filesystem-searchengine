import pytest
from pathlib import Path
import sys
import os

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from search import FileSearchEngine, SearchResult

@pytest.fixture
def test_files(tmp_path):
    """Create test files with known content"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    
    # Create test file 1
    with open(test_dir / "file1.txt", "w") as f:
        f.write("Foo is the bar best way to bat my biz bop!\n")
        f.write("Another line with foo and bar and baz\n")
    
    # Create test file 2
    with open(test_dir / "file2.txt", "w") as f:
        f.write("foo bar does not baz bop at all\n")
    
    return test_dir

@pytest.fixture
def search_engine(test_files):
    """Initialize search engine with test data"""
    return FileSearchEngine(str(test_files))

def test_tokenization(search_engine):
    """Test text tokenization"""
    text = "Foo is the bar!"
    tokens = search_engine.tokenize(text)
    assert tokens == ["foo", "is", "the", "bar"]

def test_required_terms(search_engine):
    """Test search with required terms"""
    results = search_engine.search("+foo +bar")
    assert len(results) > 0
    assert all("foo" in r.line_content.lower() and 
              "bar" in r.line_content.lower() 
              for r in results)

def test_or_group(search_engine):
    """Test OR group search"""
    results = search_engine.search("+(bat baz)")
    assert len(results) > 0
    assert all(any(term in r.line_content.lower() 
                  for term in ["bat", "baz"]) 
              for r in results)

def test_result_ordering(search_engine):
    """Test results are ordered by match count"""
    results = search_engine.search("biz +foo +bar bop")
    for i in range(len(results) - 1):
        assert results[i].match_count >= results[i + 1].match_count
