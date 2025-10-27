"""
Streamlit UI for Resume Refiner Crew

A user-friendly graphical interface for the Resume Refiner multi-agent system.
Guides users through input, processing, and results phases.
"""

import streamlit as st
import os
import json
import zipfile
import threading
from pathlib import Path
from io import BytesIO
from queue import Queue

from src.resume_refiner_crew.streamlit_runner import run_crew_with_params
from src.resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Resume Refiner Crew",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'completed' not in st.session_state:
    st.session_state.completed = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'logs_queue' not in st.session_state:
    st.session_state.logs_queue = Queue()
if 'result' not in st.session_state:
    st.session_state.result = None
if 'edited_json' not in st.session_state:
    st.session_state.edited_json = None
if 'original_json' not in st.session_state:
    st.session_state.original_json = None
if 'json_edit_mode' not in st.session_state:
    st.session_state.json_edit_mode = False


def reset_session():
    """Reset session state for a new run."""
    st.session_state.processing = False
    st.session_state.completed = False
    st.session_state.logs = []
    st.session_state.logs_queue = Queue()
    st.session_state.result = None
    st.session_state.edited_json = None
    st.session_state.original_json = None
    st.session_state.json_edit_mode = False


def run_crew_thread(resume_bytes, job_desc, api_key, model, target_words, logs_queue):
    """Run crew in a separate thread."""
    # Create a thread-safe log callback using the queue
    def log_to_queue(message: str):
        logs_queue.put(message)

    result = run_crew_with_params(
        resume_pdf_bytes=resume_bytes,
        job_description=job_desc,
        api_key=api_key,
        model=model,
        target_words=target_words,
        log_callback=log_to_queue
    )

    # Put result and completion status in queue as special messages
    logs_queue.put(('__RESULT__', result))
    logs_queue.put(('__COMPLETE__', True))


def create_zip_archive():
    """Create a ZIP file with all output files."""
    output_dir = Path("output")
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in output_dir.glob('*'):
            if file_path.is_file():
                zip_file.write(file_path, file_path.name)

    zip_buffer.seek(0)
    return zip_buffer


# ===== SIDEBAR: INPUTS =====
st.sidebar.title("Resume Refiner Crew")
st.sidebar.markdown("AI-powered resume optimization with multi-agent intelligence")
st.sidebar.divider()

# Upload Resume
st.sidebar.subheader("1. Upload Resume")
uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=['pdf'],
    help="Upload your current resume in PDF format"
)

# Show uploaded filename
if uploaded_file is not None:
    st.sidebar.success(f"✓ Uploaded: {uploaded_file.name}")

# Job Description
st.sidebar.subheader("2. Job Description")
job_description = st.sidebar.text_area(
    "Paste the complete job posting",
    height=150,
    help="Include the full job description with requirements and responsibilities"
)

# API Key
st.sidebar.subheader("3. OpenAI API Key")
api_key = st.sidebar.text_input(
    "Your OpenAI API key",
    type="password",
    value=os.getenv("OPENAI_API_KEY", ""),
    help="Your API key is never stored permanently"
)

# Model Selection
st.sidebar.subheader("4. Model Selection")
model = st.sidebar.selectbox(
    "Choose AI model",
    options=["gpt-5-mini", "gpt-5-nano"],
    index=0,
    help="Select the OpenAI model to use"
)

# Target Word Count
st.sidebar.subheader("5. Target Word Count")
target_words = st.sidebar.number_input(
    "Expected resume length",
    min_value=300,
    max_value=1000,
    value=int(os.getenv("TARGET_RESUME_WORDS", "400")),
    step=50,
    help="400-600 words for single page, 600-800 for two pages"
)

# Advanced Options
st.sidebar.subheader("6. Advanced Options")
download_all = st.sidebar.checkbox(
    "Download all output files",
    help="Include Markdown, JSON, and LaTeX files in addition to PDF"
)
allow_editing = st.sidebar.checkbox(
    "Allow final resume editing",
    help="Edit the structured JSON before generating the final PDF"
)

st.sidebar.divider()

# Validate inputs
inputs_valid = (
    uploaded_file is not None
    and len(job_description.strip()) > 0
    and len(api_key.strip()) > 0
)

# Process Button
if st.sidebar.button(
    "🚀 Process Resume",
    type="primary",
    disabled=not inputs_valid or st.session_state.processing,
    use_container_width=True
):
    reset_session()
    st.session_state.processing = True

    # Start processing in background thread
    thread = threading.Thread(
        target=run_crew_thread,
        args=(
            uploaded_file.read(),
            job_description,
            api_key,
            model,
            target_words,
            st.session_state.logs_queue  # Pass the queue to the thread
        )
    )
    thread.start()
    st.rerun()

# Reset Button
if st.sidebar.button("🔄 Start Over", use_container_width=True):
    reset_session()
    st.rerun()

# Show input validation hints
if not inputs_valid:
    st.sidebar.warning("⚠️ Please complete all required inputs above")

# ===== MAIN CONTENT AREA =====

# Show title
st.title("📄 Resume Refiner Crew")
st.markdown("Transform your resume into a job-specific, ATS-optimized document")

