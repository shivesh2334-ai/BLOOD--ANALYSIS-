"""
Reference ranges and analysis logic for blood investigation parameters.
Based on standard clinical hematology and biochemistry references.
"""

# ==========================================
# REFERENCE RANGE DEFINITIONS
# ==========================================

CBC_REFERENCE_RANGES = {
    'WBC': {
        'low': 4.0, 'high': 11.0, 'unit': '×10³/µL',
        'critical_low': 2.0, 'critical_high': 30.0,
        'aliases': ['White Blood Cell', 'Leucocyte', 'Leukocyte', 'Total WBC']
    },
    'RBC': {
        'low': 4.0, 'high': 5.5, 'unit': '×10⁶/µL',
        'critical_low': 2.0, 'critical_high': 7.5,
        'aliases': ['Red Blood Cell', 'Erythrocyte', 'Total RBC'],
        'male_low': 4.5, 'male_high': 5.5,
        'female_low': 4.0, 'female_high': 5.0
    },
    'Hemoglobin': {
        'low': 12.0, 'high': 17.5, 'unit': 'g/dL',
        'critical_low': 7.0, 'critical_high': 20.0,
        'aliases': ['Hb', 'Hgb', 'Haemoglobin'],
        'male_low': 13.5, 'male_high': 17.5,
        'female_low': 12.0, 'female_high': 15.5
    },
    'Hematocrit': {
        'low': 36.0, 'high': 54.0, 'unit': '%',
        'critical_low': 20.0, 'critical_high': 60.0,
        'aliases': ['HCT', 'PCV', 'Packed Cell Volume', 'Haematocrit'],
        'male_low': 38.0, 'male_high': 54.0,
        'female_low': 36.0, 'female_high': 48.0
    },
    'MCV': {
        'low': 80.0, 'high': 100.0, 'unit': 'fL',
        'critical_low': 50.0, 'critical_high': 130.0,
        'aliases': ['Mean Corpuscular Volume']
    },
    'MCH': {
        'low': 27.0, 'high': 33.0, 'unit': 'pg',
        'critical_low': 15.0, 'critical_high': 40.0,
        'aliases': ['Mean Corpuscular Hemoglobin']
    },
    'MCHC': {
        'low': 32.0, 'high': 36.0, 'unit': 'g/dL',
        'critical_low': 25.0, 'critical_high': 38.0,
        'aliases': ['Mean Corpuscular Hemoglobin Concentration']
    },
    'RDW': {
        'low': 11.5, 'high': 14.5, 'unit': '%',
        'critical_low': None, 'critical_high': 25.0,
        'aliases': ['Red Cell Distribution Width', 'RDW-CV']
    },
    'Platelet Count': {
        'low': 150.0, 'high': 400.0, 'unit': '×10³/µL',
        'critical_low': 50.0, 'critical_high': 1000.0,
        'aliases': ['PLT', 'Platelets', 'Thrombocyte Count']
    },
    'MPV': {
        'low': 6.0, 'high': 12.0, 'unit': 'fL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Mean Platelet Volume']
    },
    'Neutrophils': {
        'low': 40.0, 'high': 70.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Neut', 'Segmented Neutrophils', 'Segs']
    },
    'Lymphocytes': {
        'low': 20.0, 'high': 40.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Lymph']
    },
    'Monocytes': {
        'low': 2.0, 'high': 8.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Mono']
    },
    'Eosinophils': {
        'low': 1.0, 'high': 4.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Eos']
    },
    'Basophils': {
        'low': 0.0, 'high': 1.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Baso']
    },
    'Reticulocyte Count': {
        'low': 0.5, 'high': 2.5, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Retic', 'Reticulocytes']
    },
    'ESR': {
        'low': 0.0, 'high': 20.0, 'unit': 'mm/hr',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Erythrocyte Sedimentation Rate'],
        'male_low': 0, 'male_high': 15,
        'female_low': 0, 'female_high': 20
    },
}

