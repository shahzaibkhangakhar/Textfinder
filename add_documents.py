#!/usr/bin/env python3
"""
Script to add multiple PDF documents to the RAG system.
This makes it easy to train on new documents without restarting the server.
"""

import os
import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from baseline.pipeline import RAGPipeline

def add_documents_to_rag(data_dir: str = "data", model_name: str = "google/flan-t5-base"):
    """
    Add all PDF documents from the data directory to the RAG system.
    
    Args:
        data_dir (str): Directory containing PDF files
        model_name (str): Name of the generator model to use
    """
    
    # Initialize pipeline
    print(f"Initializing RAG pipeline with model: {model_name}")
    pipeline = RAGPipeline(
        model_name=model_name,
        retriever_model='all-MiniLM-L6-v2',
        log_dir="logs"
    )
    
    # Get all PDF files
    data_path = Path(data_dir)
    pdf_files = list(data_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.name} ({pdf.stat().st_size / 1024:.1f} KB)")
    
    # Add documents to pipeline
    print("\nAdding documents to RAG system...")
    pipeline.add_documents(directory=data_dir, glob_pattern="*.pdf")
    
    print(f"\n✅ Successfully added {len(pdf_files)} documents to RAG system!")
    print("You can now query the system with questions about any of these documents.")
    
    return pipeline

def main():
    parser = argparse.ArgumentParser(description="Add PDF documents to RAG system")
    parser.add_argument("--data-dir", default="data", help="Directory containing PDF files")
    parser.add_argument("--model", default="google/flan-t5-base", help="Generator model name")
    
    args = parser.parse_args()
    
    try:
        pipeline = add_documents_to_rag(args.data_dir, args.model)
        print("\n🎉 RAG system is ready for queries!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 