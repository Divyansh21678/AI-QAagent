import streamlit as st
import os
from fpdf import FPDF

from agents.qa_agent import QAAgent
from utils.report_generator import save_markdown
from pages.dashboard import show_dashboard

# Document readers import
from utils.document_reader import read_pdf, read_docx, read_txt

# Security Sanitizer Integration
from utils.security_sanitizer import SecuritySanitizer

# -----------------------------
# Page Config & Custom UI Injection
# -----------------------------
st.set_page_config(
    page_title="AI QA Copilot Pro",
    page_icon="🤖",
    layout="wide"
)

# Deep Clean Custom UI with Forced Visible Text Profiles
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F8FAFC !important;
    }
    
    .stApp p, .stApp label, .stApp span, .stApp div, [data-testid="stMetricLabel"] {
        color: #E2E8F0 !important;
        font-weight: 500 !important;
    }
    
    .stTextArea textarea, .stTextInput input {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
        font-size: 1rem !important;
    }
    
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid #334155;
    }
    
    div[data-testid="stForm"], .stTextArea textarea, .stFileUploader {
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
    }
    
    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38BDF8 0%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #CBD5E1 !important;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #0284C7 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(52, 211, 153, 0.4) !important;
    }
    
    div[data-testid="stDownloadButton"] button {
        background: #334155 !important;
        border: 1px solid #475569 !important;
        color: #E2E8F0 !important;
    }
    
    .output-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #0EA5E9;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

agent = QAAgent()

# Document text ingestion process
def extract_text(file):
    if file.name.endswith(".pdf"):
        return read_pdf(file)
    elif file.name.endswith(".docx"):
        return read_docx(file)
    else:
        return read_txt(file)

# Dynamic Table Parsing PDF Generator Block
def convert_to_pdf(text_content, output_filename):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'AI QA Copilot - Audit Report', 0, 1, 'C')
            self.ln(5)
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    clean_text = text_content.replace('<br>', '\n').replace('<br />', '\n')
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    lines = clean_text.split('\n')
    in_table = False
    table_data = []

    def draw_accumulated_table(data):
        if not data:
            return
        pdf.set_font("Arial", size=8)
        col_width = 190 / max(len(r) for r in data)
        
        for r_idx, row in enumerate(data):
            if r_idx == 0:
                pdf.set_font("Arial", 'B', 8)
                pdf.set_fill_color(226, 232, 240)
            else:
                pdf.set_font("Arial", size=7)
                pdf.set_fill_color(255, 255, 255)
                
            max_lines = 1
            for cell in row:
                lines_count = len(pdf.multi_cell(col_width, 5, cell, split_only=True))
                if lines_count > max_lines:
                    max_lines = lines_count
            
            calculated_row_height = max_lines * 5
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            for cell in row:
                pdf.multi_cell(col_width, calculated_row_height / len(pdf.multi_cell(col_width, 4, cell, split_only=True)), cell, border=1, fill=(r_idx==0))
                pdf.set_xy(x_start + col_width, y_start)
                x_start = pdf.get_x()
            pdf.ln(calculated_row_height)

    for line in lines:
        if line.strip().startswith('|'):
            if '---' in line:
                continue
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if row:
                table_data.append(row)
                in_table = True
            continue
        else:
            if in_table:
                draw_accumulated_table(table_data)
                table_data = []
                in_table = False

        if line.startswith('###'):
            pdf.set_font("Arial", 'B', 11)
            pdf.ln(2)
            pdf.cell(0, 6, line.replace('###', '').strip(), ln=1)
            pdf.ln(1)
        elif line.startswith('##'):
            pdf.set_font("Arial", 'B', 13)
            pdf.ln(3)
            pdf.cell(0, 8, line.replace('##', '').strip(), ln=1)
            pdf.ln(2)
        elif line.strip().startswith('-') or line.strip().startswith('*'):
            pdf.set_font("Arial", size=9)
            pdf.cell(5, 5, "-", ln=0)
            pdf.multi_cell(185, 5, line.strip()[1:].strip())
        else:
            if line.strip():
                pdf.set_font("Arial", size=9)
                pdf.multi_cell(190, 5, line)
            else:
                pdf.ln(2)
                
    if in_table:
        draw_accumulated_table(table_data)

    pdf.output(output_filename)
    return output_filename

