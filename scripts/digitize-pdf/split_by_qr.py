import importlib
import subprocess
import sys
from collections import defaultdict
import os
import argparse

fitz = None
cv2 = None
np = None


def ensure_dependencies():
    """Install and import required third-party dependencies if missing."""
    global fitz, cv2, np

    deps = [
        ("fitz", "PyMuPDF"),
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
    ]

    for module_name, package_name in deps:
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"Installing missing dependency: {package_name}")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )

    fitz = importlib.import_module("fitz")
    cv2 = importlib.import_module("cv2")
    np = importlib.import_module("numpy")

def extract_qr_from_page(page, dpi=300):
    """Extract QR code data from a PDF page using multiple detection methods."""
    
    # Render page at higher DPI for better detection
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to numpy array
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )
    
    # Convert to BGR
    if pix.n == 4:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Initialize QR detector
    qr_detector = cv2.QRCodeDetector()
    
    # List of image preprocessing variations to try
    images_to_try = []
    
    # 1. Original grayscale
    images_to_try.append(gray)
    
    # 2. Binary threshold
    _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    images_to_try.append(thresh1)
    
    # 3. Otsu's threshold
    _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    images_to_try.append(thresh2)
    
    # 4. Adaptive threshold
    thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 11, 2)
    images_to_try.append(thresh3)
    
    # 5. Inverted binary
    images_to_try.append(cv2.bitwise_not(thresh1))
    
    # 6. Contrast enhanced
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    images_to_try.append(enhanced)
    
    # 7. Sharpened
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    images_to_try.append(sharpened)
    
    # 8. Morphological operations
    kernel_morph = np.ones((3,3), np.uint8)
    morph = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel_morph)
    images_to_try.append(morph)
    
    # Try detection on each preprocessed image
    for img in images_to_try:
        # Convert back to BGR for detector
        if len(img.shape) == 2:
            img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_color = img
            
        data, bbox, _ = qr_detector.detectAndDecode(img_color)
        if data:
            return data
    
    # Try detecting on cropped regions (QR is usually in bottom-left)
    h, w = gray.shape
    regions = [
        gray[int(h*0.7):h, 0:int(w*0.4)],           # Bottom-left
        gray[int(h*0.8):h, 0:int(w*0.3)],           # Bottom-left (smaller)
        gray[int(h*0.6):h, 0:int(w*0.5)],           # Bottom-left (larger)
        gray[0:int(h*0.4), 0:int(w*0.4)],           # Top-left
        gray[int(h*0.7):h, int(w*0.6):w],           # Bottom-right
    ]
    
    for region in regions:
        if region.size == 0:
            continue
            
        # Try with different thresholds on each region
        for thresh_val in [100, 127, 150, 180]:
            _, region_thresh = cv2.threshold(region, thresh_val, 255, cv2.THRESH_BINARY)
            region_color = cv2.cvtColor(region_thresh, cv2.COLOR_GRAY2BGR)
            
            # Scale up small regions
            if region.shape[0] < 200 or region.shape[1] < 200:
                scale = 2
                region_color = cv2.resize(region_color, None, fx=scale, fy=scale, 
                                         interpolation=cv2.INTER_CUBIC)
            
            data, bbox, _ = qr_detector.detectAndDecode(region_color)
            if data:
                return data
    
    return None

def split_pdf_by_qr(input_pdf, pages_per_exam,output_dir="output"):
    """Split PDF into separate files based on QR code content."""
    ensure_dependencies()
    
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(input_pdf)
    
    qr_groups = defaultdict(list)
    pages_without_qr = []
    
    print(f"Processing {len(doc)/pages_per_exam} exams...")
    print("(This may take a moment due to enhanced detection)\n")
    
    for starting_page in range(0,len(doc),pages_per_exam):
        page = doc[starting_page]
        qr_data = extract_qr_from_page(page)
        
        if qr_data:
            for page in range(starting_page,starting_page+pages_per_exam):
                qr_groups[qr_data].append(page)
            print(f"Page {starting_page + 1}: ✓ QR found - {qr_data[:40]}...")
        else:
            for page in range(starting_page,starting_page+pages_per_exam):
                pages_without_qr.append(page)
            print(f"Page {starting_page + 1}: ✗ No QR code detected")
    
    print(f"\n{'='*50}")
    print(f"Found {len(qr_groups)} unique QR codes")
    print(f"{'='*50}\n")
    
    # Create PDFs for each QR group
    for idx, (qr_data, page_numbers) in enumerate(qr_groups.items(), 1):
        safe_name = "".join(c if c.isalnum() else "_" for c in qr_data[:20])
        output_filename = f"{output_dir}/group_{idx}_{safe_name}.pdf"
        
        new_doc = fitz.open()
        for page_num in page_numbers:
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        new_doc.save(output_filename)
        new_doc.close()
        
        page_list = [p+1 for p in page_numbers]
        print(f"Created: {output_filename}")
        print(f"         Pages: {page_list}\n")
    
    # Handle pages without QR
    if pages_without_qr:
        output_filename = f"{output_dir}/no_qr_code.pdf"
        new_doc = fitz.open()
        for page_num in pages_without_qr:
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        new_doc.save(output_filename)
        new_doc.close()
        print(f"Created: {output_filename}")
        print(f"         Pages without QR: {[p+1 for p in pages_without_qr]}\n")
    
    
    
    # Summary
    print(f"{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total exams: {len(doc)/pages_per_exam}")
    print(f"Unique QR codes: {len(qr_groups)}")
    print(f"Exams without QR: {len(pages_without_qr)}")
    print(f"Output directory: {output_dir}/")
    doc.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split an exam PDF into separate files based on QR content."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input PDF file.",
    )
    parser.add_argument(
        "--outdir",
        required=True,
        help="Path to the output directory.",
    )
    parser.add_argument(
        "--num-pages",
        type=int,
        default=1,
        help="Number of pages per exam (default: 1).",
    )

    args = parser.parse_args()
    if args.num_pages < 1:
        parser.error("--num-pages must be at least 1")

    split_pdf_by_qr(args.input, pages_per_exam=args.num_pages, output_dir=args.outdir)