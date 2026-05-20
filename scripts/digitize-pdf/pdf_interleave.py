#!/usr/bin/env python3
"""
PDF Page Interleaver
Inserts all pages from a second PDF after every page of the first PDF.
"""

import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing dependency. Install with:")
    print("  pip install pymupdf")
    sys.exit(1)


def interleave_pdfs(main_pdf_path, insert_pdf_path, output_path=None, start_page=1):
    """
    Insert all pages from insert_pdf after every page of main_pdf.
    
    Args:
        main_pdf_path: Path to the main PDF file
        insert_pdf_path: Path to the PDF to insert after each page
        output_path: Path for output PDF (default: main_interleaved.pdf)
        start_page: 1-based start page in insert_pdf to begin insertion (default: 1)
    
    Returns:
        Path to the created output file
    
    Example:
        Main PDF: [A, B, C]
        Insert PDF: [W, X, Y]
        start_page=2
        Inserted pages each time: [X, Y]
        Result: [A, X, Y, B, X, Y, C, X, Y]
    """
    main_path = Path(main_pdf_path)
    insert_path = Path(insert_pdf_path)
    
    if output_path is None:
        output_path = main_path.parent / f"{main_path.stem}_interleaved.pdf"
    else:
        output_path = Path(output_path)
    
    # Open source PDFs
    main_doc = fitz.open(main_pdf_path)
    insert_doc = fitz.open(insert_pdf_path)
    
    main_pages = len(main_doc)
    insert_pages = len(insert_doc)

    if start_page < 1:
        raise ValueError("start_page must be at least 1")
    if start_page > insert_pages:
        raise ValueError(
            f"start_page ({start_page}) exceeds insert PDF page count ({insert_pages})"
        )

    start_index = start_page - 1
    inserted_pages_per_main_page = insert_pages - start_index
    
    print(f"Main PDF: {main_path.name} ({main_pages} pages)")
    print(f"Insert PDF: {insert_path.name} ({insert_pages} pages)")
    print(f"Insert start page: {start_page}")
    print(
        f"Output will have: {main_pages + (main_pages * inserted_pages_per_main_page)} pages"
    )
    print("-" * 50)
    
    # Create new document
    output_doc = fitz.open()
    
    for i in range(main_pages):
        # Insert page from main PDF
        output_doc.insert_pdf(main_doc, from_page=i, to_page=i)
        
        # Insert pages from insert PDF beginning at start_page
        output_doc.insert_pdf(insert_doc, from_page=start_index, to_page=insert_pages - 1)
        
        print(f"Processed page {i + 1}/{main_pages}")
    
    # Save output
    output_doc.save(output_path)
    
    # Clean up
    output_doc.close()
    main_doc.close()
    insert_doc.close()
    
    print("-" * 50)
    print(f"Saved to: {output_path}")
    
    return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Insert all pages from one PDF after every page of another PDF."
    )
    parser.add_argument("main_pdf", help="Main PDF file")
    parser.add_argument("insert_pdf", help="PDF to insert after each page")
    parser.add_argument("-o", "--output", help="Output file path (default: <main>_interleaved.pdf)")
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="1-based page number in insert PDF to start insertion from (default: 1)",
    )
    
    args = parser.parse_args()
    
    for path in [args.main_pdf, args.insert_pdf]:
        if not Path(path).exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
    
    interleave_pdfs(args.main_pdf, args.insert_pdf, args.output, start_page=args.start_page)


if __name__ == "__main__":
    main()
