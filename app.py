import streamlit as st
import re
import io
import pypdf
import docx2txt
from google import genai
from google.genai import types

# 🖥️ Page Layout Setup
st.set_page_config(
    page_title="Whitetable AI: Multimodal Multi-Resume Screener",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Whitetable AI: Multimodal Multi-Resume Screener")
st.caption("Upload an Image, PDF, DOCX, or TXT document to evaluate CV compatibility contextually.")

# --- 🔑 OPTIONAL SIDEBAR API KEY CONFIGURATION ENGINE ---
st.sidebar.header("🔐 Security Settings")
st.sidebar.markdown("This app runs automatically using our host server key. Optionally, you can supply your personal Google AI Studio Key below to use your own limits.")

# Completely optional password input widget hidden in the sidebar
user_custom_key = st.sidebar.text_input(
    label="Your Google API Key (Optional):",
    type="password",
    placeholder="AIzaSy...",
    help="Leave this blank to use the app's default server token environment."
)

# Resolution loop checking priority tier chains
active_api_key = None
if user_custom_key.strip():
    active_api_key = user_custom_key.strip()
    st.sidebar.success("⚡ Using your custom pasted API Key.")
elif "GOOGLE_API_KEY" in st.secrets:
    active_api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.info("🔒 Running on App Server Secret Key configuration.")
else:
    st.sidebar.error("❌ Key Missing: Paste an optional token above or configure secrets to activate the engine.")

# Instantiate client context based on availability state profiles
ai_client = None
if active_api_key:
    try:
        ai_client = genai.Client(api_key=active_api_key)
    except Exception as init_err:
        st.error(f"Failed to bind client instance layout: {init_err}")

def extract_text_from_bytes(file_bytes, filename):
    """Safely extracts raw text data based on standard file extensions."""
    ext = filename.split('.')[-1].lower()
    text = ""
    try:
        if ext == 'pdf':
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext in ['docx', 'doc']:
            docx_file = io.BytesIO(file_bytes)
            text = docx2txt.process(docx_file)
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"[Error parsing text inside {filename}: {str(e)}]"
    return text

def request_gemini_evaluation(jd_text, cv_text, cv_image_bytes=None, cv_filename=""):
    """Streams payloads directly into Gemini 2.5 Flash for unified context matching."""
    if ai_client is None:
        return 0.0, "API client unconfigured.", "Please set up or paste an API Key first."

    system_prompt = """
    You are an expert recruitment system modeled after Whitetable AI.
    Analyze the provided Job Description against the Candidate Resume.
    Evaluate compliance across 4 strict weighted criteria:
    1. Education (25% weight)
    2. Domain Expertise (30% weight)
    3. Technical Stack (25% weight)
    4. Scale & Deployment (20% weight)

    You must output your complete analysis using exactly this layout structure. Do not use markdown wraps or extra descriptions:

    [START_BREAKDOWN_TABLE]
    <tr><td><b>Education</b></td><td>25.0%</td><td>[Score]%</td><td>[Contrib]%</td></tr>
    <tr><td><b>Domain Expertise</b></td><td>30.0%</td><td>[Score]%</td><td>[Contrib]%</td></tr>
    <tr><td><b>Technical Stack</b></td><td>25.0%</td><td>[Score]%</td><td>[Contrib]%</td></tr>
    <tr><td><b>Scale & Deployment</b></td><td>20.0%</td><td>[Score]%</td><td>[Contrib]%</td></tr>
    [END_BREAKDOWN_TABLE]

    [START_TOTAL_SCORE][Final Cumulative Weighted Score out of 100][END_TOTAL_SCORE]

    [START_RECRUITER_STEPS]
    <div style="margin-bottom: 12px;"><b style="color: #2b6cb0; font-size: 15px;">👉 [Step Title]:</b> <span style="color: #334155;">[Context-aware analysis and interview screening recommendation here]</span></div>
    [END_RECRUITER_STEPS]
    """

    user_contents = []
    
    # Process JD payload
    if not jd_text and cv_filename:
        pass
    else:
        user_contents.append(f"TARGET JOB DESCRIPTION:\n{jd_text}\n\n")

    # Process CV payload (Text string)
    user_contents.append(f"CANDIDATE RESUME TEXT:\n{cv_text}\n")

    # Pass Image visual structures directly if present
    if cv_image_bytes and cv_filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'webp', 'bmp']:
        image_part = types.Part.from_bytes(data=cv_image_bytes, mime_type=f"image/{cv_filename.split('.')[-1].lower()}")
        user_contents.append("\nADDITIONAL VISUAL IMAGE ATTACHMENT PROCESSED BELOW:\n")
        user_contents.append(image_part)

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.1)
        )
        resp_text = response.text

        table_match = re.search(r'\[START_BREAKDOWN_TABLE\](.*?)\[END_BREAKDOWN_TABLE\]', resp_text, re.DOTALL)
        score_match = re.search(r'\[START_TOTAL_SCORE\](.*?)\[END_TOTAL_SCORE\]', resp_text, re.DOTALL)
        steps_match = re.search(r'\[START_RECRUITER_STEPS\](.*?)\[END_RECRUITER_STEPS\]', resp_text, re.DOTALL)

        table_rows = table_match.group(1).strip() if table_match else "<tr><td colspan='4'>Failed to structure table data.</td></tr>"
        final_score = float(score_match.group(1).strip().replace('%', '')) if score_match else 0.0
        steps_content = steps_match.group(1).strip() if steps_match else "<div>Default profiling fallback.</div>"

        breakdown_html = f"""
        <table border='1' style='border-collapse: collapse; width: 100%; text-align: left; font-family: sans-serif;'>
            <tr style='background-color: #f2f2f2;'><th>Category</th><th>Weight</th><th>Category Match Score</th><th>Weighted Contribution</th></tr>
            {table_rows}
            <tr style='background-color: #e6f7ff;'><td><b>FINAL MATCH SCORE</b></td><td><b>100%</b></td><td>-</td><td><b>{final_score:.1f}%</b></td></tr>
        </table>
        """

        insights_html = f"""
        <div style="margin-top: 25px; padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px; background-color: #f8fafc; font-family: sans-serif; line-height: 1.6;">
            <h3 style="color: #1e293b; margin-top: 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">🎯 HR / Recruiter Next Steps</h3>
            {steps_content}
        </div>
        """
        return final_score, breakdown_html, insights_html
    except Exception as e:
        return 0.0, f"Error processing request: {str(e)}", ""

