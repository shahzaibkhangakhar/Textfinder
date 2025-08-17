#!/usr/bin/env python3
"""
Document management script for the RAG system.
Helps you analyze, add, and manage your document collection.
"""

import os
import sys
from pathlib import Path
import argparse
from collections import Counter

def analyze_documents(data_dir: str = "data"):
    """Analyze documents in the data directory"""
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"❌ Data directory '{data_dir}' not found")
        return
    
    # Get all files
    all_files = list(data_path.rglob("*"))
    pdf_files = list(data_path.glob("*.pdf"))
    txt_files = list(data_path.glob("*.txt"))
    other_files = [f for f in all_files if f.suffix not in ['.pdf', '.txt', '.py', '.git']]
    
    print(f"📁 Document Analysis for: {data_dir}")
    print("=" * 50)
    
    # File type breakdown
    print(f"\n📊 File Types:")
    print(f"  PDF files: {len(pdf_files)}")
    print(f"  Text files: {len(txt_files)}")
    print(f"  Other files: {len(other_files)}")
    
    # PDF details
    if pdf_files:
        print(f"\n📄 PDF Documents:")
        total_size = 0
        for pdf in pdf_files:
            size_kb = pdf.stat().st_size / 1024
            total_size += size_kb
            print(f"  - {pdf.name} ({size_kb:.1f} KB)")
        print(f"  Total PDF size: {total_size:.1f} KB")
    
    # Text details
    if txt_files:
        print(f"\n📝 Text Documents:")
        for txt in txt_files:
            size_kb = txt.stat().st_size / 1024
            print(f"  - {txt.name} ({size_kb:.1f} KB)")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if len(pdf_files) < 5:
        print("  - Consider adding more PDF documents for better coverage")
    if len(pdf_files) > 20:
        print("  - Large document collection detected - consider chunking strategy")
    
    print(f"  - Current total documents: {len(pdf_files) + len(txt_files)}")

def add_sample_documents():
    """Add some sample documents to get started"""
    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    
    # Create sample text files
    sample_texts = {
        "sample_article.txt": """
        Artificial Intelligence and Machine Learning
        
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        intelligent machines that work and react like humans. Machine Learning (ML) is a 
        subset of AI that enables computers to learn and improve from experience without 
        being explicitly programmed.
        
        Key areas of AI include:
        - Natural Language Processing
        - Computer Vision
        - Robotics
        - Expert Systems
        
        Machine Learning algorithms can be categorized into:
        - Supervised Learning
        - Unsupervised Learning
        - Reinforcement Learning
        """,
        
        "sample_notes.txt": """
        RAG System Notes
        
        A Retrieval-Augmented Generation (RAG) system combines:
        1. Document retrieval using semantic search
        2. Text generation using language models
        3. Context-aware answer generation
        
        Benefits:
        - More accurate answers
        - Up-to-date information
        - Source attribution
        - Reduced hallucination
        """
    }
    
    print("📝 Creating sample documents...")
    for filename, content in sample_texts.items():
        file_path = data_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"  ✅ Created: {filename}")
    
    print(f"\n🎉 Sample documents added to {data_path}/")
    print("You can now run: python add_documents.py")

def main():
    parser = argparse.ArgumentParser(description="Manage RAG system documents")
    parser.add_argument("--action", choices=["analyze", "add-samples"], default="analyze",
                       help="Action to perform")
    parser.add_argument("--data-dir", default="data", help="Data directory to analyze")
    
    args = parser.parse_args()
    
    if args.action == "analyze":
        analyze_documents(args.data_dir)
    elif args.action == "add-samples":
        add_sample_documents()
    else:
        print("❌ Invalid action specified")

if __name__ == "__main__":
    main() 