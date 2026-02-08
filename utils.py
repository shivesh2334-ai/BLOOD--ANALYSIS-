import pdfplumber
import pytesseract
from PIL import Image
import re

def extract_text_from_pdf(pdf_file):
    """Extracts text from a digital PDF."""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If pdfplumber finds nothing, it might be a scanned image PDF
        if not text.strip():
            return "Error: This PDF appears to be a scanned image. Please upload a digital PDF or a high-quality photo instead."
            
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_image(image_file):
    """Extracts text from an image using OCR (Tesseract)."""
    try:
        img = Image.open(image_file)
        # Standard OCR
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

def parse_blood_report(text):
    """
    Parses raw text to find blood parameters and their values.
    Returns a dictionary grouped by panel (CBC, LFT, etc.)
    """
    # Define common parameter keywords to look for
    keywords = {
        "CBC": ["WBC", "RBC", "Hemoglobin", "Hb", "Hematocrit", "HCT", "Platelet", "MCV", "MCH", "MCHC", "RDW", "Neutrophils", "Lymphocytes"],
        "LFT": ["Bilirubin", "ALT", "AST", "SGPT", "SGOT", "ALP", "Albumin", "GGT"],
        "KFT": ["Creatinine", "BUN", "Urea", "Sodium", "Potassium", "Uric Acid"],
        "HbA1c": ["HbA1c", "A1c", "Glycated"],
        "Lipid Profile": ["Cholesterol", "Triglycerides", "HDL", "LDL"],
        "TFT": ["TSH", "Free T4", "T3", "T4"]
    }

    results = {panel: {} for panel in keywords.keys()}
    
    # Split text into lines for easier processing
    lines = text.split('\n')
    
    for line in lines:
        # Regex to find: Parameter Name ... Number (optionally with unit)
        # Matches patterns like "Hemoglobin 14.5 g/dL" or "ALT: 45"
        match = re.search(r'([a-zA-Z\s\d\(\)\/]+?)\s*[:\-]?\s*(\d+\.?\d*)\s*([a-zA-Z\%/\d³µ\s]*)', line)
        
        if match:
            param_name = match.group(1).strip()
            value = match.group(2).strip()
            
            # Check which panel this parameter belongs to
            for panel, param_list in keywords.items():
                for ref_param in param_list:
                    # Case-insensitive partial matching
                    if ref_param.lower() in param_name.lower():
                        try:
                            results[panel][ref_param] = float(value)
                        except ValueError:
                            continue
                            
    return results
