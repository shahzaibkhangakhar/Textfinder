#!/usr/bin/env python3
"""
Document search and analysis tool for the RAG system.
Helps you explore, search, and analyze your processed documents.
"""

import os
import sys
from pathlib import Path
import argparse
import json
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from baseline.retriever.retriever import Retriever

class DocumentSearchTool:
    def __init__(self, processing_info_file: str = "processing_info.json"):
        """
        Initialize the document search tool.
        
        Args:
            processing_info_file: Path to the processing info JSON file
        """
        self.processing_info_file = processing_info_file
        self.processing_info = self.load_processing_info()
        self.retriever = None
        
    def load_processing_info(self) -> Dict[str, Any]:
        """Load processing information from JSON file"""
        try:
            with open(self.processing_info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Processing info file '{self.processing_info_file}' not found")
            print("Run enhanced_processor.py first to generate this file")
            return {}
        except Exception as e:
            print(f"❌ Error loading processing info: {str(e)}")
            return {}
    
    def initialize_retriever(self):
        """Initialize the retriever with processed documents"""
        if not self.processing_info:
            print("❌ No processing info available")
            return False
        
        try:
            self.retriever = Retriever(
                model_name='all-MiniLM-L6-v2',
                chunk_size=512,
                chunk_overlap=100
            )
            
            # Re-add documents to retriever
            data_dir = "data"
            self.retriever.add_directory(data_dir, "*.pdf")
            self.retriever.add_directory(data_dir, "*.txt")
            
            print(f"✅ Retriever initialized with {len(self.retriever.chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing retriever: {str(e)}")
            return False
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents for a query"""
        if not self.retriever:
            if not self.initialize_retriever():
                return []
        
        try:
            results = self.retriever.query(query, k=k)
            return results
        except Exception as e:
            print(f"❌ Error searching documents: {str(e)}")
            return []
    
    def analyze_document_coverage(self):
        """Analyze document coverage and chunk distribution"""
        if not self.processing_info:
            print("❌ No processing info available")
            return
        
        print("📊 Document Coverage Analysis")
        print("=" * 50)
        
        # Document statistics
        total_files = len(self.processing_info.get('documents_info', []))
        total_chunks = self.processing_info.get('total_chunks', 0)
        total_size_kb = sum(d['file_size'] for d in self.processing_info.get('documents_info', [])) / 1024
        
        print(f"📁 Total Documents: {total_files}")
        print(f"🧩 Total Chunks: {total_chunks}")
        print(f"💾 Total Size: {total_size_kb:.1f} KB")
        print(f"📊 Average chunks per document: {total_chunks/total_files:.1f}")
        
        # Document breakdown
        print(f"\n📄 Document Breakdown:")
        for doc in self.processing_info.get('documents_info', []):
            chunks_per_kb = doc['chunks_created'] / (doc['file_size'] / 1024)
            print(f"  {doc['filename']}:")
            print(f"    - Size: {doc['file_size']/1024:.1f} KB")
            print(f"    - Chunks: {doc['chunks_created']}")
            print(f"    - Chunks/KB: {chunks_per_kb:.2f}")
    
    def explore_chunks(self, source_file: str = None, limit: int = 5):
        """Explore chunks from a specific source or all chunks"""
        if not self.processing_info:
            print("❌ No processing info available")
            return
        
        chunks = self.processing_info.get('chunk_samples', [])
        if not chunks:
            print("❌ No chunk samples available")
            return
        
        print(f"🔍 Chunk Exploration")
        print("=" * 50)
        
        filtered_chunks = chunks
        if source_file:
            filtered_chunks = [c for c in chunks if c['metadata'].get('source_file') == source_file]
            print(f"📄 Showing chunks from: {source_file}")
        else:
            print(f"📄 Showing all chunk samples")
        
        for i, chunk in enumerate(filtered_chunks[:limit], 1):
            print(f"\n🧩 Chunk {i}:")
            print(f"  Source: {chunk['metadata'].get('source_file', 'Unknown')}")
            print(f"  Type: {chunk['metadata'].get('file_type', 'Unknown')}")
            print(f"  Length: {len(chunk['text'])} characters")
            print(f"  Text: {chunk['text'][:100]}...")
    
    def interactive_search(self):
        """Interactive search mode"""
        if not self.initialize_retriever():
            return
        
        print("🔍 Interactive Search Mode")
        print("=" * 50)
        print("Type your questions (or 'quit' to exit)")
        print("Examples:")
        print("  - What is Imran Khan's background?")
        print("  - What are the key areas of AI?")
        print("  - What is a RAG system?")
        print()
        
        while True:
            try:
                query = input("❓ Question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"\n🔍 Searching for: '{query}'")
                results = self.search_documents(query, k=3)
                
                if results:
                    print(f"✅ Found {len(results)} relevant chunks:")
                    for i, result in enumerate(results, 1):
                        source = result['metadata'].get('source_file', 'Unknown')
                        score = result['score']
                        text = result['text'][:150] + "..." if len(result['text']) > 150 else result['text']
                        print(f"\n  {i}. Source: {source} (Score: {score:.3f})")
                        print(f"     Text: {text}")
                else:
                    print("❌ No relevant chunks found")
                
                print("\n" + "-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Document search and analysis tool")
    parser.add_argument("--action", choices=["analyze", "explore", "search", "interactive"], 
                       default="analyze", help="Action to perform")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--source", help="Source file to explore")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to show")
    
    args = parser.parse_args()
    
    tool = DocumentSearchTool()
    
    if args.action == "analyze":
        tool.analyze_document_coverage()
    
    elif args.action == "explore":
        tool.explore_chunks(args.source, args.limit)
    
    elif args.action == "search":
        if not args.query:
            print("❌ Please provide a search query with --query")
            return
        
        results = tool.search_documents(args.query, args.limit)
        if results:
            print(f"🔍 Search results for: '{args.query}'")
            print("=" * 50)
            for i, result in enumerate(results, 1):
                source = result['metadata'].get('source_file', 'Unknown')
                score = result['score']
                text = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                print(f"\n{i}. Source: {source} (Score: {score:.3f})")
                print(f"   {text}")
        else:
            print("❌ No results found")
    
    elif args.action == "interactive":
        tool.interactive_search()

if __name__ == "__main__":
    main() 