LFT_REFERENCE_RANGES = {
    'Total Bilirubin': {
        'low': 0.1, 'high': 1.2, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 15.0,
        'aliases': ['T. Bilirubin', 'Bil Total']
    },
    'Direct Bilirubin': {
        'low': 0.0, 'high': 0.3, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 10.0,
        'aliases': ['D. Bilirubin', 'Conjugated Bilirubin']
    },
    'Indirect Bilirubin': {
        'low': 0.1, 'high': 0.9, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Unconjugated Bilirubin']
    },
    'AST': {
        'low': 5.0, 'high': 40.0, 'unit': 'U/L',
        'critical_low': None, 'critical_high': 1000.0,
        'aliases': ['SGOT', 'Aspartate Aminotransferase']
    },
    'ALT': {
        'low': 5.0, 'high': 40.0, 'unit': 'U/L',
        'critical_low': None, 'critical_high': 1000.0,
        'aliases': ['SGPT', 'Alanine Aminotransferase']
    },
    'ALP': {
        'low': 44.0, 'high': 147.0, 'unit': 'U/L',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Alkaline Phosphatase']
    },
    'GGT': {
        'low': 0.0, 'high': 60.0, 'unit': 'U/L',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Gamma GT', 'Gamma Glutamyl Transferase']
    },
    'Total Protein': {
        'low': 6.0, 'high': 8.3, 'unit': 'g/dL',
        'critical_low': 4.0, 'critical_high': None,
        'aliases': ['T. Protein']
    },
    'Albumin': {
        'low': 3.5, 'high': 5.5, 'unit': 'g/dL',
        'critical_low': 2.0, 'critical_high': None,
        'aliases': ['Alb']
    },
    'Globulin': {
        'low': 2.0, 'high': 3.5, 'unit': 'g/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Glob']
    },
    'A/G Ratio': {
        'low': 1.0, 'high': 2.5, 'unit': '',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Albumin/Globulin Ratio']
    },
}

KFT_REFERENCE_RANGES = {
    'BUN': {
        'low': 7.0, 'high': 20.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 100.0,
        'aliases': ['Blood Urea Nitrogen', 'Urea']
    },
    'Creatinine': {
        'low': 0.6, 'high': 1.2, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 10.0,
        'aliases': ['Creat', 'Serum Creatinine'],
        'male_low': 0.7, 'male_high': 1.3,
        'female_low': 0.6, 'female_high': 1.1
    },
    'Uric Acid': {
        'low': 3.0, 'high': 7.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 13.0,
        'aliases': ['Urate'],
        'male_low': 3.5, 'male_high': 7.2,
        'female_low': 2.6, 'female_high': 6.0
    },
    'eGFR': {
        'low': 90.0, 'high': 120.0, 'unit': 'mL/min/1.73m²',
        'critical_low': 15.0, 'critical_high': None,
        'aliases': ['Estimated GFR', 'Glomerular Filtration Rate']
    },
    'Sodium': {
        'low': 136.0, 'high': 145.0, 'unit': 'mEq/L',
        'critical_low': 120.0, 'critical_high': 160.0,
        'aliases': ['Na', 'Na+']
    },
    'Potassium': {
        'low': 3.5, 'high': 5.0, 'unit': 'mEq/L',
        'critical_low': 2.5, 'critical_high': 6.5,
        'aliases': ['K', 'K+']
    },
    'Chloride': {
        'low': 98.0, 'high': 106.0, 'unit': 'mEq/L',
        'critical_low': 80.0, 'critical_high': 120.0,
        'aliases': ['Cl', 'Cl-']
    },
    'Calcium': {
        'low': 8.5, 'high': 10.5, 'unit': 'mg/dL',
        'critical_low': 6.0, 'critical_high': 13.0,
        'aliases': ['Ca', 'Ca++', 'Total Calcium']
    },
    'Phosphorus': {
        'low': 2.5, 'high': 4.5, 'unit': 'mg/dL',
        'critical_low': 1.0, 'critical_high': 8.0,
        'aliases': ['Phosphate', 'PO4']
    },
}

HBA1C_REFERENCE_RANGES = {
    'HbA1c': {
        'low': 4.0, 'high': 5.6, 'unit': '%',
        'critical_low': None, 'critical_high': 14.0,
        'aliases': ['Glycated Hemoglobin', 'A1c', 'Glycosylated Hemoglobin']
    },
    'Estimated Average Glucose': {
        'low': 70.0, 'high': 126.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['eAG', 'Average Glucose']
    },
}

