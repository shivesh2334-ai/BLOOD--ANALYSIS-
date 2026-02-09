import streamlit as st
import pandas as pd
from utils import extract_text_from_pdf, extract_text_from_image, parse_blood_report
from reference_ranges import (
    CBC_REFERENCE_RANGES, LFT_REFERENCE_RANGES, KFT_REFERENCE_RANGES,
    HBA1C_REFERENCE_RANGES, LIPID_PROFILE_REFERENCE_RANGES,
    IRON_STUDIES_REFERENCE_RANGES, TFT_REFERENCE_RANGES,
    analyze_parameter, get_sample_quality_assessment,
    get_parameter_discussion, get_differential_diagnosis, get_comprehensive_analysis
)
from ai_review import get_ai_review

# --- UI STYLING ---
def apply_custom_css():
    st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; font-weight: bold; color: #c0392b; text-align: center; border-bottom: 3px solid #c0392b; margin-bottom: 20px; }
        .sub-header { font-size: 1.4rem; font-weight: bold; color: #2c3e50; border-bottom: 2px solid #3498db; margin: 20px 0 10px 0; }
        .param-card { border-radius: 10px; padding: 15px; margin: 5px; text-align: center; border: 2px solid #ddd; height: 100%; }
        .status-Normal { background-color: #d4edda; border-color: #28a745; }
        .status-Low, .status-High { background-color: #fff3cd; border-color: #ffc107; }
        .status-Critical { background-color: #f8d7da; border-color: #dc3545; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); } 100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); } }
        .diagnosis-box { background-color: #f8f9fa; border-left: 5px solid #3498db; padding: 10px; margin: 5px 0; border-radius: 5px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENT FUNCTIONS ---
def render_parameter_card(name, value, unit, ref_range, status):
    status_class = f"status-{status.split()[-1]}" if "Critical" not in status else "status-Critical"
    val_color = "#dc3545" if "Critical" in status or "High" in status or "Low" in status else "#28a745"
    
    return f"""
    <div class="param-card {status_class}">
        <div style="font-size: 0.8rem; font-weight: bold; color: #555;">{name}</div>
        <div style="font-size: 1.6rem; font-weight: bold; color: {val_color};">{value}</div>
        <div style="font-size: 0.7rem; color: #666;">{unit}</div>
        <div style="font-size: 0.7rem; color: #888;">Ref: {ref_range}</div>
        <div style="font-size: 0.8rem; font-weight: bold; margin-top: 5px;">{status}</div>
    </div>
    """

def display_results_grid(parameters, panel_name):
    """Dynamically analyzes and displays parameters in a grid."""
    ref_library = {
        "CBC": CBC_REFERENCE_RANGES, "LFT": LFT_REFERENCE_RANGES, 
        "KFT": KFT_REFERENCE_RANGES, "HbA1c": HBA1C_REFERENCE_RANGES,
        "Lipid Profile": LIPID_PROFILE_REFERENCE_RANGES, 
        "Iron Studies": IRON_STUDIES_REFERENCE_RANGES, "TFT": TFT_REFERENCE_RANGES
    }.get(panel_name, {})

    analysis_results = {}
    cols = st.columns(4)
    
    for idx, (name, val) in enumerate(parameters.items()):
        # Resolve reference info
        ref_info = next((v for k, v in ref_library.items() if k.lower() == name.lower() or name in v.get('aliases', [])), None)
        
        if ref_info:
            analysis = analyze_parameter(name, val, ref_info)
            analysis_results[name] = analysis
            with cols[idx % 4]:
                st.markdown(render_parameter_card(
                    name, val, ref_info.get('unit', ''),
                    f"{ref_info.get('low')} - {ref_info.get('high')}",
                    analysis['status']
                ), unsafe_allow_html=True)
    return analysis_results

def dynamic_manual_form(panel_name):
    """Generates input fields based on reference range definitions."""
    ref_library = {
        "CBC": CBC_REFERENCE_RANGES, "LFT": LFT_REFERENCE_RANGES, 
        "KFT": KFT_REFERENCE_RANGES, "HbA1c": HBA1C_REFERENCE_RANGES,
        "Lipid Profile": LIPID_PROFILE_REFERENCE_RANGES, 
        "Iron Studies": IRON_STUDIES_REFERENCE_RANGES, "TFT": TFT_REFERENCE_RANGES
    }.get(panel_name, {})

    data = {}
    st.write(f"### Enter {panel_name} Values")
    cols = st.columns(3)
    for idx, (param, info) in enumerate(ref_library.items()):
        with cols[idx % 3]:
            val = st.number_input(f"{param} ({info['unit']})", min_value=0.0, step=0.1, key=f"manual_{param}")
            if val > 0: data[param] = val
    return data

# --- MAIN APP ---
def main():
    st.set_page_config(page_title="Blood Analyzer Pro", page_icon="🩸", layout="wide")
    apply_custom_css()

    st.markdown('<div class="main-header">🩸 Blood Investigation Analyzer</div>', unsafe_allow_html=True)

    # Sidebar: Patient Context
    with st.sidebar:
        st.header("🏥 Patient Context")
        p_name = st.text_input("Name", "John Doe")
        p_age = st.number_input("Age", 0, 120, 35)
        p_gender = st.selectbox("Gender", ["Male", "Female"])
        input_method = st.radio("Input Method", ["📄 Upload Report", "📝 Manual Entry"])
        st.markdown("---")
        st.caption("⚠️ For clinical screening only. Not a definitive diagnosis.")

    # Processing Logic
    all_panel_data = {}

    if input_method == "📄 Upload Report":
        uploaded_file = st.file_uploader("Upload Blood Report (PDF/Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
        if uploaded_file:
            with st.spinner("🔍 Extracting Clinical Data..."):
                text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == 'application/pdf' else extract_text_from_image(uploaded_file)
                all_panel_data = parse_blood_report(text)
                if not all_panel_data:
                    st.error("Could not parse data. Please try Manual Entry.")
    else:
        panel_choice = st.selectbox("Select Panel", ["CBC", "LFT", "KFT", "HbA1c", "Lipid Profile", "Iron Studies", "TFT"])
        manual_data = dynamic_manual_form(panel_choice)
        if st.button("Analyze Manual Entry"):
            all_panel_data = {panel_choice: manual_data}

    # Analysis Display
    if all_panel_data:
        full_analysis_cache = {}
        
        for panel, params in all_panel_data.items():
            if params:
                st.markdown(f'<div class="sub-header">📊 {panel} Analysis</div>', unsafe_allow_html=True)
                panel_analysis = display_results_grid(params, panel)
                full_analysis_cache[panel] = panel_analysis
                
                # CBC Specific Quality Check
                if panel == "CBC":
                    quality = get_sample_quality_assessment(params)
                    st.info(f"**🔬 Lab Quality Note:** {quality}")

                # Display Abnormalities & Differentials
                abnormal = {k: v for k, v in panel_analysis.items() if v['status'] != 'Normal'}
                if abnormal:
                    for p, report in abnormal.items():
                        with st.expander(f"⚠️ Findings for {p} ({report['status']})"):
                            c1, c2 = st.columns(2)
                            c1.markdown(f"**Discussion:**\n{get_parameter_discussion(p, report['status'])}")
                            diffs = get_differential_diagnosis(p, report['status'])
                            c2.markdown("**Differential Diagnosis:**")
                            for d in diffs:
                                c2.markdown(f'<div class="diagnosis-box"><b>{d["diagnosis"]}</b><br>{d["discussion"]}</div>', unsafe_allow_html=True)

        # AI Synthesis
        st.markdown("---")
        if st.button("🧠 Generate Comprehensive AI Review"):
            st.session_state['ready_for_ai'] = True

        if st.session_state.get('ready_for_ai'):
            with st.spinner("Generating AI review..."):
                # Simplified provider logic for example
                ai_output = get_ai_review(all_panel_data, full_analysis_cache, {"name": p_name, "age": p_age, "gender": p_gender}, "Local Analysis", None)
                st.markdown(ai_output, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
