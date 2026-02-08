# README.md

# 🩸 CBC Analyzer Pro

A comprehensive Streamlit application for automated Complete Blood Count (CBC) analysis with AI-powered interpretation. The application extracts CBC parameters from uploaded documents (PDF, JPG, JPEG, PNG) or manual entry, provides quality assessment, differential diagnosis, and clinical correlation.

## Features

- **Document Upload**: Extract CBC values from PDF reports and images using OCR
- **Manual Entry**: Input values directly with intuitive interface
- **Quality Assessment**: Rule of Threes validation and sample quality checks
- **Parameter Analysis**: Detailed interpretation of each abnormal parameter
- **Differential Diagnosis**: Evidence-based differential diagnoses for abnormalities
- **AI Review**: Comprehensive pattern recognition and clinical recommendations
- **Clinical Guidelines**: Based on UpToDate literature (current through Jan 2026)

## Parameters Analyzed

### RBC Parameters
- RBC Count, Hemoglobin, Hematocrit
- MCV, MCH, MCHC, RDW

### WBC Parameters
- Total WBC Count
- Differential (Neutrophils, Lymphocytes, Monocytes, Eosinophils, Basophils)

### Platelet Parameters
- Platelet Count, MPV
- Reticulocyte Count

## Deployment

### Local Deployment
```bash
pip install -r requirements.txt
streamlit run app.py