LIPID_PROFILE_REFERENCE_RANGES = {
    'Total Cholesterol': {
        'low': 0.0, 'high': 200.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 400.0,
        'aliases': ['TC', 'Cholesterol Total']
    },
    'LDL': {
        'low': 0.0, 'high': 100.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 300.0,
        'aliases': ['LDL Cholesterol', 'Low Density Lipoprotein', 'LDL-C']
    },
    'HDL': {
        'low': 40.0, 'high': 60.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['HDL Cholesterol', 'High Density Lipoprotein', 'HDL-C'],
        'male_low': 40.0, 'female_low': 50.0
    },
    'Triglycerides': {
        'low': 0.0, 'high': 150.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': 500.0,
        'aliases': ['TG', 'Triacylglycerol']
    },
    'VLDL': {
        'low': 2.0, 'high': 30.0, 'unit': 'mg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['VLDL Cholesterol', 'Very Low Density Lipoprotein']
    },
    'TC/HDL Ratio': {
        'low': 0.0, 'high': 5.0, 'unit': '',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Cholesterol/HDL Ratio']
    },
}

IRON_STUDIES_REFERENCE_RANGES = {
    'Serum Iron': {
        'low': 60.0, 'high': 170.0, 'unit': 'µg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Iron', 'Fe'],
        'male_low': 65.0, 'male_high': 175.0,
        'female_low': 50.0, 'female_high': 170.0
    },
    'TIBC': {
        'low': 250.0, 'high': 370.0, 'unit': 'µg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['Total Iron Binding Capacity']
    },
    'Ferritin': {
        'low': 12.0, 'high': 300.0, 'unit': 'ng/mL',
        'critical_low': None, 'critical_high': 1000.0,
        'aliases': ['Serum Ferritin'],
        'male_low': 20.0, 'male_high': 300.0,
        'female_low': 12.0, 'female_high': 150.0
    },
    'Transferrin Saturation': {
        'low': 20.0, 'high': 50.0, 'unit': '%',
        'critical_low': None, 'critical_high': None,
        'aliases': ['TSAT', 'Iron Saturation']
    },
}

TFT_REFERENCE_RANGES = {
    'TSH': {
        'low': 0.4, 'high': 4.0, 'unit': 'mIU/L',
        'critical_low': 0.01, 'critical_high': 50.0,
        'aliases': ['Thyroid Stimulating Hormone', 'Thyrotropin']
    },
    'Free T3': {
        'low': 2.3, 'high': 4.2, 'unit': 'pg/mL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['FT3', 'Free Triiodothyronine']
    },
    'Free T4': {
        'low': 0.8, 'high': 1.8, 'unit': 'ng/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['FT4', 'Free Thyroxine']
    },
    'Total T3': {
        'low': 80.0, 'high': 200.0, 'unit': 'ng/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['T3 Total']
    },
    'Total T4': {
        'low': 5.0, 'high': 12.0, 'unit': 'µg/dL',
        'critical_low': None, 'critical_high': None,
        'aliases': ['T4 Total']
    },
}

# ==========================================
# ANALYSIS LOGIC FUNCTIONS
# ==========================================

def analyze_parameter(name, value, ref_info, gender=None):
    """Analyze a single parameter against reference ranges, considering gender if available"""
    result = {
        'name': name,
        'value': value,
        'unit': ref_info.get('unit', ''),
        'status': 'Normal',
        'deviation_pct': None
    }
    
    try:
        val = float(value)
    except (ValueError, TypeError):
        result['status'] = 'Unable to analyze'
        return result

    # Determine which reference range to use based on gender
    ref_low = ref_info.get('low')
    ref_high = ref_info.get('high')
    
    if gender:
        gender_low = ref_info.get(f'{gender.lower()}_low')
        gender_high = ref_info.get(f'{gender.lower()}_high')
        if gender_low is not None: ref_low = gender_low
        if gender_high is not None: ref_high = gender_high
    
    result['ref_low'] = ref_low
    result['ref_high'] = ref_high
    
    critical_low = ref_info.get('critical_low')
    critical_high = ref_info.get('critical_high')
    
    # Check critical values
    if critical_low is not None and val < critical_low:
        result['status'] = 'Critical Low'
    elif critical_high is not None and val > critical_high:
        result['status'] = 'Critical High'
    elif ref_low is not None and val < ref_low:
        result['status'] = 'Low'
    elif ref_high is not None and val > ref_high:
        result['status'] = 'High'
    else:
        result['status'] = 'Normal'
        
    # Calculate deviation percentage
    if result['status'] != 'Normal':
        if val < ref_low and ref_low != 0:
            result['deviation_pct'] = ((ref_low - val) / ref_low) * 100
        elif val > ref_high and ref_high != 0:
            result['deviation_pct'] = ((val - ref_high) / ref_high) * 100
    else:
        # Position in range
        if ref_low is not None and ref_high is not None and ref_high > ref_low:
            mid = (ref_low + ref_high) / 2
            range_span = ref_high - ref_low
            result['deviation_pct'] = ((val - mid) / (range_span / 2)) * 100
            
    return result

