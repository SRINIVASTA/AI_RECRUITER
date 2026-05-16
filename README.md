# 🎯 AI Recruiter: Multimodal Multi-Resume Screener

A professional, production-ready recruitment screening dashboard built with **Streamlit** and powered by the modern **Google GenAI SDK**. This application evaluates compatibility between Job Descriptions (JDs) and Candidate Resumes (CVs) across four strict weight-distributed compliance tracks.

---

## 🚀 Key Features

*   **Multimodal Asset Support:** Natively parses **Images (PNG, JPG, JPEG)**, **PDFs**, **Word Documents (DOCX)**, and plain **TXT** files.
*   **Dual-Engine Hybrid Scoring Matrix:** 
    *   **API Mode (Gemini 2.5 Flash):** Contextual semantic analysis, synonym matching, and context-aware filtering when an API key is available.
    *   **Local Standalone Mode (TF-IDF):** Localized keyword vectorization fallback matching when an API key is absent, ensuring 100% operational uptime.
*   **Real-Time Auto-Population:** Extracted text maps immediately to user workspaces upon file upload.
*   **Dynamic UI Controls:** The action button dynamically adapts its label and backend matching engine depending on API Token availability checks.
*   **Recruiter Strategy Suite:** Outputs custom interactive matrix tables along with specific actionable next steps (e.g., *Do Not Auto-Reject overrides* or *Talent Pool Redirection guidelines*).

---

## 📊 Weight Distribution Profile

Compliance and compatibility scoring matrices are strictly weighted according to modern ATS screening criteria:


| Category | Weight | Evaluation Parameter Footprint |
| :--- | :--- | :--- |
| **Domain Expertise** | `30%` | Functional alignment, core industry positioning, video analytics / vision experience metrics. |
| **Education** | `25%` | Degree matching tier baselines (e.g., Tier-1 institute, engineering fields). |
| **Technical Stack** | `25%` | Frameworks, core coding architectures, and tool matches (e.g., PyTorch, TensorFlow). |
| **Scale & Deployment** | `20%` | Production environment exposure, MLOps orchestration, edge systems deployment. |

---

## 🛠️ Local Installation & Setup

To run this dashboard project locally on your machine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com
   cd AI Recruiter-cv-matcher
   ```

2. **Install Required Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit Web Server:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Streamlit Cloud Deployment Blueprint

1. Fork or push this repository configuration structure directly to **GitHub**.
2. Log in to [Streamlit Share](https://https://airecruiter-bjhauwjq4ncyh6p8q7diot.streamlit.app/) and link your GitHub authentication tokens.
3. Click **New App**, then pick your target repository and set the Main file path to `app.py`.
4. **Configure Secrets (Optional):** Expand **Advanced Settings** -> **Secrets**, and paste your fallback master API credentials:
   ```toml
   GOOGLE_API_KEY = "****************************"
   ```
5. Click **Deploy!** Your cloud app instance environment will build and run live in less than 60 seconds.

---

## 🔐 Security & Custom API Key Overrides

*   **Pasted Credentials Option:** The sidebar interface panel provides an **optional** text input field masked as a secure password field (`type="password"`). 
*   **Priority Hierarchy Chain:** If a user supplies their custom token string inside the workspace sidebar console, the application instantly routes API logic calls through that profile. If left blank, it cleanly cascades down to read the `st.secrets` background server environment. If neither is available, it switches gracefully into standalone local keyword analysis mode.

---

### 🛠️ Built with Passion

*   **Created by:** Srinivasta 🧑‍💻✨
*   **Powered by:** Streamlit 🎈 & Gemini 2.5 Flash 🤖🚀
*   **Target Domain:** Intelligent Recruitment Automation 🎯📊
