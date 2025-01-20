import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import argparse

@dataclass
class SearchResult:
    directory: str
    filename: str
    line_number: int
    line_content: str
    match_count: int

class FileSearchEngine:
    def __init__(self, directory: str):
        self.directory = directory
        self.index: Dict[str, List[Tuple[str, str, int, str]]] = defaultdict(list)
        self.build_index()

    def tokenize(self, text: str) -> List[str]:
        """Convert text to lowercase tokens"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return text.split()

    def build_index(self):
        """Build inverted index from files"""
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.txt'):
                    self._index_file(root, file)

    def _index_file(self, root: str, filename: str):
        filepath = os.path.join(root, filename)
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                for token in self.tokenize(line):
                    self.index[token].append((root, filename, line_num, line.strip()))

    def parse_query(self, query: str) -> Tuple[List[str], List[List[str]], List[str]]:
        """Parse search query into required, or_required, and optional terms"""
        terms = query.split()
        required = []
        or_required = []
        optional = []

        i = 0
        while i < len(terms):
            if terms[i].startswith('+'):
                if terms[i].startswith('+('):
                    or_group = []
                    i += 1
                    while i < len(terms) and not terms[i].endswith(')'):
                        or_group.append(terms[i].lower())
                        i += 1
                    if i < len(terms):
                        or_group.append(terms[i][:-1].lower())
                    or_required.append(or_group)
                else:
                    required.append(terms[i][1:].lower())
            else:
                optional.append(terms[i].lower())
            i += 1

        return required, or_required, optional

    def search(self, query: str) -> List[SearchResult]:
        """Execute search query and return sorted results"""
        required, or_required, optional = self.parse_query(query)
        results = defaultdict(int)
        
        # Get documents matching required terms
        if required:
            docs = set(self.index[required[0]])
            for term in required[1:]:
                docs &= set(self.index[term])
        else:
            docs = set()
            for term_list in self.index.values():
                docs.update(term_list)

        # Filter by OR groups
        for or_group in or_required:
            or_docs = set()
            for term in or_group:
                or_docs.update(self.index[term])
            docs &= or_docs

        # Score remaining documents
        scored_results = []
        for doc in docs:
            score = len(required) + len(or_required)
            for term in optional:
                if doc in self.index[term]:
                    score += 1
            scored_results.append(SearchResult(
                directory=doc[0],
                filename=doc[1],
                line_number=doc[2],
                line_content=doc[3],
                match_count=score
            ))

        return sorted(scored_results, key=lambda x: x.match_count, reverse=True)

def main():
    parser = argparse.ArgumentParser(description='File content search engine')
    parser.add_argument('--dir', required=True, help='Directory to search')
    args = parser.parse_args()

    engine = FileSearchEngine(args.dir)
    print(f"Indexed files in {args.dir}")
    
    while True:
        try:
            query = input("> ")
            if query.lower() == 'quit':
                break
                
            results = engine.search(query)
            for result in results:
                print(f"{os.path.join(result.directory, result.filename)} "
                      f"{result.line_number} \"{result.line_content}\"")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()