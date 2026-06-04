#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

"""
OMEGA Semantic Search
====================
Embedding-based code search using semantic similarity.
Finds relevant code snippets by meaning, not just regex/grep.

Inspired by: codebase-mcp, Claude Code - semantic code search
"""

import re
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO, format='[SEMANTIC] %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class CodeChunk:
    """A chunk of code with embedding."""
    id: str
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    chunk_type: str  # function, class, docstring, comment
    vector: Optional[np.ndarray] = None


@dataclass
class SearchResult:
    """Search result with relevance score."""
    chunk: CodeChunk
    score: float
    highlights: List[str] = field(default_factory=list)


class OmegaSemanticSearch:
    """
    Semantic code search using embeddings.
    Falls back to keyword + structural search if embeddings unavailable.
    """
    
    LANGUAGE_PATTERNS = {
        'python': {
            'function': r'def\s+(\w+)\s*\([^)]*\)\s*:',
            'class': r'class\s+(\w+)\s*[:(]',
            'method': r'def\s+(\w+)\s*\([^)]*\)\s*:',
            'import': r'^(?:from\s+(\S+)\s+)?import\s+(\S+)',
        },
        'javascript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*\([^)]*\)\s*=>)',
            'class': r'class\s+(\w+)',
            'method': r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',
            'import': r'import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
        },
        'typescript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?\(|(\w+)\s*\([^)]*\)\s*[=:])',
            'class': r'class\s+(\w+)',
            'interface': r'interface\s+(\w+)',
            'import': r'import\s+(?:{[^}]+}|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
        },
    }
    
    def __init__(self, root_path: Optional[str] = None, embedding_model: str = "all-MiniLM-L6-v2"):
        self.root = Path(root_path or PROJECT_ROOT)
        self.chunks: List[CodeChunk] = []
        self.chunk_index: Dict[str, int] = {}
        self._embeddings = None
        self._model = None
        self._embedding_model = embedding_model
        
    def _try_load_embeddings(self) -> bool:
        """Try to load sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._embedding_model)
            logger.info(f"Loaded embedding model: {self._embedding_model}")
            return True
        except ImportError:
            logger.warning("sentence-transformers not available, using keyword search")
            return False
    
    def _tokenize(self, text: str) -> set:
        """Simple tokenizer."""
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return set(text.split())
    
    def _get_ngrams(self, text: str, n: int = 3) -> set:
        """Get character n-grams for fuzzy matching."""
        text = text.lower()
        return set(text[i:i+n] for i in range(len(text) - n + 1))
    
    def _chunk_code(self, content: str, file_path: str, language: str = "python") -> List[CodeChunk]:
        """Split code into semantic chunks."""
        chunks = []
        lines = content.split('\n')
        
        patterns = self.LANGUAGE_PATTERNS.get(language, self.LANGUAGE_PATTERNS['python'])
        
        # Find all function/class definitions
        definitions = []
        for i, line in enumerate(lines):
            for chunk_type, pattern in patterns.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    name = match.group(1) or match.group(2) or match.group(3)
                    if name and not name.startswith('_'):
                        definitions.append({
                            'type': chunk_type,
                            'name': name,
                            'line': i + 1,
                            'start': i
                        })
        
        # Sort by line number
        definitions.sort(key=lambda x: x['line'])
        
        # Create chunks between definitions
        for i, defn in enumerate(definitions):
            start = defn['start']
            end = definitions[i + 1]['start'] if i + 1 < len(definitions) else len(lines)
            
            # Include docstring before definition if present
            docstring_start = start
            for j in range(start - 1, max(0, start - 10), -1):
                if '"""' in lines[j] or "'''" in lines[j]:
                    docstring_start = j
                    break
            
            chunk_content = '\n'.join(lines[docstring_start:end])
            
            if len(chunk_content.strip()) < 20:
                continue
                
            chunk_id = hashlib.md5(f"{file_path}:{start}:{end}".encode()).hexdigest()[:12]
            
            chunk = CodeChunk(
                id=chunk_id,
                content=chunk_content,
                file_path=file_path,
                start_line=docstring_start + 1,
                end_line=end,
                language=language,
                chunk_type=defn['type']
            )
            chunks.append(chunk)
        
        # If no definitions found, chunk by size
        if not chunks:
            chunk_size = 50
            for i in range(0, len(lines), chunk_size):
                chunk_content = '\n'.join(lines[i:i + chunk_size])
                if len(chunk_content.strip()) < 20:
                    continue
                chunk_id = hashlib.md5(f"{file_path}:{i}:{i+chunk_size}".encode()).hexdigest()[:12]
                chunks.append(CodeChunk(
                    id=chunk_id,
                    content=chunk_content,
                    file_path=file_path,
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    language=language,
                    chunk_type='block'
                ))
        
        return chunks
    
    def index_repository(self, extensions: List[str] = None) -> Dict:
        """Index entire repository for semantic search."""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go']
        
        logger.info(f"Indexing repository: {self.root}")
        
        files_processed = 0
        total_chunks = 0
        
        for ext in extensions:
            for path in self.root.rglob(f"*{ext}"):
                # Skip ignored directories
                if any(ignored in str(path) for ignored in ['node_modules', '__pycache__', '.git', 'venv']):
                    continue
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    language = self._get_language(ext)
                    file_chunks = self._chunk_code(content, str(path), language)
                    
                    for chunk in file_chunks:
                        self.chunks.append(chunk)
                        self.chunk_index[chunk.id] = len(self.chunks) - 1
                    
                    files_processed += 1
                    total_chunks += len(file_chunks)
                    
                except Exception as e:
                    logger.warning(f"Failed to index {path}: {e}")
        
        logger.info(f"Indexed {files_processed} files, {total_chunks} chunks")
        
        # Try to compute embeddings
        embeddings_loaded = self._try_load_embeddings()
        
        if embeddings_loaded and self.chunks:
            logger.info("Computing embeddings for all chunks...")
            texts = [c.content for c in self.chunks]
            
            # Batch compute embeddings
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                emb = self._model.encode(batch, convert_to_numpy=True)
                all_embeddings.append(emb)
            
            embeddings = np.vstack(all_embeddings)
            
            # Store embeddings
            for i, chunk in enumerate(self.chunks):
                chunk.vector = embeddings[i]
            
            logger.info(f"Computed {len(embeddings)} embeddings")
        
        return {
            'files_indexed': files_processed,
            'chunks_created': total_chunks,
            'embeddings_available': self._model is not None
        }
    
    def _get_language(self, ext: str) -> str:
        """Get language from extension."""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'javascript', '.tsx': 'typescript', '.rs': 'rust',
            '.go': 'go', '.java': 'java', '.c': 'c', '.cpp': 'cpp'
        }
        return lang_map.get(ext, 'unknown')
    
    def search(self, query: str, top_k: int = 10, min_score: float = 0.1) -> List[SearchResult]:
        """Search code semantically."""
        if not self.chunks:
            return []
        
        results = []
        
        if self._model is not None:
            # Semantic search with embeddings
            query_embedding = self._model.encode([query], convert_to_numpy=True)[0]
            
            # Compute cosine similarity
            for chunk in self.chunks:
                if chunk.vector is not None:
                    similarity = np.dot(chunk.vector, query_embedding) / (
                        np.linalg.norm(chunk.vector) * np.linalg.norm(query_embedding) + 1e-8
                    )
                    
                    if similarity >= min_score:
                        highlights = self._extract_highlights(chunk.content, query)
                        results.append(SearchResult(
                            chunk=chunk,
                            score=float(similarity),
                            highlights=highlights
                        ))
        else:
            # Fallback: keyword + structural search
            query_tokens = self._tokenize(query)
            query_ngrams = self._get_ngrams(query.lower())
            
            for chunk in self.chunks:
                chunk_tokens = self._tokenize(chunk.content)
                chunk_ngrams = self._get_ngrams(chunk.content.lower())
                
                # Token overlap score
                token_overlap = len(query_tokens & chunk_tokens)
                ngram_overlap = len(query_ngrams & chunk_ngrams)
                
                # Boost by name match
                name_boost = 0
                for token in query_tokens:
                    if token in chunk.content.lower().split()[:10]:
                        name_boost += 0.2
                
                score = (token_overlap * 0.5 + ngram_overlap * 0.3 + name_boost) / (
                    len(query_tokens) + 1
                )
                
                if score >= min_score:
                    highlights = self._extract_highlights(chunk.content, query)
                    results.append(SearchResult(
                        chunk=chunk,
                        score=score,
                        highlights=highlights
                    ))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _extract_highlights(self, content: str, query: str) -> List[str]:
        """Extract relevant highlighted sections."""
        query_terms = query.lower().split()
        highlights = []
        
        for term in query_terms:
            # Find lines containing the term
            for line in content.split('\n'):
                if term in line.lower():
                    stripped = line.strip()
                    if len(stripped) > 10:
                        highlights.append(stripped[:100])
                        break
        
        return highlights[:5]
    
    def search_by_file(self, file_path: str, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search within a specific file."""
        file_chunks = [c for c in self.chunks if c.file_path == file_path]
        
        if not file_chunks:
            return []
        
        query_tokens = self._tokenize(query)
        
        results = []
        for chunk in file_chunks:
            chunk_tokens = self._tokenize(chunk.content)
            score = len(query_tokens & chunk_tokens) / (len(query_tokens) + 1)
            
            if score > 0:
                results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    highlights=self._extract_highlights(chunk.content, query)
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def find_similar(self, code_snippet: str, top_k: int = 5) -> List[SearchResult]:
        """Find similar code to a given snippet."""
        return self.search(code_snippet, top_k=top_k)
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[CodeChunk]:
        """Retrieve a specific chunk."""
        idx = self.chunk_index.get(chunk_id)
        return self.chunks[idx] if idx is not None else None
    
    def export_index(self) -> Dict:
        """Export index for serialization."""
        return {
            'total_chunks': len(self.chunks),
            'embeddings_available': self._model is not None,
            'chunks': [
                {
                    'id': c.id,
                    'file_path': c.file_path,
                    'start_line': c.start_line,
                    'end_line': c.end_line,
                    'language': c.language,
                    'chunk_type': c.chunk_type,
                    'content_preview': c.content[:200]
                }
                for c in self.chunks[:100]
            ]
        }


if __name__ == "__main__":
    import sys
    
    search = OmegaSemanticSearch()
    search.index_repository()
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        results = search.search(query)
        
        print(f"Search: {query}")
        print(f"Results: {len(results)}\n")
        
        for r in results[:5]:
            print(f"[{r.score:.3f}] {r.chunk.file_path}:{r.chunk.start_line}")
            print(f"  {r.chunk.content[:150].strip()}...")
            print()
    else:
        print(json.dumps(search.export_index(), indent=2))