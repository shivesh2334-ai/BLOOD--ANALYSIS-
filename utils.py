import re
import io
from typing import Dict, Optional

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            # Try with pdfplumber as fallback
            try:
                import pdfplumber
                uploaded_file.seek(0)
                with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except ImportError:
                pass
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_image(uploaded_file) -> str:
    """Extract text from uploaded image file using OCR"""
    try:
        from PIL import Image
        import pytesseract
        
        image = Image.open(io.BytesIO(uploaded_file.read()))
        
        # Preprocess image for better OCR
        image = image.convert('L')  # Convert to grayscale
        
        # Extract text
        text = pytesseract.image_to_string(image, config='--psm 6')
        
        return text.strip()
    except ImportError:
        # If pytesseract is not available, try easyocr
        try:
            import easyocr
            uploaded_file.seek(0)
            reader = easyocr.Reader(['en'])
            result = reader.readtext(uploaded_file.read(), detail=0)
            return '\n'.join(result)
        except ImportError:
            raise Exception(
                "OCR library not available. Please install pytesseract or easyocr. "
                "For local deployment, install Tesseract OCR engine. "
                "Alternatively, use manual entry mode."
            )
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")


def parse_blood_report(text: str) -> Dict[str, Dict[str, float]]:
    """Parse extracted text to identify blood parameters and their values"""
    
    results = {
        "CBC": {},
        "LFT": {},
        "KFT": {},
        "HbA1c": {},
        "Lipid Profile": {},
        "Iron Studies": {},
        "TFT": {}
    }
    
    # Normalize text
    text_lower = text.lower()
    lines = text.split('\n')
    
    # CBC patterns
    cbc_patterns = {
        'WBC': [
            r'(?:wbc|white\s*blood\s*cell|leucocyte|leukocyte)\s*(?:count)?\s*[:\-]?\s*([\d.]+)',
            r'(?:total\s*)?(?:wbc|leucocyte)\s*(?:count)?\s*[:\-]?\s*([\d.]+)',
        ],
        'RBC': [
            r'(?:rbc|red\s*blood\s*cell|erythrocyte)\s*(?:count)?\s*[:\-]?\s*([\d.]+)',
        ],
        'Hemoglobin': [
            r'(?:h[ae]moglobin|hgb|hb)\s*[:\-]?\s*([\d.]+)',
        ],
        'Hematocrit': [
            r'(?:h[ae]matocrit|hct|pcv|packed\s*cell\s*volume)\s*[:\-]?\s*([\d.]+)',
        ],
        'MCV': [
            r'(?:mcv|mean\s*corpuscular\s*volume)\s*[:\-]?\s*([\d.]+)',
        ],
        'MCH': [
            r'(?:mch(?!c)|mean\s*corpuscular\s*h[ae]moglobin(?!\s*con))\s*[:\-]?\s*([\d.]+)',
        ],
        'MCHC': [
            r'(?:mchc|mean\s*corpuscular\s*h[ae]moglobin\s*con(?:centration)?)\s*[:\-]?\s*([\d.]+)',
        ],
        'RDW': [
            r'(?:rdw|red\s*(?:cell\s*)?distribution\s*width)\s*(?:[-%]?\s*(?:cv|sd))?\s*[:\-]?\s*([\d.]+)',
        ],
        'Platelet Count': [
            r'(?:platelet|plt)\s*(?:count)?\s*[:\-]?\s*([\d.]+)',
        ],
        'MPV': [
            r'(?:mpv|mean\s*platelet\s*volume)\s*[:\-]?\s*([\d.]+)',
        ],
        'Neutrophils': [
            r'(?:neutrophil|neut|segmented)\s*(?:s|%|count)?\s*[:\-]?\s*([\d.]+)\s*%?',
        ],
        'Lymphocytes': [
            r'(?:lymphocyte|lymph)\s*(?:s|%|count)?\s*[:\-]?\s*([\d.]+)\s*%?',
        ],
        'Monocytes': [
            r'(?:monocyte|mono)\s*(?:s|%|count)?\s*[:\-]?\s*([\d.]+)\s*%?',
        ],
        'Eosinophils': [
            r'(?:eosinophil|eos)\s*(?:s|%|count)?\s*[:\-]?\s*([\d.]+)\s*%?',
        ],
        'Basophils': [
            r'(?:basophil|baso)\s*(?:s|%|count)?\s*[:\-]?\s*([\d.]+)\s*%?',
        ],
        'Reticulocyte Count': [
            r'(?:reticulocyte|retic)\s*(?:count|%)?\s*[:\-]?\s*([\d.]+)',
        ],
        'ESR': [
            r'(?:esr|erythrocyte\s*sedimentation\s*rate)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # LFT patterns
    lft_patterns = {
        'Total Bilirubin': [
            r'(?:total\s*bilirubin|t[\.\s]*bilirubin|bil[\.\s]*total)\s*[:\-]?\s*([\d.]+)',
        ],
        'Direct Bilirubin': [
            r'(?:direct\s*bilirubin|d[\.\s]*bilirubin|conjugated\s*bilirubin)\s*[:\-]?\s*([\d.]+)',
        ],
        'Indirect Bilirubin': [
            r'(?:indirect\s*bilirubin|unconjugated\s*bilirubin)\s*[:\-]?\s*([\d.]+)',
        ],
        'AST': [
            r'(?:ast|sgot|aspartate\s*(?:amino)?transaminase)\s*[:\-]?\s*([\d.]+)',
        ],
        'ALT': [
            r'(?:alt|sgpt|alanine\s*(?:amino)?transaminase)\s*[:\-]?\s*([\d.]+)',
        ],
        'ALP': [
            r'(?:alp|alkaline\s*phosphatase)\s*[:\-]?\s*([\d.]+)',
        ],
        'GGT': [
            r'(?:ggt|gamma\s*(?:glutamyl\s*)?transferase|γ[\-\s]*gt)\s*[:\-]?\s*([\d.]+)',
        ],
        'Total Protein': [
            r'(?:total\s*protein|t[\.\s]*protein)\s*[:\-]?\s*([\d.]+)',
        ],
        'Albumin': [
            r'(?:albumin|alb)\s*[:\-]?\s*([\d.]+)',
        ],
        'Globulin': [
            r'(?:globulin|glob)\s*[:\-]?\s*([\d.]+)',
        ],
        'A/G Ratio': [
            r'(?:a/g\s*ratio|albumin/globulin)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # KFT patterns
    kft_patterns = {
        'BUN': [
            r'(?:bun|blood\s*urea\s*nitrogen)\s*[:\-]?\s*([\d.]+)',
        ],
        'Creatinine': [
            r'(?:creatinine|creat)\s*[:\-]?\s*([\d.]+)',
        ],
        'Uric Acid': [
            r'(?:uric\s*acid)\s*[:\-]?\s*([\d.]+)',
        ],
        'eGFR': [
            r'(?:egfr|estimated\s*gfr|glomerular\s*filtration)\s*[:\-]?\s*([\d.]+)',
        ],
        'Sodium': [
            r'(?:sodium|na)\s*[:\-]?\s*([\d.]+)',
        ],
        'Potassium': [
            r'(?:potassium|k)\s*[:\-]?\s*([\d.]+)',
        ],
        'Chloride': [
            r'(?:chloride|cl)\s*[:\-]?\s*([\d.]+)',
        ],
        'Calcium': [
            r'(?:calcium|ca)\s*[:\-]?\s*([\d.]+)',
        ],
        'Phosphorus': [
            r'(?:phosphorus|phosphate|phos)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # HbA1c patterns
    hba1c_patterns = {
        'HbA1c': [
            r'(?:hba1c|hb\s*a1c|glycated\s*h[ae]moglobin|glycosylated\s*h[ae]moglobin|a1c)\s*[:\-]?\s*([\d.]+)',
        ],
        'Estimated Average Glucose': [
            r'(?:estimated\s*average\s*glucose|eag|avg\s*glucose)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # Lipid Profile patterns
    lipid_patterns = {
        'Total Cholesterol': [
            r'(?:total\s*cholesterol|t[\.\s]*cholesterol|cholesterol[\s,]*total)\s*[:\-]?\s*([\d.]+)',
        ],
        'LDL': [
            r'(?:ldl|low\s*density\s*lipoprotein)\s*(?:cholesterol)?\s*[:\-]?\s*([\d.]+)',
        ],
        'HDL': [
            r'(?:hdl|high\s*density\s*lipoprotein)\s*(?:cholesterol)?\s*[:\-]?\s*([\d.]+)',
        ],
        'Triglycerides': [
            r'(?:triglycerides?|tg)\s*[:\-]?\s*([\d.]+)',
        ],
        'VLDL': [
            r'(?:vldl|very\s*low\s*density)\s*(?:cholesterol)?\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # Iron Studies patterns
    iron_patterns = {
        'Serum Iron': [
            r'(?:serum\s*iron|s[\.\s]*iron|iron[\s,]*serum)\s*[:\-]?\s*([\d.]+)',
        ],
        'TIBC': [
            r'(?:tibc|total\s*iron\s*binding\s*capacity)\s*[:\-]?\s*([\d.]+)',
        ],
        'Ferritin': [
            r'(?:ferritin|s[\.\s]*ferritin|serum\s*ferritin)\s*[:\-]?\s*([\d.]+)',
        ],
        'Transferrin Saturation': [
            r'(?:transferrin\s*sat(?:uration)?|tsat|iron\s*sat(?:uration)?)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # TFT patterns
    tft_patterns = {
        'TSH': [
            r'(?:tsh|thyroid\s*stimulating\s*hormone|thyrotropin)\s*[:\-]?\s*([\d.]+)',
        ],
        'Free T3': [
            r'(?:free\s*t3|ft3|free\s*triiodothyronine)\s*[:\-]?\s*([\d.]+)',
        ],
        'Free T4': [
            r'(?:free\s*t4|ft4|free\s*thyroxine)\s*[:\-]?\s*([\d.]+)',
        ],
        'Total T3': [
            r'(?:total\s*t3|t3[\s,]*total)\s*[:\-]?\s*([\d.]+)',
        ],
        'Total T4': [
            r'(?:total\s*t4|t4[\s,]*total)\s*[:\-]?\s*([\d.]+)',
        ],
    }
    
    # Map patterns to result categories
    pattern_map = {
        "CBC": cbc_patterns,
        "LFT": lft_patterns,
        "KFT": kft_patterns,
        "HbA1c": hba1c_patterns,
        "Lipid Profile": lipid_patterns,
        "Iron Studies": iron_patterns,
        "TFT": tft_patterns,
    }
    
    # Extract values
    for category, patterns in pattern_map.items():
        for param_name, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        value = float(match.group(1))
                        results[category][param_name] = value
                    except (ValueError, IndexError):
                        continue
                    break  # Stop after first match for this parameter
    
    # Remove empty categories
    results = {k: v for k, v in results.items() if v}
    
    return results
