#!/usr/bin/env python3
"""
PHASE 13: RAG Integration
Retrieval-Augmented Generation for long-term memory.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

class OmegaRAG:
    """
    RAG system for retrieving relevant context from MEMORY.md.
    Uses simple TF-IDF-like scoring (no external dependencies).
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.memory_file = self.project_path / "memory" / "MEMORY.md"
        self.index_file = self.project_path / "state" / "rag_index.json"
        self._ensure_memory()
        self._build_index()
    
    def _ensure_memory(self):
        """Ensure memory file exists."""
        if not self.memory_file.exists():
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.memory_file.write_text("# OMEGA Long-Term Memory\n\nNo entries yet.\n")
    
    def _build_index(self):
        """Build simple inverted index for retrieval."""
        if self.index_file.exists():
            try:
                self.index = json.loads(self.index_file.read_text())
                return
            except:
                pass
        
        self.index = {"terms": {}, "chunks": []}
        self._reindex()
    
    def _reindex(self):
        """Reindex all memory content."""
        content = self.memory_file.read_text()
        lines = content.split("\n")
        
        chunks = []
        current_chunk = []
        
        for line in lines:
            if line.startswith("## "):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
            current_chunk.append(line)
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        term_doc = {}
        for i, chunk in enumerate(chunks):
            words = chunk.lower().split()
            for word in words:
                word = word.strip(".,!?;:()[]{}")
                if len(word) > 2:
                    if word not in term_doc:
                        term_doc[word] = []
                    term_doc[word].append(i)
        
        self.index = {"terms": term_doc, "chunks": chunks}
        self._save_index()
    
    def _save_index(self):
        """Save index to disk."""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.index_file.write_text(json.dumps(self.index, indent=2))
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant chunks for query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
        
        Returns:
            List of dicts with 'content' and 'score'
        """
        query_terms = [w.strip(".,!?;:()[]{}").lower() 
                      for w in query.split() if len(w) > 2]
        
        if not query_terms:
            return []
        
        doc_scores = {}
        for term in query_terms:
            if term in self.index["terms"]:
                for doc_id in self.index["terms"][term]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        if not doc_scores:
            return []
        
        max_score = max(doc_scores.values())
        results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: -x[1])[:top_k]:
            if doc_id < len(self.index["chunks"]):
                results.append({
                    "content": self.index["chunks"][doc_id],
                    "score": score / max_score,
                    "chunk_id": doc_id
                })
        
        return results
    
    def add_to_memory(self, text: str, category: str = "learned"):
        """Add new entry to memory."""
        timestamp = datetime.now().isoformat()
        
        entry = f"\n\n## {category.title()} - {timestamp}\n\n{text}\n"
        
        with open(self.memory_file, "a") as f:
            f.write(entry)
        
        self._reindex()
    
    def retrieve_context(self, query: str, max_tokens: int = 500) -> str:
        """Retrieve context and format for LLM prompt."""
        results = self.retrieve(query, top_k=3)
        
        if not results:
            return ""
        
        context_parts = ["# Relevant Context from Memory\n"]
        for r in results:
            context_parts.append(r["content"][:max_tokens])
        
        return "\n---\n".join(context_parts)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: omega_rag.py <project_path> [query]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    rag = OmegaRAG(project_path)
    
    if len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        results = rag.retrieve(query)
        print(f"Found {len(results)} results for: {query}\n")
        for r in results:
            print(f"[Score: {r['score']:.2f}]")
            print(r['content'][:200])
            print("---")
    else:
        rag.add_to_memory(
            "When solving import errors, always check sys.path first",
            category="lesson"
        )
        print("Added sample memory entry")