def get_sample_quality_assessment(cbc_params):
    """Assess sample quality based on CBC parameters - Rule of Threes and other checks"""
    issues = []
    quality_notes = []
    
    # Extract common keys or aliases
    rbc = cbc_params.get('RBC', 0)
    hb = cbc_params.get('Hemoglobin') or cbc_params.get('Hb', 0) or cbc_params.get('Hgb', 0)
    hct = cbc_params.get('Hematocrit') or cbc_params.get('HCT', 0) or cbc_params.get('PCV', 0)
    mcv = cbc_params.get('MCV', 0)
    mchc = cbc_params.get('MCHC', 0)
    
    # Rule of Threes (RBC x 3 = Hb)
    if rbc > 0 and hb > 0:
        expected_hb = rbc * 3
        hb_deviation = abs(hb - expected_hb) / expected_hb * 100
        if hb_deviation > 10:
            issues.append(f"⚠️ Rule of Threes (RBC × 3 ≈ Hb): Expected Hb ~{expected_hb:.1f}, got {hb:.1f} (deviation: {hb_deviation:.1f}%).")
        else:
            quality_notes.append(f"✅ Rule of Threes (RBC × 3 ≈ Hb): PASS")
    
    # Rule of Threes (Hb x 3 = HCT)
    if hb > 0 and hct > 0:
        expected_hct = hb * 3
        hct_deviation = abs(hct - expected_hct) / expected_hct * 100
        if hct_deviation > 10:
            issues.append(f"⚠️ Rule of Threes (Hb × 3 ≈ HCT): Expected HCT ~{expected_hct:.1f}%, got {hct:.1f}% (deviation: {hct_deviation:.1f}%).")
        else:
            quality_notes.append(f"✅ Rule of Threes (Hb × 3 ≈ HCT): PASS")
    
    # MCHC check (Spurious results/Hemolysis indicator)
    if mchc > 0:
        if mchc > 37:
            issues.append(f"⚠️ Spurious Result Alert: MCHC ({mchc:.1f}) is physiologically high (>37). Consider lipemia, cold agglutinins, or instrument error.")
        elif mchc < 30:
            issues.append(f"⚠️ Low MCHC ({mchc:.1f}): Suggests severe hypochromia.")

    # Differential Check
    diff_params = ['Neutrophils', 'Lymphocytes', 'Monocytes', 'Eosinophils', 'Basophils']
    diff_values = [cbc_params.get(p, 0) for p in diff_params]
    diff_sum = sum(diff_values)
    if diff_sum > 0:
        if abs(diff_sum - 100) > 5:
            issues.append(f"⚠️ WBC Differential sums to {diff_sum:.1f}% (Expected ~100%).")
        else:
            quality_notes.append(f"✅ WBC Differential Sum: PASS ({diff_sum:.1f}%)")

    return {
        'is_reliable': len(issues) == 0,
        'issues': issues,
        'notes': quality_notes
    }

def classify_anemia(hb, mcv, mchc, rdw):
    """Morphological classification of anemia"""
    if hb >= 12.0: return "No anemia detected."
    
    classification = ""
    if mcv < 80: classification = "Microcytic "
    elif mcv > 100: classification = "Macrocytic "
    else: classification = "Normocytic "
        
    if mchc < 32: classification += "Hypochromic Anemia"
    else: classification += "Normochromic Anemia"
        
    if rdw > 14.5: classification += " with Anisocytosis"
        
    # Correlation Note
    if "Microcytic" in classification:
        note = "Commonly seen in Iron Deficiency or Thalassemia."
    elif "Macrocytic" in classification:
        note = "Commonly seen in B12/Folate deficiency or Liver Disease."
    else:
        note = "Commonly seen in Anemia of Chronic Disease or Acute Blood Loss."
        
    return f"{classification}. {note}"

