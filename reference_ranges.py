"""
reference_ranges.py
Reference ranges and analysis logic for blood investigation parameters.
"""

# ==========================================
# 1. REFERENCE RANGE DEFINITIONS
# ==========================================

CBC_REFERENCE_RANGES = {
    'WBC': {'low': 4.0, 'high': 11.0, 'unit': '×10³/µL', 'critical_low': 2.0, 'critical_high': 30.0, 'aliases': ['White Blood Cell', 'Leucocyte', 'Leukocyte', 'Total WBC']},
    'RBC': {'low': 4.0, 'high': 5.5, 'unit': '×10⁶/µL', 'critical_low': 2.0, 'critical_high': 7.5, 'aliases': ['Red Blood Cell', 'Erythrocyte', 'Total RBC']},
    'Hemoglobin': {'low': 12.0, 'high': 17.5, 'unit': 'g/dL', 'critical_low': 7.0, 'critical_high': 20.0, 'aliases': ['Hb', 'Hgb', 'Haemoglobin']},
    'Hematocrit': {'low': 36.0, 'high': 54.0, 'unit': '%', 'critical_low': 20.0, 'critical_high': 60.0, 'aliases': ['HCT', 'PCV', 'Packed Cell Volume']},
    'MCV': {'low': 80.0, 'high': 100.0, 'unit': 'fL', 'critical_low': 50.0, 'critical_high': 130.0, 'aliases': ['Mean Corpuscular Volume']},
    'MCH': {'low': 27.0, 'high': 33.0, 'unit': 'pg', 'critical_low': 15.0, 'critical_high': 40.0, 'aliases': ['Mean Corpuscular Hemoglobin']},
    'MCHC': {'low': 32.0, 'high': 36.0, 'unit': 'g/dL', 'critical_low': 25.0, 'critical_high': 38.0, 'aliases': ['Mean Corpuscular Hemoglobin Concentration']},
    'RDW': {'low': 11.5, 'high': 14.5, 'unit': '%', 'critical_low': None, 'critical_high': 25.0, 'aliases': ['Red Cell Distribution Width']},
    'Platelet Count': {'low': 150.0, 'high': 400.0, 'unit': '×10³/µL', 'critical_low': 50.0, 'critical_high': 1000.0, 'aliases': ['PLT', 'Platelets']},
    'MPV': {'low': 6.0, 'high': 12.0, 'unit': 'fL', 'critical_low': None, 'critical_high': None, 'aliases': ['Mean Platelet Volume']},
    'Neutrophils': {'low': 40.0, 'high': 70.0, 'unit': '%', 'aliases': ['Neut', 'Segs']},
    'Lymphocytes': {'low': 20.0, 'high': 40.0, 'unit': '%', 'aliases': ['Lymph']},
    'Monocytes': {'low': 2.0, 'high': 8.0, 'unit': '%', 'aliases': ['Mono']},
    'Eosinophils': {'low': 1.0, 'high': 4.0, 'unit': '%', 'aliases': ['Eos']},
    'Basophils': {'low': 0.0, 'high': 1.0, 'unit': '%', 'aliases': ['Baso']},
}

LFT_REFERENCE_RANGES = {
    'Total Bilirubin': {'low': 0.1, 'high': 1.2, 'unit': 'mg/dL', 'critical_high': 15.0, 'aliases': ['T. Bilirubin']},
    'Direct Bilirubin': {'low': 0.0, 'high': 0.3, 'unit': 'mg/dL', 'aliases': ['Conjugated Bilirubin']},
    'AST': {'low': 5.0, 'high': 40.0, 'unit': 'U/L', 'critical_high': 1000.0, 'aliases': ['SGOT']},
    'ALT': {'low': 5.0, 'high': 40.0, 'unit': 'U/L', 'critical_high': 1000.0, 'aliases': ['SGPT']},
    'ALP': {'low': 44.0, 'high': 147.0, 'unit': 'U/L', 'aliases': ['Alkaline Phosphatase']},
    'Albumin': {'low': 3.5, 'high': 5.5, 'unit': 'g/dL', 'critical_low': 2.0, 'aliases': ['Alb']},
}

KFT_REFERENCE_RANGES = {
    'BUN': {'low': 7.0, 'high': 20.0, 'unit': 'mg/dL', 'critical_high': 100.0, 'aliases': ['Urea']},
    'Creatinine': {'low': 0.6, 'high': 1.2, 'unit': 'mg/dL', 'critical_high': 10.0, 'aliases': ['Serum Creatinine']},
    'Sodium': {'low': 136.0, 'high': 145.0, 'unit': 'mEq/L', 'critical_low': 120.0, 'critical_high': 160.0},
    'Potassium': {'low': 3.5, 'high': 5.0, 'unit': 'mEq/L', 'critical_low': 2.5, 'critical_high': 6.5},
}

HBA1C_REFERENCE_RANGES = {
    'HbA1c': {'low': 4.0, 'high': 5.6, 'unit': '%', 'critical_high': 14.0, 'aliases': ['A1c']},
}

