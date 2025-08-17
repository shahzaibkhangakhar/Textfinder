#!/usr/bin/env python3
"""
Enhanced document processor for the RAG system.
Features better chunking, metadata extraction, and document analysis.
"""

import os
import sys
from pathlib import Path
import argparse
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from baseline.retriever.retriever import Retriever

class EnhancedDocumentProcessor:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        """
        Initialize the enhanced document processor.
        
        Args:
            chunk_size: Size of document chunks (in characters)
            chunk_overlap: Overlap between chunks (in characters)
        """
        self.retriever = Retriever(
            model_name='all-MiniLM-L6-v2',
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.documents_info = []
        
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document and extract metadata"""
        try:
            # Get file info
            file_info = {
                'filename': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_type': file_path.suffix,
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'chunks_created': 0
            }
            
            # Add document to retriever
            self.retriever.add_file(file_path)
            
            # Count chunks created
            file_info['chunks_created'] = len(self.retriever.chunks) - sum(d['chunks_created'] for d in self.documents_info)
            
            # Add source metadata to chunks
            for chunk in self.retriever.chunks[-file_info['chunks_created']:]:
                chunk['metadata']['source_file'] = file_path.name
                chunk['metadata']['file_type'] = file_path.suffix
                chunk['metadata']['processed_at'] = datetime.now().isoformat()
            
            self.documents_info.append(file_info)
            return file_info
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
            return None
    
    def process_directory(self, data_dir: str, file_types: List[str] = None) -> Dict[str, Any]:
        """
        Process all documents in a directory.
        
        Args:
            data_dir: Directory containing documents
            file_types: List of file extensions to process (e.g., ['.pdf', '.txt'])
        """
        if file_types is None:
            file_types = ['.pdf', '.txt', '.md']
        
        data_path = Path(data_dir)
        if not data_path.exists():
            print(f"❌ Data directory '{data_dir}' not found")
            return {}
        
        # Find all matching files
        all_files = []
        for ext in file_types:
            all_files.extend(data_path.glob(f"*{ext}"))
        
        print(f"📁 Processing {len(all_files)} documents in {data_dir}")
        print("=" * 60)
        
        # Process each file
        successful = 0
        failed = 0
        
        for file_path in all_files:
            print(f"🔄 Processing: {file_path.name}")
            result = self.process_document(file_path)
            
            if result:
                successful += 1
                print(f"  ✅ Success: {result['chunks_created']} chunks created")
            else:
                failed += 1
                print(f"  ❌ Failed to process")
        
        # Summary
        total_chunks = len(self.retriever.chunks)
        total_size = sum(d['file_size'] for d in self.documents_info)
        
        summary = {
            'total_files': len(all_files),
            'successful_files': successful,
            'failed_files': failed,
            'total_chunks': total_chunks,
            'total_size_kb': total_size / 1024,
            'documents_info': self.documents_info
        }
        
        print(f"\n📊 Processing Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Successful: {summary['successful_files']}")
        print(f"  Failed: {summary['failed_files']}")
        print(f"  Total chunks: {summary['total_chunks']}")
        print(f"  Total size: {summary['total_size_kb']:.1f} KB")
        
        return summary
    
    def save_processing_info(self, output_file: str = "processing_info.json"):
        """Save processing information to a JSON file"""
        info = {
            'processed_at': datetime.now().isoformat(),
            'total_chunks': len(self.retriever.chunks),
            'documents_info': self.documents_info,
            'chunk_samples': self.retriever.chunks[:3] if self.retriever.chunks else []
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Processing info saved to {output_file}")
    
    def get_chunk_statistics(self) -> Dict[str, Any]:
        """Get statistics about the created chunks"""
        if not self.retriever.chunks:
            return {}
        
        chunk_lengths = [len(chunk['text']) for chunk in self.retriever.chunks]
        sources = [chunk['metadata'].get('source_file', 'unknown') for chunk in self.retriever.chunks]
        
        stats = {
            'total_chunks': len(self.retriever.chunks),
            'avg_chunk_length': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths),
            'source_distribution': dict(Counter(sources))
        }
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Enhanced document processor for RAG system")
    parser.add_argument("--data-dir", default="data", help="Directory containing documents")
    parser.add_argument("--chunk-size", type=int, default=512, help="Size of document chunks")
    parser.add_argument("--chunk-overlap", type=int, default=100, help="Overlap between chunks")
    parser.add_argument("--save-info", action="store_true", help="Save processing information")
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = EnhancedDocumentProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        # Process documents
        summary = processor.process_directory(args.data_dir)
        
        # Get chunk statistics
        stats = processor.get_chunk_statistics()
        if stats:
            print(f"\n📈 Chunk Statistics:")
            print(f"  Average chunk length: {stats['avg_chunk_length']:.1f} characters")
            print(f"  Chunk length range: {stats['min_chunk_length']} - {stats['max_chunk_length']}")
            print(f"  Source distribution:")
            for source, count in stats['source_distribution'].items():
                print(f"    {source}: {count} chunks")
        
        # Save processing info if requested
        if args.save_info:
            processor.save_processing_info()
        
        print(f"\n🎉 Enhanced processing complete!")
        print(f"Your RAG system now has {summary['total_chunks']} chunks from {summary['successful_files']} documents!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 