# -----------------------------
# Session Initialization
# -----------------------------
if "response" not in st.session_state:
    st.session_state.response = None

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Navigation Hub
# -----------------------------
with st.sidebar:
    st.markdown("<h1 style='color: #38BDF8; font-size: 1.8rem;'>AI QA Copilot Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    
    st.subheader("Model Settings")
    ai_provider = st.selectbox(
        "Select AI Engine:",
        ["Gemini 2.5 Flash", "Groq (Llama 3.3)"],
        key="sidebar_provider"
    )
    
    st.write("---")
    st.subheader("Navigation Links")
    
    page = st.radio(
        "Navigation Links",
        ["Dashboard", "Functional Testing", "API Testing", "Security Testing", "Smart Bug Finder", "Reports"],
        label_visibility="collapsed"
    )

# -----------------------------
# App Routing Logic
# -----------------------------
if page == "Dashboard":
    st.markdown("<div class='main-title'>AI QA Copilot Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Next-Generation Automated Test Case Suite Generation Pipeline</div>", unsafe_allow_html=True)
    show_dashboard()

elif page == "Smart Bug Finder":
    st.markdown("<div class='main-title'>Smart Bug Finder and Defect Logger</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>Heuristic Production Analysis Core powered by: <strong style='color: #38BDF8;'>{ai_provider}</strong></div>", unsafe_allow_html=True)
    
    col_input, col_tips = st.columns([2, 1])
    with col_input:
        bug_description = st.text_area(
            "Paste Raw Bug Logs, Error Tracebacks, or System Observations",
            placeholder="Example:\nWhen I clicked checkout on the staging web app, the console threw a 500 internal error...",
            height=250
        )
    with col_tips:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-top: 28px;">
            <h4 style="color: #38BDF8; margin-top: 0;">Root Cause Isolated</h4>
            <p style="font-size: 0.9rem; color: #94A3B8; line-height: 1.5;">
                Provide raw console traces or user behavioral steps. The security layer will scrub vulnerable infrastructure data out of the prompt payload automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Analyze Defect and Generate Production Bug Report", use_container_width=True):
        if bug_description.strip():
            with st.spinner("Processing architectural log files and heuristics..."):
                # Real-Time Security Scrubbing
                sanitized_bug = SecuritySanitizer.sanitize_input_text(bug_description)
                
                response = agent.generate_bug_report(sanitized_bug, provider=ai_provider)
                st.session_state.response = response
                st.session_state.history.append({
                    "type": f"Bug Report ({ai_provider})",
                    "requirement": sanitized_bug,
                    "response": response
                })
        else:
            st.warning("Please insert a raw system flaw trace before logging.")

    if st.session_state.response:
        st.write("")
        st.markdown("<h3 style='color: #34D399;'>Generated Jira-Ready Defect File</h3>", unsafe_allow_html=True)
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.response)
        st.markdown('</div>', unsafe_allow_html=True)

        filename = "defect_analysis_report.md"
        pdf_filename = "defect_analysis_report.pdf"
        save_markdown(filename, st.session_state.response)
        convert_to_pdf(st.session_state.response, pdf_filename)

        st.write("")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("Export Defect MD", st.session_state.response, file_name=filename, mime="text/markdown", use_container_width=True)
        with col_dl2:
            if os.path.exists(pdf_filename):
                with open(pdf_filename, "rb") as pdf:
                    st.download_button("Export Defect PDF Report", pdf, file_name=pdf_filename, mime="application/pdf", use_container_width=True)