def analyze_liver_injury_pattern(alt, alp):
    """Determines Hepatocellular vs Cholestatic pattern via R-ratio"""
    # R = (ALT_Value / ALT_ULN) / (ALP_Value / ALP_ULN)
    alt_r = alt / 40.0
    alp_r = alp / 147.0
    if alp_r == 0: return "Insufficient data."
    
    r_ratio = alt_r / alp_r
    if r_ratio >= 5: return "Pattern: Hepatocellular (e.g., Viral/Toxic Hepatitis)"
    elif r_ratio <= 2: return "Pattern: Cholestatic (e.g., Biliary Obstruction)"
    else: return "Pattern: Mixed Liver Injury"

def process_full_report(patient_data, gender=None):
    """Main processing pipeline for a blood report dictionary"""
    analysis_results = []
    summary = {'critical': [], 'high': [], 'low': [], 'interpretations': []}
    
    # Aggregate all reference libraries
    all_refs = {**CBC_REFERENCE_RANGES, **LFT_REFERENCE_RANGES, **KFT_REFERENCE_RANGES, 
                **HBA1C_REFERENCE_RANGES, **LIPID_PROFILE_REFERENCE_RANGES, 
                **IRON_STUDIES_REFERENCE_RANGES, **TFT_REFERENCE_RANGES}
    
    # Map input keys to official names via aliases
    alias_map = {}
    for official_name, info in all_refs.items():
        alias_map[official_name.lower()] = official_name
        for alias in info.get('aliases', []):
            alias_map[alias.lower()] = official_name

    # 1. Individual Parameter Analysis
    for key, val in patient_data.items():
        official_name = alias_map.get(key.lower())
        if official_name:
            res = analyze_parameter(official_name, val, all_refs[official_name], gender)
            analysis_results.append(res)
            
            # Populate Summary
            if 'Critical' in res['status']: summary['critical'].append(official_name)
            elif res['status'] == 'High': summary['high'].append(official_name)
            elif res['status'] == 'Low': summary['low'].append(official_name)

    # 2. Contextual Clinical Interpretations
    # Anemia Check
    hb = patient_data.get('Hb') or patient_data.get('Hemoglobin') or patient_data.get('Hgb')
    if hb and float(hb) < 12.0:
        mcv = patient_data.get('MCV', 90)
        mchc = patient_data.get('MCHC', 34)
        rdw = patient_data.get('RDW', 13)
        summary['interpretations'].append(classify_anemia(float(hb), float(mcv), float(mchc), float(rdw)))

    # Liver Check
    alt = patient_data.get('ALT') or patient_data.get('SGPT')
    alp = patient_data.get('ALP')
    if alt and alp and (float(alt) > 40 or float(alp) > 147):
        summary['interpretations'].append(analyze_liver_injury_pattern(float(alt), float(alp)))

    # 3. Sample Quality Check
    quality = get_sample_quality_assessment(patient_data)

    return {
        'results': analysis_results,
        'summary': summary,
        'quality': quality
    }

# ==========================================
# EXAMPLE EXECUTION
# ==========================================

if __name__ == "__main__":
    # Simulated Lab Data
    test_input = {
        'Hb': 9.5,
        'RBC': 3.1,
        'HCT': 29.0,
        'MCV': 72.0,
        'MCHC': 29.5,
        'RDW': 17.2,
        'WBC': 14.5,
        'ALT': 120,
        'ALP': 95,
        'Neutrophils': 75,
        'Lymphocytes': 15,
        'Monocytes': 10
    }
    
    report = process_full_report(test_input, gender='Female')
    
    print("--- BLOOD INVESTIGATION ANALYSIS ---")
    print(f"Summary: {len(report['summary']['critical'])} Critical, {len(report['summary']['high'])} High, {len(report['summary']['low'])} Low")
    
    print("\n[Interpretations]")
    for inter in report['summary']['interpretations']:
        print(f"- {inter}")
        
    print("\n[Quality Assessment]")
    for issue in report['quality']['issues']:
        print(issue)
        
    print("\n[Detailed Table]")
    print(f"{'Parameter':<20} | {'Value':<8} | {'Status':<15}")
    print("-" * 50)
    for r in report['results']:
        print(f"{r['name']:<20} | {r['value']:<8} | {r['status']:<15}")
