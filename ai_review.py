"""
ai_review.py
Handles AI-powered synthesis of blood report results using OpenAI, Gemini, or Local Logic.
"""

import json

def get_ai_review(parsed_results, all_analysis, patient_info, provider, api_key=None):
    """
    Main entry point for generating clinical reviews.
    """
    # 1. Prepare the data summary for the AI
    data_summary = _prepare_data_summary(all_analysis, patient_info)
    
    # 2. Route to the selected provider
    if provider == "Local Analysis (No API needed)":
        return _generate_local_review(data_summary, patient_info)
    
    if not api_key:
        return "⚠️ Error: API Key is required for AI providers. Please provide a key or select 'Local Analysis'."

    if "OpenAI" in provider:
        return _generate_openai_review(data_summary, api_key)
    
    if "Google" in provider:
        return _generate_gemini_review(data_summary, api_key)

    return "Unknown AI provider selected."

def _prepare_data_summary(all_analysis, patient_info):
    """Formats the results into a readable string for the AI prompt."""
    summary_lines = [
        f"Patient: {patient_info.get('gender', 'Unknown')}, Age {patient_info.get('age', 'Unknown')}",
        "Findings:"
    ]
    
    for panel, params in all_analysis.items():
        summary_lines.append(f"\n--- {panel} ---")
        for name, data in params.items():
            if data['status'] != 'Normal':
                summary_lines.append(f"🔴 {name}: {data['value']} {data['unit']} ({data['status']})")
            else:
                summary_lines.append(f"✅ {name}: {data['value']} {data['unit']} (Normal)")
                
    return "\n".join(summary_lines)

def _generate_local_review(data_summary, patient_info):
    """Fallback rule-based synthesis when no AI API is used."""
    review = f"""
    ### 🔬 Clinical Review Summary (Rule-Based)
    
    **Patient Profile:** {patient_info.get('age')} year old {patient_info.get('gender')}.
    
    **Key Observations:**
    The automated analysis has identified the following status of your report:
    
    {data_summary}
    
    **Recommendations:**
    1. **Primary Care:** Please schedule a follow-up with your primary physician to discuss the 'Critical' or 'High/Low' findings.
    2. **Clinical Correlation:** These results must be interpreted alongside your physical symptoms and medical history.
    3. **Action:** Do not self-medicate or stop current medications based on this automated screening.
    """
    return review

def _generate_openai_review(data_summary, api_key):
    """Generates review using OpenAI GPT-4."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Act as a professional Clinical Pathologist. Analyze these blood results and provide:
        1. A summary of significant abnormalities.
        2. Potential physiological or pathological causes.
        3. Suggested follow-up questions for the patient.
        
        Patient Data:
        {data_summary}
        
        Keep the tone professional and include a disclaimer that this is an AI-generated screening.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI Error: {str(e)}"

def _generate_gemini_review(data_summary, api_key):
    """Generates review using Google Gemini."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"Act as a Clinical Pathologist. Synthesize these results: {data_summary}. Provide insights on abnormalities and next steps."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"