elif page == "Reports":
    st.markdown("<div class='main-title'>Global Reports and Analytics Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Real-time QA Audit Logs, Test Coverage Matrix and Defect Registry</div>", unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("Session registry is currently empty.")
    else:
        total_runs = len(st.session_state.history)
        functional_count = sum(1 for item in st.session_state.history if "Functional" in item["type"])
        api_count = sum(1 for item in st.session_state.history if "API" in item["type"])
        security_count = sum(1 for item in st.session_state.history if "Security" in item["type"])
        bug_count = sum(1 for item in st.session_state.history if "Bug" in item["type"])
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric(label="Total Scenarios Audited", value=total_runs)
        with m_col2:
            st.metric(label="Functional Frameworks", value=functional_count)
        with m_col3:
            st.metric(label="API Contracts Verified", value=api_count)
        with m_col4:
            st.metric(label="Vulnerability Scans / Bugs", value=security_count + bug_count)
            
        st.write("---")
        st.markdown("### Master Defect and Test Suite Registry")
        
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Log #{total_runs - idx} | Type: {item['type']} | Profile: {item['requirement'][:50]}..."):
                st.markdown("#### Input Context Metadata (Sanitized)")
                st.code(item['requirement'], language='text')
                st.write("---")
                st.markdown("#### Generated System Architecture Profile")
                st.markdown(item['response'])
                
                clean_name = f"archived_report_{total_runs - idx}"
                md_filename = f"{clean_name}.md"
                pdf_filename = f"{clean_name}.pdf"
                
                save_markdown(md_filename, item['response'])
                convert_to_pdf(item['response'], pdf_filename)
                
                col_arch1, col_arch2 = st.columns(2)
                with col_arch1:
                    st.download_button(f"Download Markdown Log #{total_runs - idx}", item['response'], file_name=md_filename, mime="text/markdown", key=f"dl_md_{idx}")
                with col_arch2:
                    if os.path.exists(pdf_filename):
                        with open(pdf_filename, "rb") as arch_pdf:
                            st.download_button(f"Download Corporate PDF #{total_runs - idx}", arch_pdf, file_name=pdf_filename, mime="application/pdf", key=f"dl_pdf_{idx}")

else:
    st.markdown(f"<div class='main-title'>{page}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>Engineered via high-performance LLM: <strong style='color: #38BDF8;'>{ai_provider}</strong></div>", unsafe_allow_html=True)
    
    col_input, col_tips = st.columns([2, 1])
    
    with col_input:
        uploaded_file = st.file_uploader(
            "Upload Requirement Specifications (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"]
        )

        requirement = ""
        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            # 1. Deep Magic Bytes Signature validation gate
            if not SecuritySanitizer.is_file_safe(uploaded_file.name, file_bytes):
                st.error("Security Blocked: Unauthorized structure or payload mismatch isolated within document data.")
            else:
                requirement = extract_text(uploaded_file)
                st.toast("Document verified & loaded safely!", icon="✅")
                requirement = st.text_area("Loaded Specifications Matrix", value=requirement, height=250)
        else:
            requirement = st.text_area(
                "Raw Requirements Input Profile",
                placeholder="Example:\nLogin Portal Feature\n- Email Validation\n- Password Complexity Check",
                height=250
            )
            
    with col_tips:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-top: 28px;">
            <h4 style="color: #38BDF8; margin-top: 0;">Copilot Studio Tips</h4>
            <p style="font-size: 0.9rem; color: #94A3B8; line-height: 1.5;">
                All text inputs are scrubbed of high-entropy credentials, hashes, and dynamic instruction override signatures before executing remote logic.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    if page == "Functional Testing":
        if st.button("Execute Functional Test Case Generation", use_container_width=True):
            if requirement.strip():
                with st.spinner("Compiling structural verification scenarios..."):
                    # 2. Text payload runtime scrubbing
                    sanitized_req = SecuritySanitizer.sanitize_input_text(requirement)
                    response = agent.generate_functional_tests(sanitized_req, provider=ai_provider)
                    st.session_state.response = response
                    st.session_state.history.append({
                        "type": f"Functional ({ai_provider})",
                        "requirement": sanitized_req,
                        "response": response
                    })
            else:
                st.warning("Input queue is empty. Please enter configuration details.")

    elif page == "API Testing":
        if st.button("Execute API Test Suite Generation", use_container_width=True):
            if requirement.strip():
                with st.spinner("Evaluating API endpoints and boundary checks..."):
                    sanitized_req = SecuritySanitizer.sanitize_input_text(requirement)
                    response = agent.generate_api_tests(sanitized_req, provider=ai_provider)
                    st.session_state.response = response
                    st.session_state.history.append({
                        "type": f"API ({ai_provider})",
                        "requirement": sanitized_req,
                        "response": response
                    })
            else:
                st.warning("Input queue is empty. Please enter configuration details.")

    elif page == "Security Testing":
        if st.button("Execute Vulnerability and Security Test Generation", use_container_width=True):
            if requirement.strip():
                with st.spinner("Analyzing penetration vectors..."):
                    sanitized_req = SecuritySanitizer.sanitize_input_text(requirement)
                    response = agent.generate_security_tests(sanitized_req, provider=ai_provider)
                    st.session_state.response = response
                    st.session_state.history.append({
                        "type": f"Security ({ai_provider})",
                        "requirement": sanitized_req,
                        "response": response
                    })
            else:
                st.warning("Input queue is empty. Please enter configuration details.")

    if st.session_state.response:
        st.write("")
        st.markdown("<h3 style='color: #34D399;'>Generated Scenarios Summary</h3>", unsafe_allow_html=True)
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(st.session_state.response)
        st.markdown('</div>', unsafe_allow_html=True)

        clean_filename = "".join(c if c.isalnum() else "_" for c in requirement[:30].strip().lower())
        filename = f"{clean_filename}_test_cases.md"
        pdf_filename = f"{clean_filename}_test_cases.pdf"
        
        save_markdown(filename, st.session_state.response)
        convert_to_pdf(st.session_state.response, pdf_filename)

        st.write("")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("Export System Markdown (.md)", st.session_state.response, file_name=filename, mime="text/markdown", use_container_width=True)
        with col_dl2:
            if os.path.exists(pdf_filename):
                with open(pdf_filename, "rb") as pdf:
                    st.download_button("Export Finalized PDF Report", pdf, file_name=pdf_filename, mime="application/pdf", use_container_width=True)

# Corporate Branding Footer
st.markdown("""
<br><hr>
<div style="text-align: center; color: #475569; font-size: 0.85rem; padding-bottom: 20px;">
    AI QA Copilot Pro Hub • Secure Enterprise Engine Framework Built with Streamlit Architecture
</div>
""", unsafe_allow_html=True)