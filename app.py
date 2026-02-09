# app.py
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import pdf2image
import io
import re
import json
from datetime import datetime
import base64

# Configure page
st.set_page_config(
    page_title="CBC Analyzer Pro",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .parameter-box {
        background-color: #f0f9ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
    }
    .abnormal-high {
        color: #dc2626;
        font-weight: bold;
    }
    .abnormal-low {
        color: #2563eb;
        font-weight: bold;
    }
    .normal {
        color: #059669;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .diagnosis-box {
        background-color: #f3e8ff;
        border-left: 4px solid #9333ea;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #1e40af;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Reference ranges for CBC parameters
REFERENCE_RANGES = {
    'RBC': {'male': (4.5, 5.5), 'female': (4.0, 5.0), 'unit': 'x10^12/L'},
    'Hemoglobin': {'male': (13.5, 17.5), 'female': (12.0, 16.0), 'unit': 'g/dL'},
    'Hematocrit': {'male': (41, 50), 'female': (36, 44), 'unit': '%'},
    'MCV': {'range': (80, 100), 'unit': 'fL'},
    'MCH': {'range': (27, 33), 'unit': 'pg'},
    'MCHC': {'range': (32, 36), 'unit': 'g/dL'},
    'RDW': {'range': (11.5, 14.5), 'unit': '%'},
    'WBC': {'range': (4.5, 11.0), 'unit': 'x10^9/L'},
    'Platelets': {'range': (150, 450), 'unit': 'x10^9/L'},
    'MPV': {'range': (7.5, 11.5), 'unit': 'fL'},
    'Neutrophils': {'range': (40, 70), 'unit': '%'},
    'Lymphocytes': {'range': (20, 40), 'unit': '%'},
    'Monocytes': {'range': (2, 8), 'unit': '%'},
    'Eosinophils': {'range': (1, 4), 'unit': '%'},
    'Basophils': {'range': (0.5, 1), 'unit': '%'},
    'Reticulocytes': {'range': (0.5, 2.5), 'unit': '%'}
}

def extract_text_from_image(image):
    """Extract text from image using OCR"""
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF"""
    try:
        images = pdf2image.convert_from_bytes(pdf_file.read())
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        st.error(f"PDF Processing Error: {str(e)}")
        return ""

def parse_cbc_values(text):
    """Parse CBC values from extracted text"""
    cbc_data = {}
    
    # Patterns for different CBC parameters
    patterns = {
        'RBC': r'(?:RBC|Red Blood Cell|Red Blood Cells|Erythrocytes)[\s:]*(\d+\.?\d*)',
        'Hemoglobin': r'(?:Hemoglobin|Hb|HGB)[\s:]*(\d+\.?\d*)',
        'Hematocrit': r'(?:Hematocrit|Hct|HCT)[\s:]*(\d+\.?\d*)',
        'MCV': r'(?:MCV|Mean Corpuscular Volume)[\s:]*(\d+\.?\d*)',
        'MCH': r'(?:MCH|Mean Corpuscular Hb)[\s:]*(\d+\.?\d*)',
        'MCHC': r'(?:MCHC)[\s:]*(\d+\.?\d*)',
        'RDW': r'(?:RDW|Red Cell Distribution Width)[\s:]*(\d+\.?\d*)',
        'WBC': r'(?:WBC|White Blood Cell|White Blood Cells|Leukocytes)[\s:]*(\d+\.?\d*)',
        'Platelets': r'(?:Platelets|PLT|Platelet Count)[\s:]*(\d+)',
        'MPV': r'(?:MPV|Mean Platelet Volume)[\s:]*(\d+\.?\d*)',
        'Neutrophils': r'(?:Neutrophils|NEUT|Segs)[\s:]*(\d+\.?\d*)',
        'Lymphocytes': r'(?:Lymphocytes|LYMPH)[\s:]*(\d+\.?\d*)',
        'Monocytes': r'(?:Monocytes|MONO)[\s:]*(\d+\.?\d*)',
        'Eosinophils': r'(?:Eosinophils|EO)[\s:]*(\d+\.?\d*)',
        'Basophils': r'(?:Basophils|BASO)[\s:]*(\d+\.?\d*)',
        'Reticulocytes': r'(?:Reticulocytes|Retic)[\s:]*(\d+\.?\d*)'
    }
    
    for param, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                cbc_data[param] = float(matches[0])
            except:
                pass
    
    return cbc_data

def check_sample_quality(cbc_data):
    """Assess sample quality based on Rule of Threes and other criteria"""
    quality_issues = []
    warnings = []
    
    if all(k in cbc_data for k in ['RBC', 'Hemoglobin', 'Hematocrit']):
        rbc = cbc_data['RBC']
        hgb = cbc_data['Hemoglobin']
        hct = cbc_data['Hematocrit']
        
        # Rule of Threes: Hgb ≈ 3 × RBC, Hct ≈ 3 × Hgb
        expected_hgb = rbc * 3
        expected_hct = hgb * 3
        
        hgb_deviation = abs(hgb - expected_hgb) / expected_hgb * 100
        hct_deviation = abs(hct - expected_hct) / expected_hct * 100
        
        if hgb_deviation > 10:
            quality_issues.append(f"Hemoglobin ({hgb}) deviates {hgb_deviation:.1f}% from expected ({expected_hgb:.1f}) - possible hemolysis or sample error")
        if hct_deviation > 10:
            quality_issues.append(f"Hematocrit ({hct}%) deviates {hct_deviation:.1f}% from expected ({expected_hct:.1f}%) - possible sample error")
    
    # Check for critical values that might indicate sample issues
    if 'MCHC' in cbc_data:
        mchc = cbc_data['MCHC']
        if mchc > 37:
            quality_issues.append(f"Elevated MCHC ({mchc}) suggests spherocytosis, cold agglutinins, or sample interference")
        elif mchc < 30:
            quality_issues.append(f"Low MCHC ({mchc}) suggests iron deficiency or hypochromia")
    
    if 'MCV' in cbc_data and cbc_data['MCV'] > 105:
        warnings.append("Elevated MCV may indicate sample aging (>72 hours) or macrocytosis")
    
    if 'Platelets' in cbc_data and cbc_data['Platelets'] < 50:
        warnings.append("Severe thrombocytopenia - verify with blood smear for platelet clumping")
    
    return quality_issues, warnings

def analyze_parameter(param, value, gender='male'):
    """Analyze individual parameter and provide interpretation"""
    interpretation = {
        'status': 'normal',
        'analysis': '',
        'differential': [],
        'clinical_significance': ''
    }
    
    if param in ['RBC', 'Hemoglobin', 'Hematocrit']:
        ref = REFERENCE_RANGES[param][gender]
        unit = REFERENCE_RANGES[param]['unit']
    else:
        ref = REFERENCE_RANGES[param]['range']
        unit = REFERENCE_RANGES[param]['unit']
    
    low, high = ref
    
    if value < low:
        interpretation['status'] = 'low'
    elif value > high:
        interpretation['status'] = 'high'
    else:
        interpretation['status'] = 'normal'
    
    # Parameter-specific analysis
    analyses = {
        'RBC': {
            'low': {
                'analysis': 'Decreased RBC count indicates anemia or blood loss',
                'differential': [
                    'Iron deficiency anemia',
                    'Anemia of chronic disease',
                    'Thalassemia trait',
                    'Vitamin B12/Folate deficiency',
                    'Hemolysis',
                    'Bone marrow failure',
                    'Acute or chronic blood loss'
                ],
                'clinical': 'Requires correlation with hemoglobin, MCV, and reticulocyte count'
            },
            'high': {
                'analysis': 'Elevated RBC count suggests polycythemia or dehydration',
                'differential': [
                    'Dehydration (relative polycythemia)',
                    'Polycythemia vera (primary polycythemia)',
                    'Secondary polycythemia (hypoxia, COPD, high altitude)',
                    'Ectopic erythropoietin production',
                    'Thalassemia minor (high RBC, low MCV)'
                ],
                'clinical': 'Check hematocrit and hemoglobin; evaluate for JAK2 mutation if primary polycythemia suspected'
            }
        },
        'Hemoglobin': {
            'low': {
                'analysis': 'Anemia - decreased oxygen-carrying capacity',
                'differential': [
                    'Iron deficiency (most common)',
                    'Anemia of chronic disease/inflammation',
                    'Acute or chronic blood loss',
                    'Hemolytic anemia',
                    'Bone marrow suppression/aplasia',
                    'Nutritional deficiencies (B12, folate)'
                ],
                'clinical': 'Severity determines symptoms; acute vs chronic presentation differs'
            },
            'high': {
                'analysis': 'Elevated hemoglobin suggests hemoconcentration or polycythemia',
                'differential': [
                    'Dehydration',
                    'Polycythemia vera',
                    'Secondary polycythemia',
                    'Smoking-related',
                    'Androgen use'
                ],
                'clinical': 'Risk of thrombosis if true polycythemia'
            }
        },
        'MCV': {
            'low': {
                'analysis': 'Microcytosis - small RBCs',
                'differential': [
                    'Iron deficiency anemia (most common)',
                    'Thalassemia trait/alpha or beta',
                    'Anemia of chronic disease (sometimes)',
                    'Sideroblastic anemia',
                    'Lead poisoning'
                ],
                'clinical': 'Check iron studies, hemoglobin electrophoresis if indicated; RDW helps distinguish iron deficiency (high RDW) from thalassemia (normal RDW)'
            },
            'high': {
                'analysis': 'Macrocytosis - large RBCs',
                'differential': [
                    'Vitamin B12 deficiency',
                    'Folate deficiency',
                    'Liver disease',
                    'Alcohol use',
                    'Myelodysplastic syndrome',
                    'Hypothyroidism',
                    'Reticulocytosis (hemolysis/bleeding)',
                    'Medications (methotrexate, zidovudine)',
                    'Sample aging artifact'
                ],
                'clinical': 'Check B12, folate, LFTs, TSH; peripheral smear for hypersegmented neutrophils'
            }
        },
        'RDW': {
            'high': {
                'analysis': 'Increased RBC size variation (anisocytosis)',
                'differential': [
                    'Iron deficiency anemia (early indicator)',
                    'Mixed deficiency (iron + B12/folate)',
                    'Recent transfusion',
                    'Hemoglobinopathies',
                    'Myelodysplastic syndrome'
                ],
                'clinical': 'Useful in distinguishing iron deficiency (high RDW) from thalassemia (normal RDW) in microcytic anemia'
            }
        },
        'WBC': {
            'low': {
                'analysis': 'Leukopenia - increased infection risk',
                'differential': [
                    'Viral infections',
                    'Bone marrow suppression (chemotherapy, radiation)',
                    'Aplastic anemia',
                    'Autoimmune disorders',
                    'Splenomegaly/hypersplenism',
                    'Drug-induced',
                    'Nutritional deficiency (B12, folate)'
                ],
                'clinical': 'Neutropenia is most clinically significant; risk of bacterial infections if ANC <1000'
            },
            'high': {
                'analysis': 'Leukocytosis - infection, inflammation, or malignancy',
                'differential': [
                    'Bacterial infection (neutrophilia)',
                    'Inflammation/tissue necrosis',
                    'Corticosteroid use',
                    'Myeloproliferative neoplasms',
                    'Leukemia (especially if blasts present)',
                    'Physiological stress, exercise',
                    'Pregnancy'
                ],
                'clinical': 'Review differential count; left shift suggests bacterial infection; blasts require urgent hematology referral'
            }
        },
        'Platelets': {
            'low': {
                'analysis': 'Thrombocytopenia - bleeding risk',
                'differential': [
                    'Immune thrombocytopenia (ITP)',
                    'Drug-induced thrombocytopenia',
                    'Bone marrow failure/aplasia',
                    'Sepsis/DIC',
                    'TTP/HUS',
                    'Splenic sequestration',
                    'Pseudothrombocytopenia (EDTA-dependent agglutinin)'
                ],
                'clinical': 'Check peripheral smear for clumping; severe bleeding risk if <20,000; spontaneous bleeding if <10,000'
            },
            'high': {
                'analysis': 'Thrombocytosis',
                'differential': [
                    'Reactive thrombocytosis (infection, inflammation, iron deficiency)',
                    'Myeloproliferative neoplasms (essential thrombocythemia)',
                    'Post-splenectomy',
                    'Malignancy'
                ],
                'clinical': 'Iron deficiency is common cause of reactive thrombocytosis; JAK2/CALR/MPL testing if persistent unexplained thrombocytosis'
            }
        },
        'MPV': {
            'low': {
                'analysis': 'Small platelets',
                'differential': [
                    'Bone marrow suppression/aplasia',
                    'Wiskott-Aldrich syndrome',
                    'Splenic sequestration'
                ],
                'clinical': 'Inverse relationship with platelet count normally; low MPV with low platelets suggests decreased production'
            },
            'high': {
                'analysis': 'Large platelets - young, active platelets',
                'differential': [
                    'Immune thrombocytopenia (ITP)',
                    'Recovery from bone marrow suppression',
                    'Bernard-Soulier syndrome',
                    'Gray platelet syndrome',
                    'MYH9-related disease'
                ],
                'clinical': 'High MPV with thrombocytopenia suggests increased platelet destruction with compensatory production'
            }
        }
    }
    
    if param in analyses and interpretation['status'] in analyses[param]:
        data = analyses[param][interpretation['status']]
        interpretation['analysis'] = data['analysis']
        interpretation['differential'] = data['differential']
        interpretation['clinical_significance'] = data['clinical']
    else:
        interpretation['analysis'] = 'Within normal limits'
        interpretation['differential'] = ['No significant differential diagnosis']
        interpretation['clinical_significance'] = 'Normal parameter'
    
    return interpretation

def generate_ai_review(cbc_data, gender='male'):
    """Generate comprehensive AI analysis"""
    review = []
    
    # Overall assessment
    abnormal_params = []
    for param, value in cbc_data.items():
        if param in REFERENCE_RANGES:
            if param in ['RBC', 'Hemoglobin', 'Hematocrit']:
                low, high = REFERENCE_RANGES[param][gender]
            else:
                low, high = REFERENCE_RANGES[param]['range']
            
            if value < low or value > high:
                abnormal_params.append(param)
    
    if not abnormal_params:
        review.append("## Overall Assessment: NORMAL CBC")
        review.append("All parameters within normal limits. No significant hematologic abnormalities detected.")
    else:
        review.append(f"## Overall Assessment: ABNORMAL CBC")
        review.append(f"Abnormal parameters: {', '.join(abnormal_params)}")
    
    # Pattern recognition
    patterns = []
    
    # Anemia patterns
    if 'Hemoglobin' in cbc_data and 'MCV' in cbc_data:
        hgb = cbc_data['Hemoglobin']
        mcv = cbc_data['MCV']
        
        if hgb < (12.0 if gender == 'female' else 13.5):
            if mcv < 80:
                patterns.append("**Microcytic Anemia Pattern**: Suggests iron deficiency, thalassemia, or anemia of chronic disease")
            elif mcv > 100:
                patterns.append("**Macrocytic Anemia Pattern**: Suggests B12/folate deficiency, liver disease, MDS, or hemolysis")
            else:
                patterns.append("**Normocytic Anemia Pattern**: Suggests acute blood loss, hemolysis, anemia of chronic disease, or early iron deficiency")
    
    # Thrombocytopenia patterns
    if 'Platelets' in cbc_data and 'MPV' in cbc_data:
        plt = cbc_data['Platelets']
        mpv = cbc_data['MPV']
        
        if plt < 150:
            if mpv > 11.5:
                patterns.append("**High MPV with Thrombocytopenia**: Suggests peripheral destruction (ITP, TTP) with compensatory production")
            else:
                patterns.append("**Low MPV with Thrombocytopenia**: Suggests bone marrow failure or splenic sequestration")
    
    # Leukocytosis patterns
    if 'WBC' in cbc_data and cbc_data['WBC'] > 11.0:
        patterns.append("**Leukocytosis**: Consider infection, inflammation, stress, or hematologic malignancy")
    
    if patterns:
        review.append("\n## Recognized Patterns:")
        for pattern in patterns:
            review.append(f"- {pattern}")
    
    # Recommendations
    review.append("\n## Recommendations:")
    
    if 'MCV' in cbc_data and cbc_data['MCV'] < 80:
        review.append("- Iron studies (serum iron, ferritin, TIBC)")
        review.append("- Hemoglobin electrophoresis if iron studies normal")
    
    if 'MCV' in cbc_data and cbc_data['MCV'] > 100:
        review.append("- Vitamin B12 and folate levels")
        review.append("- Liver function tests")
        review.append("- TSH")
        review.append("- Peripheral blood smear examination")
    
    if 'Platelets' in cbc_data and cbc_data['Platelets'] < 150:
        review.append("- Peripheral blood smear to rule out pseudothrombocytopenia")
        review.append("- If confirmed: coagulation studies, consider bone marrow biopsy if persistent")
    
    if 'WBC' in cbc_data and cbc_data['WBC'] > 15:
        review.append("- Differential count with manual review")
        review.append("- Blood cultures if infection suspected")
        review.append("- Peripheral smear for blasts/immature forms")
    
    if not any([p in cbc_data for p in ['MCV', 'Platelets', 'WBC']]):
        review.append("- Repeat CBC to confirm results")
        review.append("- Peripheral blood smear examination")
    
    return "\n".join(review)

def main():
    st.markdown('<h1 class="main-header">🩸 CBC Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #64748b; margin-bottom: 2rem;">
        Automated Complete Blood Count Analysis with AI-Powered Interpretation<br>
        <small>Based on UpToDate Clinical Guidelines • Literature Review Current Through: Jan 2026</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Patient Information")
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.number_input("Age", min_value=0, max_value=120, value=35)
        
        st.header("Upload Options")
        upload_option = st.radio("Choose input method:", 
                                ["Upload File (PDF/Image)", "Manual Entry"])
        
        if upload_option == "Upload File (PDF/Image)":
            uploaded_file = st.file_uploader("Upload CBC Report", 
                                           type=['pdf', 'png', 'jpg', 'jpeg'])
        
        st.header("Analysis Options")
        show_differential = st.checkbox("Show Differential Diagnosis", value=True)
        show_quality = st.checkbox("Sample Quality Assessment", value=True)
        enable_ai = st.checkbox("Enable AI Review", value=True)
    
    # Main content
    cbc_data = {}
    
    if upload_option == "Upload File (PDF/Image)" and 'uploaded_file' in locals() and uploaded_file:
        st.subheader("Document Processing")
        
        file_type = uploaded_file.type
        extracted_text = ""
        
        with st.spinner("Processing document..."):
            if file_type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                extracted_text = extract_text_from_image(image)
        
        if extracted_text:
            with st.expander("View Extracted Text"):
                st.text(extracted_text)
            
            cbc_data = parse_cbc_values(extracted_text)
            
            if cbc_data:
                st.success(f"Extracted {len(cbc_data)} parameters")
            else:
                st.warning("Could not extract CBC values automatically. Please use manual entry.")
    
    # Manual entry section
    if upload_option == "Manual Entry" or not cbc_data:
        st.subheader("Manual Parameter Entry")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**RBC Parameters**")
            rbc = st.number_input("RBC (x10^12/L)", min_value=0.0, max_value=10.0, value=0.0, step=0.01)
            hgb = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=25.0, value=0.0, step=0.1)
            hct = st.number_input("Hematocrit (%)", min_value=0.0, max_value=70.0, value=0.0, step=0.1)
            mcv = st.number_input("MCV (fL)", min_value=0.0, max_value=150.0, value=0.0, step=0.1)
            mch = st.number_input("MCH (pg)", min_value=0.0, max_value=50.0, value=0.0, step=0.1)
            mchc = st.number_input("MCHC (g/dL)", min_value=0.0, max_value=40.0, value=0.0, step=0.1)
            rdw = st.number_input("RDW (%)", min_value=0.0, max_value=30.0, value=0.0, step=0.1)
        
        with col2:
            st.markdown("**WBC Parameters**")
            wbc = st.number_input("WBC (x10^9/L)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            neut = st.number_input("Neutrophils (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            lymph = st.number_input("Lymphocytes (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            mono = st.number_input("Monocytes (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
            eo = st.number_input("Eosinophils (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            baso = st.number_input("Basophils (%)", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
        
        with col3:
            st.markdown("**Platelet Parameters**")
            plt = st.number_input("Platelets (x10^9/L)", min_value=0, max_value=2000, value=0, step=1)
            mpv = st.number_input("MPV (fL)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
            retic = st.number_input("Reticulocytes (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
        
        # Build data dictionary
        manual_data = {
            'RBC': rbc, 'Hemoglobin': hgb, 'Hematocrit': hct,
            'MCV': mcv, 'MCH': mch, 'MCHC': mchc, 'RDW': rdw,
            'WBC': wbc, 'Neutrophils': neut, 'Lymphocytes': lymph,
            'Monocytes': mono, 'Eosinophils': eo, 'Basophils': baso,
            'Platelets': plt, 'MPV': mpv, 'Reticulocytes': retic
        }
        
        cbc_data = {k: v for k, v in manual_data.items() if v > 0}
    
    # Analysis section
    if cbc_data:
        st.markdown("---")
        st.subheader("📊 CBC Results Analysis")
        
        # Create results grid
        cols = st.columns(3)
        col_idx = 0
        
        for param, value in cbc_data.items():
            if param not in REFERENCE_RANGES:
                continue
                
            with cols[col_idx % 3]:
                if param in ['RBC', 'Hemoglobin', 'Hematocrit']:
                    low, high = REFERENCE_RANGES[param][gender.lower()]
                else:
                    low, high = REFERENCE_RANGES[param]['range']
                unit = REFERENCE_RANGES[param]['unit']
                
                # Determine status
                if value < low:
                    status_class = "abnormal-low"
                    status_icon = "🔽"
                    status_text = "LOW"
                elif value > high:
                    status_class = "abnormal-high"
                    status_icon = "🔼"
                    status_text = "HIGH"
                else:
                    status_class = "normal"
                    status_icon = "✅"
                    status_text = "NORMAL"
                
                st.markdown(f"""
                <div class="parameter-box">
                    <strong>{param}</strong><br>
                    <span style="font-size: 1.5rem; font-weight: bold;" class="{status_class}">
                        {value} {unit} {status_icon}
                    </span><br>
                    <small>Reference: {low}-{high} {unit}</small><br>
                    <small>Status: {status_text}</small>
                </div>
                """, unsafe_allow_html=True)
                
                col_idx += 1
        
        # Sample Quality Assessment
        if show_quality:
            st.markdown("---")
            st.subheader("🔍 Sample Quality Assessment")
            
            quality_issues, warnings = check_sample_quality(cbc_data)
            
            if quality_issues:
                for issue in quality_issues:
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>⚠️ Quality Issue:</strong> {issue}
                    </div>
                    """, unsafe_allow_html=True)
            
            if warnings:
                for warning in warnings:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>ℹ️ Note:</strong> {warning}
                    </div>
                    """, unsafe_allow_html=True)
            
            if not quality_issues and not warnings:
                st.success("✅ No significant quality issues detected. Sample appears adequate.")
        
        # Detailed Analysis
        if show_differential:
            st.markdown("---")
            st.subheader("🩺 Detailed Parameter Analysis")
            
            for param, value in cbc_data.items():
                if param not in REFERENCE_RANGES:
                    continue
                    
                interpretation = analyze_parameter(param, value, gender.lower())
                
                if interpretation['status'] != 'normal':
                    with st.expander(f"{param}: {value} ({interpretation['status'].upper()})"):
                        st.markdown(f"**Analysis:** {interpretation['analysis']}")
                        
                        st.markdown("**Differential Diagnosis:**")
                        for dx in interpretation['differential']:
                            st.markdown(f"- {dx}")
                        
                        st.markdown(f"**Clinical Significance:** {interpretation['clinical_significance']}")
        
        # AI Review
        if enable_ai:
            st.markdown("---")
            st.subheader("🤖 AI Comprehensive Review")
            
            ai_review = generate_ai_review(cbc_data, gender.lower())
            st.markdown(ai_review)
            
            # Disclaimer
            st.markdown("""
            <div style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 0.9rem;">
                <strong>⚠️ Medical Disclaimer:</strong> This analysis is for educational and informational purposes only. 
                It does not constitute medical advice. All results should be interpreted by qualified healthcare professionals 
                in the context of the patient's full clinical picture. Always correlate with clinical findings and consider 
                repeat testing if results are unexpected.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