# --- UI Layout Session State Setup ---
if "jd_text_val" not in st.session_state: st.session_state.jd_text_val = ""
if "cv_text_val" not in st.session_state: st.session_state.cv_text_val = ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 1. Target Job Description")
    uploaded_jd = st.file_uploader("Upload JD File", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    
    if uploaded_jd:
        ext = uploaded_jd.name.split('.')[-1].lower()
        if ext in ['png', 'jpg', 'jpeg']:
            st.session_state.jd_text_val = f"[📸 Image Registered: {uploaded_jd.name}. Will evaluate visually.]"
        else:
            st.session_state.jd_text_val = extract_text_from_bytes(uploaded_jd.read(), uploaded_jd.name)
            
    jd_area = st.text_area("JD Layout Workspace:", value=st.session_state.jd_text_val, height=220, key="jd_area_key")

with col2:
    st.subheader("📄 2. Candidate Resume (CV)")
    uploaded_cv = st.file_uploader("Upload CV File", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    
    cv_bytes, cv_name = None, ""
    if uploaded_cv:
        cv_name = uploaded_cv.name
        cv_bytes = uploaded_cv.read()
        ext = cv_name.split('.')[-1].lower()
        if ext in ['png', 'jpg', 'jpeg']:
            st.session_state.cv_text_val = f"[📸 Image Registered: {cv_name}. Will evaluate visually.]"
        else:
            st.session_state.cv_text_val = extract_text_from_bytes(cv_bytes, cv_name)
            
    cv_area = st.text_area("CV Layout Workspace:", value=st.session_state.cv_text_val, height=220, key="cv_area_key")

# --- 🚀 DASHBOARD ACTION CONTROLLERS ---
btn_col1, btn_col2 = st.columns([0.7, 0.3])

with btn_col1:
    run_btn = st.button("🚀 Run Intelligent API Assessment", use_container_width=True, type="primary")

with btn_col2:
    if st.button("🧹 Reset & Clean Dashboard", use_container_width=True):
        st.session_state.jd_text_val = ""
        st.session_state.cv_text_val = ""
        st.rerun()

if run_btn:
    if ai_client is None:
        st.error("❌ Execution Aborted: Missing valid Google API key setup credentials. Please add a key in Secrets or use the optional sidebar input.")
    else:
        final_jd = jd_area.strip() if "[📸 Image Registered:" not in jd_area else ""
        final_cv = cv_area.strip() if "[📸 Image Registered:" not in cv_area else ""
        
        if (not final_jd and not uploaded_jd) or (not final_cv and not uploaded_cv):
            st.error("❌ Input Error: Both fields must contain valid content to run matching profiles.")
        else:
            with st.spinner("🤖 Running contextual matrix analysis via Gemini..."):
                score, table_html, steps_html = request_gemini_evaluation(final_jd, final_cv, cv_bytes, cv_name)
                
                color = "#28a745" if score >= 75 else ("#ffc107" if score >= 40 else "#dc3545")
                tier = "TIER 1 (Strong Fit)" if score >= 75 else ("TIER 2 (Partial Fit)" if score >= 40 else "TIER 3 (Low Match)")
                
                st.markdown(f"""
                <div style="padding: 16px; border-radius: 6px; background-color: {color}; color: white; margin-top: 15px;">
                    <h2 style="margin: 0; color: white;">{score:.1f}% Match Rating</h2>
                    <p style="margin: 4px 0 0 0; font-weight: bold;">Status Classification: {tier}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("### AI-Generated Matrix Profile:")
                st.markdown(table_html, unsafe_allow_html=True)
                st.markdown(steps_html, unsafe_allow_html=True)