LIPID_PROFILE_REFERENCE_RANGES = {
    'Total Cholesterol': {'low': 0.0, 'high': 200.0, 'unit': 'mg/dL', 'aliases': ['TC']},
    'LDL': {'low': 0.0, 'high': 100.0, 'unit': 'mg/dL', 'aliases': ['LDL-C']},
    'HDL': {'low': 40.0, 'high': 60.0, 'unit': 'mg/dL', 'aliases': ['HDL-C']},
    'Triglycerides': {'low': 0.0, 'high': 150.0, 'unit': 'mg/dL', 'aliases': ['TG']},
}

IRON_STUDIES_REFERENCE_RANGES = {
    'Serum Iron': {'low': 60.0, 'high': 170.0, 'unit': 'µg/dL', 'aliases': ['Iron']},
    'Ferritin': {'low': 12.0, 'high': 300.0, 'unit': 'ng/mL'},
}

TFT_REFERENCE_RANGES = {
    'TSH': {'low': 0.4, 'high': 4.0, 'unit': 'mIU/L', 'critical_low': 0.01, 'critical_high': 50.0},
    'Free T4': {'low': 0.8, 'high': 1.8, 'unit': 'ng/dL', 'aliases': ['FT4']},
}

# ==========================================
# 2. CORE ANALYSIS FUNCTIONS
# ==========================================

def analyze_parameter(name, value, ref_info):
    """Analyze a single value against low, high, and critical levels."""
    try:
        val = float(value)
    except:
        return {'status': 'Error', 'value': value, 'deviation_pct': 0}

    low = ref_info.get('low')
    high = ref_info.get('high')
    crit_low = ref_info.get('critical_low')
    crit_high = ref_info.get('critical_high')

    status = 'Normal'
    if crit_low is not None and val < crit_low: status = 'Critical Low'
    elif crit_high is not None and val > crit_high: status = 'Critical High'
    elif low is not None and val < low: status = 'Low'
    elif high is not None and val > high: status = 'High'

    # Calculate deviation %
    dev = 0
    if status in ['Low', 'Critical Low'] and low: dev = ((low - val) / low) * 100
    elif status in ['High', 'Critical High'] and high: dev = ((val - high) / high) * 100

    return {
        'name': name, 'value': val, 'status': status,
        'unit': ref_info.get('unit', ''), 'ref_low': low, 'ref_high': high,
        'deviation_pct': dev
    }

def get_sample_quality_assessment(cbc_params):
    """Rule of Threes (RBC x 3 = Hb, Hb x 3 = Hct)"""
    hb = float(cbc_params.get('Hemoglobin', 0) or cbc_params.get('Hb', 0) or 0)
    rbc = float(cbc_params.get('RBC', 0) or 0)
    hct = float(cbc_params.get('Hematocrit', 0) or cbc_params.get('HCT', 0) or 0)
    
    notes = []
    if rbc > 0 and hb > 0:
        if abs((rbc * 3) - hb) > 1.5: notes.append("Hb/RBC mismatch (Rule of 3 failed).")
    if hb > 0 and hct > 0:
        if abs((hb * 3) - hct) > 3: notes.append("Hb/Hct mismatch (Rule of 3 failed).")
    
    return "✅ Sample appears reliable." if not notes else f"⚠️ {', '.join(notes)}"

def get_parameter_discussion(param, status):
    """Provides a brief clinical explanation of the finding."""
    discussions = {
        'Hemoglobin': {'Low': 'Lowered oxygen-carrying capacity (Anemia).', 'High': 'Increased blood viscosity (Polycythemia).'},
        'WBC': {'High': 'Suggests infection, inflammation, or stress response.', 'Low': 'Increased risk of infection (Leukopenia).'},
        'Platelet Count': {'Low': 'Increased risk of bleeding.', 'High': 'Risk of clotting/thrombosis.'},
        'ALT': {'High': 'Indicator of acute liver cell injury.'},
        'Creatinine': {'High': 'Suggests reduced kidney filtration capability.'}
    }
    return discussions.get(param, {}).get(status.split()[-1], "Requires clinical correlation with patient symptoms.")

def get_differential_diagnosis(param, status):
    """Returns possible causes for the abnormal result."""
    # Simplified logic for example
    if param in ['Hemoglobin', 'Hb'] and 'Low' in status:
        return [
            {'diagnosis': 'Iron Deficiency Anemia', 'discussion': 'Most common cause due to blood loss or diet.'},
            {'diagnosis': 'Chronic Disease', 'discussion': 'Anemia caused by long-term inflammation.'}
        ]
    if param == 'ALT' and 'High' in status:
        return [
            {'diagnosis': 'Viral Hepatitis', 'discussion': 'Inflammation of the liver due to virus.'},
            {'diagnosis': 'Fatty Liver (NAFLD)', 'discussion': 'Common in metabolic syndrome.'}
        ]
    return [{'diagnosis': 'Non-specific finding', 'discussion': 'Consult primary physician.'}]

def get_comprehensive_analysis(all_analysis, age, gender):
    """Synthesizes all results into a summary paragraph."""
    abnormals = []
    for panel in all_analysis.values():
        for p_name, data in panel.items():
            if data['status'] != 'Normal':
                abnormals.append(p_name)
    
    if not abnormals:
        return f"### Summary\nResults for this {age}-year-old {gender} are **entirely normal**."
    
    return f"### Summary\nFor this {age}-year-old {gender}, the analysis identified abnormalities in **{', '.join(abnormals)}**. These findings warrant clinical correlation."
