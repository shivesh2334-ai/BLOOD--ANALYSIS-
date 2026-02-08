import streamlit as st
import json
import re
import os
from PIL import Image
import io
from utils import extract_text_from_pdf, extract_text_from_image, parse_blood_report
from reference_ranges import (
    CBC_REFERENCE_RANGES, LFT_REFERENCE_RANGES, KFT_REFERENCE_RANGES,
    HBA1C_REFERENCE_RANGES, LIPID_PROFILE_REFERENCE_RANGES,
    IRON_STUDIES_REFERENCE_RANGES, TFT_REFERENCE_RANGES,
    analyze_parameter, get_differential_diagnosis, get_sample_quality_assessment,
    get_parameter_discussion, get_comprehensive_analysis
)
from ai_review import get_ai_review

# Page Configuration
st.set_page_config(
    page_title="Blood Investigation Analyzer",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #c0392b;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #c0392b;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        padding: 0.5rem 0;
        border-bottom: 2px solid #3498db;
        margin: 1rem 0;
    }
    .parameter-box-normal {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
    }
    .parameter-box-low {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
    }
    .parameter-box-high {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
    }
    .parameter-box-critical {
        background-color: #f5c6cb;
        border: 3px solid #721c24;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
    }
    .param-name {
        font-size: 0.85rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
    .param-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 5px 0;
    }
    .param-unit {
        font-size: 0.75rem;
        color: #7f8c8d;
    }
    .param-range {
        font-size: 0.7rem;
        color: #95a5a6;
        margin-top: 3px;
    }
    .param-status {
        font-size: 0.8rem;
        font-weight: bold;
        margin-top: 5px;
    }
    .diagnosis-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    .quality-box {
        background-color: #e8f4f8;
        border: 2px solid #17a2b8;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .critical-alert {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

def get_status_color(status):
    """Return color based on status"""
    if status == "Normal":
        return "#28a745"
    elif status == "Low" or status == "High":
        return "#ffc107" if "borderline" in status.lower() else "#dc3545"
    elif "Critical" in status:
        return "#721c24"
    return "#6c757d"

def get_box_class(status):
    """Return CSS class based on status"""
    if status == "Normal":
        return "parameter-box-normal"
    elif "Critical" in status:
        return "parameter-box-critical"
    elif "Low" in status:
        return "parameter-box-low"
    elif "High" in status:
        return "parameter-box-high"
    return "parameter-box-normal"

def render_parameter_box(name, value, unit, ref_range, status):
    """Render a parameter box with appropriate styling"""
    box_class = get_box_class(status)
    status_color = get_status_color(status)
    
    value_color = "#28a745" if status == "Normal" else "#dc3545" if "Critical" in status else "#e67e22" if ("Low" in status or "High" in status) else "#2c3e50"
    
    html = f"""
    <div class="{box_class}">
        <div class="param-name">{name}</div>
        <div class="param-value" style="color: {value_color};">{value}</div>
        <div class="param-unit">{unit}</div>
        <div class="param-range">Ref: {ref_range}</div>
        <div class="param-status" style="color: {status_color};">{'⚠️ ' if status != 'Normal' else '✅ '}{status}</div>
    </div>
    """
    return html

def display_parameters_grid(parameters, reference_ranges, panel_name):
    """Display parameters in a grid layout with colored boxes"""
    if not parameters:
        st.warning(f"No {panel_name} parameters detected in the uploaded document.")
        return {}
    
    analysis_results = {}
    cols_per_row = 4
    param_list = list(parameters.items())
    
    for i in range(0, len(param_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(param_list):
                param_name, param_value = param_list[i + j]
                
                # Find matching reference range
                ref_info = None
                for ref_key, ref_val in reference_ranges.items():
                    if ref_key.lower() == param_name.lower() or any(
                        alias.lower() == param_name.lower() 
                        for alias in ref_val.get('aliases', [])
                    ):
                        ref_info = ref_val
                        break
                
                if ref_info:
                    analysis = analyze_parameter(param_name, param_value, ref_info)
                    analysis_results[param_name] = analysis
                    
                    with col:
                        st.markdown(
                            render_parameter_box(
                                param_name,
                                param_value,
                                ref_info.get('unit', ''),
                                f"{ref_info.get('low', 'N/A')} - {ref_info.get('high', 'N/A')}",
                                analysis['status']
                            ),
                            unsafe_allow_html=True
                        )
                else:
                    with col:
                        st.markdown(
                            render_parameter_box(
                                param_name,
                                param_value,
                                '',
                                'N/A',
                                'Unknown'
                            ),
                            unsafe_allow_html=True
                        )
    
    return analysis_results

def display_analysis_section(analysis_results, panel_name):
    """Display detailed analysis for abnormal parameters"""
    abnormal_params = {k: v for k, v in analysis_results.items() if v['status'] != 'Normal'}
    
    if not abnormal_params:
        st.success(f"✅ All {panel_name} parameters are within normal limits.")
        return
    
    st.markdown(f'<div class="sub-header">🔍 Detailed Analysis - {panel_name}</div>', unsafe_allow_html=True)
    
    # Critical values alert
    critical_params = {k: v for k, v in abnormal_params.items() if 'Critical' in v['status']}
    if critical_params:
        st.markdown('<div class="critical-alert">🚨 CRITICAL VALUES DETECTED - Immediate clinical attention may be required!</div>', unsafe_allow_html=True)
        for param, analysis in critical_params.items():
            st.error(f"**{param}**: {analysis['value']} {analysis.get('unit', '')} - {analysis['status']}")
    
    # Detailed analysis for each abnormal parameter
    for param, analysis in abnormal_params.items():
        with st.expander(f"{'🔴' if 'Critical' in analysis['status'] else '🟡'} {param}: {analysis['value']} - {analysis['status']}", expanded='Critical' in analysis['status']):
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Parameter Details:**")
                st.write(f"- **Value:** {analysis['value']} {analysis.get('unit', '')}")
                st.write(f"- **Reference Range:** {analysis.get('ref_low', 'N/A')} - {analysis.get('ref_high', 'N/A')} {analysis.get('unit', '')}")
                st.write(f"- **Status:** {analysis['status']}")
                if analysis.get('deviation_pct') is not None:
                    st.write(f"- **Deviation:** {analysis['deviation_pct']:.1f}% from normal range")
                
                # Parameter-specific discussion
                discussion = get_parameter_discussion(param, analysis['status'])
                if discussion:
                    st.markdown("**Clinical Discussion:**")
                    st.markdown(f'<div class="diagnosis-box">{discussion}</div>', unsafe_allow_html=True)
            
            with col2:
                # Differential diagnosis
                differentials = get_differential_diagnosis(param, analysis['status'])
                if differentials:
                    st.markdown("**Differential Diagnosis:**")
                    for i, dx in enumerate(differentials, 1):
                        st.markdown(f'<div class="diagnosis-box"><strong>{i}. {dx["diagnosis"]}</strong><br>{dx["discussion"]}</div>', unsafe_allow_html=True)

def manual_entry_form():
    """Display manual entry form for blood parameters"""
    st.markdown('<div class="sub-header">📝 Manual Parameter Entry</div>', unsafe_allow_html=True)
    
    panel_type = st.selectbox(
        "Select Investigation Panel",
        ["CBC", "LFT", "KFT", "HbA1c", "Lipid Profile", "Iron Studies", "TFT"]
    )
    
    parameters = {}
    
    if panel_type == "CBC":
        st.markdown("#### Complete Blood Count (CBC)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            parameters['WBC'] = st.number_input("WBC (×10³/µL)", min_value=0.0, max_value=500.0, value=0.0, step=0.1, format="%.2f")
            parameters['RBC'] = st.number_input("RBC (×10⁶/µL)", min_value=0.0, max_value=15.0, value=0.0, step=0.01, format="%.2f")
            parameters['Hemoglobin'] = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=25.0, value=0.0, step=0.1, format="%.1f")
        with col2:
            parameters['Hematocrit'] = st.number_input("Hematocrit (%)", min_value=0.0, max_value=80.0, value=0.0, step=0.1, format="%.1f")
            parameters['MCV'] = st.number_input("MCV (fL)", min_value=0.0, max_value=150.0, value=0.0, step=0.1, format="%.1f")
            parameters['MCH'] = st.number_input("MCH (pg)", min_value=0.0, max_value=50.0, value=0.0, step=0.1, format="%.1f")
        with col3:
            parameters['MCHC'] = st.number_input("MCHC (g/dL)", min_value=0.0, max_value=40.0, value=0.0, step=0.1, format="%.1f")
            parameters['RDW'] = st.number_input("RDW (%)", min_value=0.0, max_value=30.0, value=0.0, step=0.1, format="%.1f")
            parameters['Platelet Count'] = st.number_input("Platelet Count (×10³/µL)", min_value=0.0, max_value=2000.0, value=0.0, step=1.0, format="%.0f")
        with col4:
            parameters['MPV'] = st.number_input("MPV (fL)", min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
            parameters['Neutrophils'] = st.number_input("Neutrophils (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
            parameters['Lymphocytes'] = st.number_input("Lymphocytes (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            parameters['Monocytes'] = st.number_input("Monocytes (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
        with col6:
            parameters['Eosinophils'] = st.number_input("Eosinophils (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
        with col7:
            parameters['Basophils'] = st.number_input("Basophils (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
        with col8:
            parameters['Reticulocyte Count'] = st.number_input("Reticulocyte Count (%)", min_value=0.0, max_value=30.0, value=0.0, step=0.1, format="%.1f")
    
    elif panel_type == "LFT":
        st.markdown("#### Liver Function Tests (LFT)")
        col1, col2, col3 = st.columns(3)
        with col1:
            parameters['Total Bilirubin'] = st.number_input("Total Bilirubin (mg/dL)", min_value=0.0, max_value=50.0, value=0.0, step=0.1, format="%.1f")
            parameters['Direct Bilirubin'] = st.number_input("Direct Bilirubin (mg/dL)", min_value=0.0, max_value=30.0, value=0.0, step=0.1, format="%.1f")
            parameters['Indirect Bilirubin'] = st.number_input("Indirect Bilirubin (mg/dL)", min_value=0.0, max_value=30.0, value=0.0, step=0.1, format="%.1f")
        with col2:
            parameters['AST'] = st.number_input("AST/SGOT (U/L)", min_value=0.0, max_value=5000.0, value=0.0, step=1.0, format="%.0f")
            parameters['ALT'] = st.number_input("ALT/SGPT (U/L)", min_value=0.0, max_value=5000.0, value=0.0, step=1.0, format="%.0f")
            parameters['ALP'] = st.number_input("ALP (U/L)", min_value=0.0, max_value=2000.0, value=0.0, step=1.0, format="%.0f")
        with col3:
            parameters['GGT'] = st.number_input("GGT (U/L)", min_value=0.0, max_value=2000.0, value=0.0, step=1.0, format="%.0f")
            parameters['Total Protein'] = st.number_input("Total Protein (g/dL)", min_value=0.0, max_value=15.0, value=0.0, step=0.1, format="%.1f")
            parameters['Albumin'] = st.number_input("Albumin (g/dL)", min_value=0.0, max_value=7.0, value=0.0, step=0.1, format="%.1f")
    
    elif panel_type == "KFT":
        st.markdown("#### Kidney Function Tests (KFT)")
        col1, col2, col3 = st.columns(3)
        with col1:
            parameters['BUN'] = st.number_input("BUN (mg/dL)", min_value=0.0, max_value=200.0, value=0.0, step=0.1, format="%.1f")
            parameters['Creatinine'] = st.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=30.0, value=0.0, step=0.01, format="%.2f")
        with col2:
            parameters['Uric Acid'] = st.number_input("Uric Acid (mg/dL)", min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
            parameters['eGFR'] = st.number_input("eGFR (mL/min/1.73m²)", min_value=0.0, max_value=200.0, value=0.0, step=1.0, format="%.0f")
        with col3:
            parameters['Sodium'] = st.number_input("Sodium (mEq/L)", min_value=0.0, max_value=200.0, value=0.0, step=0.1, format="%.1f")
            parameters['Potassium'] = st.number_input("Potassium (mEq/L)", min_value=0.0, max_value=10.0, value=0.0, step=0.01, format="%.2f")
    
    elif panel_type == "HbA1c":
        st.markdown("#### HbA1c / Glycated Hemoglobin")
        parameters['HbA1c'] = st.number_input("HbA1c (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
        parameters['Estimated Average Glucose'] = st.number_input("Estimated Average Glucose (mg/dL)", min_value=0.0, max_value=500.0, value=0.0, step=1.0, format="%.0f")
    
    elif panel_type == "Lipid Profile":
        st.markdown("#### Lipid Profile")
        col1, col2 = st.columns(2)
        with col1:
            parameters['Total Cholesterol'] = st.number_input("Total Cholesterol (mg/dL)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0, format="%.0f")
            parameters['LDL'] = st.number_input("LDL Cholesterol (mg/dL)", min_value=0.0, max_value=500.0, value=0.0, step=1.0, format="%.0f")
            parameters['HDL'] = st.number_input("HDL Cholesterol (mg/dL)", min_value=0.0, max_value=200.0, value=0.0, step=1.0, format="%.0f")
        with col2:
            parameters['Triglycerides'] = st.number_input("Triglycerides (mg/dL)", min_value=0.0, max_value=5000.0, value=0.0, step=1.0, format="%.0f")
            parameters['VLDL'] = st.number_input("VLDL (mg/dL)", min_value=0.0, max_value=200.0, value=0.0, step=1.0, format="%.0f")
            parameters['TC/HDL Ratio'] = st.number_input("TC/HDL Ratio", min_value=0.0, max_value=20.0, value=0.0, step=0.1, format="%.1f")
    
    elif panel_type == "Iron Studies":
        st.markdown("#### Iron Studies")
        col1, col2 = st.columns(2)
        with col1:
            parameters['Serum Iron'] = st.number_input("Serum Iron (µg/dL)", min_value=0.0, max_value=500.0, value=0.0, step=1.0, format="%.0f")
            parameters['TIBC'] = st.number_input("TIBC (µg/dL)", min_value=0.0, max_value=800.0, value=0.0, step=1.0, format="%.0f")
        with col2:
            parameters['Ferritin'] = st.number_input("Ferritin (ng/mL)", min_value=0.0, max_value=5000.0, value=0.0, step=1.0, format="%.0f")
            parameters['Transferrin Saturation'] = st.number_input("Transferrin Saturation (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, format="%.1f")
    
    elif panel_type == "TFT":
        st.markdown("#### Thyroid Function Tests (TFT)")
        col1, col2, col3 = st.columns(3)
        with col1:
            parameters['TSH'] = st.number_input("TSH (mIU/L)", min_value=0.0, max_value=100.0, value=0.0, step=0.01, format="%.3f")
        with col2:
            parameters['Free T3'] = st.number_input("Free T3 (pg/mL)", min_value=0.0, max_value=30.0, value=0.0, step=0.01, format="%.2f")
        with col3:
            parameters['Free T4'] = st.number_input("Free T4 (ng/dL)", min_value=0.0, max_value=10.0, value=0.0, step=0.01, format="%.2f")
    
    # Remove zero values
    parameters = {k: v for k, v in parameters.items() if v > 0}
    
    return panel_type, parameters


def get_reference_for_panel(panel_type):
    """Return appropriate reference ranges for the selected panel"""
    panel_map = {
        "CBC": CBC_REFERENCE_RANGES,
        "LFT": LFT_REFERENCE_RANGES,
        "KFT": KFT_REFERENCE_RANGES,
        "HbA1c": HBA1C_REFERENCE_RANGES,
        "Lipid Profile": LIPID_PROFILE_REFERENCE_RANGES,
        "Iron Studies": IRON_STUDIES_REFERENCE_RANGES,
        "TFT": TFT_REFERENCE_RANGES
    }
    return panel_map.get(panel_type, {})


def main():
    # Header
    st.markdown('<div class="main-header">🩸 Blood Investigation Analyzer</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #7f8c8d; font-size: 1.1rem;">
    Comprehensive analysis of CBC, LFT, KFT, HbA1c, Lipid Profile, Iron Studies, and Thyroid Function Tests
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/blood-sample.png", width=80)
        st.markdown("### 🏥 Patient Information")
        patient_name = st.text_input("Patient Name", placeholder="Enter patient name")
        patient_age = st.number_input("Age", min_value=0, max_value=120, value=30)
        patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        patient_id = st.text_input("Patient ID", placeholder="Enter patient ID")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        input_method = st.radio(
            "Input Method",
            ["📄 Upload Document", "📝 Manual Entry"],
            help="Choose how to input blood investigation results"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This application analyzes blood investigation reports including:
        - **CBC** - Complete Blood Count
        - **LFT** - Liver Function Tests
        - **KFT** - Kidney Function Tests
        - **HbA1c** - Glycated Hemoglobin
        - **Lipid Profile**
        - **Iron Studies**
        - **TFT** - Thyroid Function Tests
        
        Upload a PDF or image of your report, or manually enter values.
        """)
        
        st.markdown("---")
        st.caption("⚠️ **Disclaimer**: This tool is for educational and screening purposes only. Always consult a qualified healthcare professional for medical advice and treatment decisions.")
    
    # Main Content
    if "📄 Upload Document" in input_method:
        st.markdown('<div class="sub-header">📤 Upload Blood Investigation Report</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your blood report (PDF, JPG, JPEG, PNG)",
            type=['pdf', 'jpg', 'jpeg', 'png'],
            help="Upload a clear image or PDF of your blood investigation report"
        )
        
        if uploaded_file is not None:
            file_type = uploaded_file.type
            
            # Display uploaded file info
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.info(f"📁 **File:** {uploaded_file.name}")
            with col_info2:
                st.info(f"📊 **Type:** {file_type}")
            with col_info3:
                st.info(f"💾 **Size:** {uploaded_file.size / 1024:.1f} KB")
            
            # Extract text
            with st.spinner("🔄 Extracting data from document..."):
                try:
                    if 'pdf' in file_type:
                        extracted_text = extract_text_from_pdf(uploaded_file)
                    else:
                        extracted_text = extract_text_from_image(uploaded_file)
                    
                    if extracted_text:
                        with st.expander("📜 View Extracted Text", expanded=False):
                            st.text_area("Raw extracted text:", extracted_text, height=200)
                        
                        # Parse the extracted text
                        parsed_results = parse_blood_report(extracted_text)
                        
                        if parsed_results:
                            st.success(f"✅ Successfully extracted {sum(len(v) for v in parsed_results.values())} parameters from the document.")
                            
                            # Store results in session state
                            st.session_state['parsed_results'] = parsed_results
                            st.session_state['patient_info'] = {
                                'name': patient_name,
                                'age': patient_age,
                                'gender': patient_gender,
                                'id': patient_id
                            }
                            
                            # Display results by panel
                            all_analysis = {}
                            for panel_name, params in parsed_results.items():
                                if params:
                                    ref_ranges = get_reference_for_panel(panel_name)
                                    st.markdown(f'<div class="sub-header">📊 {panel_name} Results</div>', unsafe_allow_html=True)
                                    analysis = display_parameters_grid(params, ref_ranges, panel_name)
                                    all_analysis[panel_name] = analysis
                                    
                                    # Sample quality assessment
                                    if panel_name == "CBC":
                                        quality = get_sample_quality_assessment(params)
                                        st.markdown(f'<div class="quality-box"><strong>🔬 Sample Quality Assessment:</strong><br>{quality}</div>', unsafe_allow_html=True)
                                    
                                    # Detailed analysis
                                    display_analysis_section(analysis, panel_name)
                                    st.markdown("---")
                            
                            # Comprehensive analysis
                            if all_analysis:
                                st.markdown('<div class="sub-header">📋 Comprehensive Analysis Summary</div>', unsafe_allow_html=True)
                                comprehensive = get_comprehensive_analysis(all_analysis, patient_age, patient_gender)
                                st.markdown(comprehensive, unsafe_allow_html=True)
                            
                            # Store for AI review
                            st.session_state['all_analysis'] = all_analysis
                        else:
                            st.warning("⚠️ Could not parse blood parameters from the extracted text. Please try manual entry.")
                    else:
                        st.error("❌ Could not extract text from the document. Please ensure the document is clear and readable, or use manual entry.")
                
                except Exception as e:
                    st.error(f"❌ Error processing document: {str(e)}")
                    st.info("💡 Tip: Try uploading a clearer image or use manual entry instead.")
    
    else:  # Manual Entry
        panel_type, parameters = manual_entry_form()
        
        if st.button("🔍 Analyze Results", type="primary", use_container_width=True):
            if parameters:
                ref_ranges = get_reference_for_panel(panel_type)
                
                st.markdown(f'<div class="sub-header">📊 {panel_type} Results</div>', unsafe_allow_html=True)
                analysis = display_parameters_grid(parameters, ref_ranges, panel_type)
                
                # Sample quality assessment for CBC
                if panel_type == "CBC":
                    quality = get_sample_quality_assessment(parameters)
                    st.markdown(f'<div class="quality-box"><strong>🔬 Sample Quality Assessment:</strong><br>{quality}</div>', unsafe_allow_html=True)
                
                # Detailed analysis
                display_analysis_section(analysis, panel_type)
                
                # Comprehensive analysis
                all_analysis = {panel_type: analysis}
                st.markdown('<div class="sub-header">📋 Comprehensive Analysis Summary</div>', unsafe_allow_html=True)
                comprehensive = get_comprehensive_analysis(all_analysis, patient_age, patient_gender)
                st.markdown(comprehensive, unsafe_allow_html=True)
                
                # Store for AI review
                st.session_state['all_analysis'] = all_analysis
                st.session_state['parsed_results'] = {panel_type: parameters}
                st.session_state['patient_info'] = {
                    'name': patient_name,
                    'age': patient_age,
                    'gender': patient_gender,
                    'id': patient_id
                }
            else:
                st.warning("⚠️ Please enter at least one parameter value.")
    
    # AI Review Section
    st.markdown("---")
    st.markdown('<div class="sub-header">🤖 AI-Powered Review</div>', unsafe_allow_html=True)
    
    ai_provider = st.selectbox(
        "Select AI Provider",
        ["OpenAI (GPT-4)", "Google (Gemini)", "Local Analysis (No API needed)"],
        help="Choose an AI provider for advanced review. Local analysis uses built-in rules."
    )
    
    if ai_provider != "Local Analysis (No API needed)":
        api_key = st.text_input(
            f"Enter {'OpenAI' if 'OpenAI' in ai_provider else 'Google'} API Key",
            type="password",
            help="Your API key is not stored and is only used for this session."
        )
    else:
        api_key = None
    
    if st.button("🧠 Generate AI Review", type="secondary", use_container_width=True):
        if 'all_analysis' in st.session_state and st.session_state['all_analysis']:
            with st.spinner("🔄 Generating AI-powered review..."):
                patient_info = st.session_state.get('patient_info', {})
                parsed_results = st.session_state.get('parsed_results', {})
                
                review = get_ai_review(
                    parsed_results,
                    st.session_state['all_analysis'],
                    patient_info,
                    ai_provider,
                    api_key
                )
                
                st.markdown('<div class="sub-header">📝 AI Review Report</div>', unsafe_allow_html=True)
                st.markdown(review, unsafe_allow_html=True)
                
                # Download option
                st.download_button(
                    label="📥 Download AI Review Report",
                    data=review,
                    file_name=f"ai_review_{patient_info.get('name', 'patient')}_{patient_info.get('id', 'unknown')}.md",
                    mime="text/markdown"
                )
        else:
            st.warning("⚠️ Please analyze blood parameters first before requesting an AI review.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #95a5a6; padding: 20px;">
        <p>🩸 Blood Investigation Analyzer v2.0</p>
        <p style="font-size: 0.8rem;">Based on evidence-based hematology references including UpToDate clinical resources.</p>
        <p style="font-size: 0.75rem;">⚠️ This tool is for educational and screening purposes only. Not a substitute for professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
