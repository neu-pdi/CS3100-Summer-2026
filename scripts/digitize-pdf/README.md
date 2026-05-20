# digitize-pdf Scripts

## `split_by_qr.py`

Splits a scanned exam PDF that contains multiple scanned exams into multiple files, each based on QR codes embedded on each exam. Each QR code encodes an exam version; the script groups exams by that identifier and writes one PDF per version to the output directory. Missing dependencies (PyMuPDF, opencv-python, numpy) are installed automatically on first run.

Use the --num-pages argument to specify how many pages per student are contained in the PDF. For example, if the PDF contains the entire exam for each student, this argument should be equal to the number of pages per exam. If the PDF contains only the first (bubble form) page for each student, this argument should be equal to 1.

**Usage:**
```
python3 split_by_qr.py --input <input.pdf> --outdir <output_dir> [--num-pages N]
```

| Argument | Required | Description |
|---|---|---|
| `--input INPUT` | Yes | Path to the scanned input PDF |
| `--outdir OUTDIR` | Yes | Directory to write per-student output PDFs |
| `--num-pages N` | No | Number of pages per exam (default: `1`) |

**Example:**
```
python3 split_by_qr.py --input scanned_exams.pdf --outdir output/ --num-pages 2
```

---

## `pdf_interleave.py`

Inserts all pages (or a suffix of pages) from a second PDF after every page of a first PDF. This is useful if only the first page of each student exam is scanned in, and the rest of the exam is to be appended to each such page before importing it in Gradescope (which expects all the pages for each student) Requires PyMuPDF (`pip install pymupdf`).

Use the --start-page argument to "skip" pages from the second PDF. For example, if the input contains only page 1 for each student, then one can provide the entire exam (including page 1) as the second PDF with a --start-page 2, so that it will insert pages (2-N) of the second PDF after every page of the first PDF.

**Usage:**
```
python3 pdf_interleave.py <main_pdf> <insert_pdf> [-o OUTPUT] [--start-page N]
```

| Argument | Required | Description |
|---|---|---|
| `main_pdf` | Yes | Main PDF file (positional) |
| `insert_pdf` | Yes | PDF whose pages are inserted after each main page (positional) |
| `-o / --output OUTPUT` | No | Output file path (default: `<main>_interleaved.pdf`) |
| `--start-page N` | No | 1-based page in `insert_pdf` to start inserting from (default: `1`) |

**Example:**
```
python3 pdf_interleave.py exams.pdf answer_sheet.pdf -o exams_with_answers.pdf --start-page 2
```