# PROCESSING PHASE
if st.session_state.processing:
    # Poll the queue and update session state logs
    while not st.session_state.logs_queue.empty():
        item = st.session_state.logs_queue.get()

        # Check for special messages
        if isinstance(item, tuple):
            if item[0] == '__RESULT__':
                st.session_state.result = item[1]
            elif item[0] == '__COMPLETE__':
                st.session_state.processing = False
                st.session_state.completed = True
        else:
            # Regular log message
            st.session_state.logs.append(item)

    st.header("⚙️ Processing in progress...")

    # Progress visualization
    progress_steps = [
        "Parsing Resume",
        "Analyzing Job Requirements",
        "Optimizing Content",
        "Verifying Facts",
        "Formatting Resume",
        "Generating PDF"
    ]

    # Show progress steps
    cols = st.columns(len(progress_steps))
    for i, step in enumerate(progress_steps):
        with cols[i]:
            st.markdown(f"**{i+1}. {step}**")

    st.divider()

    # Live logs
    st.subheader("📋 Live Progress Logs")
    log_container = st.container(height=400)

    with log_container:
        if st.session_state.logs:
            for log in st.session_state.logs:
                st.text(log)
        else:
            st.info("Initializing...")

    # Auto-refresh while processing
    if st.session_state.processing:
        import time
        time.sleep(1)
        st.rerun()

# RESULTS PHASE
elif st.session_state.completed:
    result = st.session_state.result

    if result and result['success']:
        st.success("✅ Your optimized resume is ready!")

        # Display final report
        st.header("📊 Optimization Report")

        report_path = Path("output/final_report.md")
        if report_path.exists():
            report_content = report_path.read_text(encoding='utf-8')
            st.markdown(report_content)
        else:
            st.warning("Report file not found")

        st.divider()

        # JSON EDITING MODE
        if allow_editing and not st.session_state.json_edit_mode:
            st.header("✏️ Edit Structured Resume (Optional)")

            json_path = Path("output/structured_resume.json")
            if json_path.exists():
                # Load original JSON if not already loaded
                if st.session_state.original_json is None:
                    st.session_state.original_json = json_path.read_text(encoding='utf-8')
                    st.session_state.edited_json = st.session_state.original_json

                st.info("You can edit the structured resume data below before generating the final PDF")

                # JSON editor
                edited_json = st.text_area(
                    "Structured Resume JSON",
                    value=st.session_state.edited_json,
                    height=400,
                    key="json_editor"
                )

                # Update session state
                st.session_state.edited_json = edited_json

                # Validate JSON
                try:
                    json.loads(edited_json)
                    json_valid = True
                except json.JSONDecodeError as e:
                    json_valid = False
                    st.error(f"Invalid JSON: {str(e)}")

                # Buttons
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("↺ Restore Original JSON"):
                        st.session_state.edited_json = st.session_state.original_json
                        st.rerun()

                with col2:
                    if st.button(
                        "✓ Apply Changes and Generate PDF",
                        disabled=not json_valid,
                        type="primary"
                    ):
                        # Save edited JSON
                        json_path.write_text(edited_json, encoding='utf-8')

                        # Regenerate PDF
                        with st.spinner("Generating PDF from edited resume..."):
                            pdf_path = generate_resume_pdf_from_json()
                            if pdf_path:
                                st.session_state.result['pdf_path'] = pdf_path
                                st.session_state.json_edit_mode = True
                                st.success(f"✓ PDF regenerated: {pdf_path}")
                                st.rerun()
                            else:
                                st.error("PDF generation failed")

                st.divider()

        # DOWNLOAD SECTION
        if not allow_editing or st.session_state.json_edit_mode:
            st.header("📥 Download Your Resume")

            # PDF Download (always available)
            pdf_path = Path(result['pdf_path'])
            if pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="📄 Download PDF Resume",
                        data=f.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.error("PDF file not found")

            # ZIP Download (if enabled)
            if download_all:
                st.download_button(
                    label="📦 Download All Files (ZIP)",
                    data=create_zip_archive(),
                    file_name="resume_optimization_complete.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    else:
        # Error handling
        st.error("❌ Processing Failed")

        error_msg = result.get('error', 'Unknown error') if result else 'Unknown error'
        st.error(f"Error: {error_msg}")

        st.subheader("What to try:")
        st.markdown("""
        - Check that your OpenAI API key is valid
        - Ensure your resume PDF is not corrupted
        - Verify the job description is complete
        - Try with a different model
        """)

        if st.button("🔄 Retry", type="primary"):
            reset_session()
            st.rerun()

# INITIAL STATE
else:
    st.info("👈 Please complete the inputs in the sidebar and click 'Process Resume' to begin")

    st.subheader("How it works:")
    st.markdown("""
    1. **Upload** your current resume (PDF format)
    2. **Paste** the complete job description
    3. **Configure** AI model and target word count
    4. **Process** and watch the multi-agent system optimize your resume
    5. **Download** your tailored, ATS-optimized resume

    The system uses 7 specialized AI agents to analyze, optimize, and format your resume
    to maximize your chances of getting noticed by recruiters and passing ATS systems.
    """)

    st.subheader("Key Features:")
    st.markdown("""
    - ✅ Intelligent resume parsing
    - ✅ Job fit scoring with detailed analysis
    - ✅ ATS optimization with proper keywords
    - ✅ Fact-checking to prevent AI hallucinations
    - ✅ Harvard Business School formatting
    - ✅ Professional PDF output
    """)
