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
import time
from pathlib import Path
from io import BytesIO

from src.resume_refiner_crew.streamlit_runner import run_crew_with_params
from src.resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@st.cache_data
def get_openai_chat_models():
    """Fetch available OpenAI chat models dynamically.

    Returns a filtered, sorted list of chat model IDs.
    Falls back to hardcoded list on error.
    """
    import re
    from openai import OpenAI

    # Fallback model list
    fallback_models = [
        "gpt-5-pro", "gpt-5", "gpt-5-mini", "gpt-5-nano",
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
        "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-4",
        "gpt-3.5-turbo-16k", "gpt-3.5-turbo"
    ]

    try:
        client = OpenAI()
        models = [m.id for m in client.models.list()]

        # Regex patterns for filtering
        INC = re.compile(r"^(gpt-\d)", re.IGNORECASE)  # include GPT*
        END_DATE = re.compile(r"-\d{4}-\d{2}-\d{2}$")  # ends with YYYY-MM-DD
        EXCLUDE = re.compile(
            r"(whisper|sora|dall-e|tts|audio|image|embed(?:ding)?|"
            r"moderation|realtime|search|transcribe|diarize|codex|"
            r"davinci|babbage|instruct)",
            re.IGNORECASE
        )

        # Filter and sort models
        chat_models = sorted(
            (mid for mid in models
             if INC.search(mid) and not END_DATE.search(mid) and not EXCLUDE.search(mid)),
            reverse=True
        )

        return chat_models if chat_models else fallback_models

    except Exception as e:
        # Return fallback list on any error (invalid key, network issue, etc.)
        return fallback_models


# Page configuration
st.set_page_config(
    page_title="Resume Refiner Crew",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'completed' not in st.session_state:
    st.session_state.completed = False
if 'result' not in st.session_state:
    st.session_state.result = None
if 'edited_json' not in st.session_state:
    st.session_state.edited_json = None
if 'original_json' not in st.session_state:
    st.session_state.original_json = None
if 'json_edit_mode' not in st.session_state:
    st.session_state.json_edit_mode = False
if 'thread' not in st.session_state:
    st.session_state.thread = None
if 'thread_result' not in st.session_state:
    st.session_state.thread_result = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'show_logs' not in st.session_state:
    st.session_state.show_logs = False


def reset_session():
    """Reset session state for a new run."""
    st.session_state.processing = False
    st.session_state.completed = False
    st.session_state.result = None
    st.session_state.edited_json = None
    st.session_state.original_json = None
    st.session_state.json_edit_mode = False
    st.session_state.thread = None
    st.session_state.thread_result = None
    st.session_state.start_time = None
    st.session_state.show_logs = False


def run_crew_thread(resume_bytes, job_desc, api_key, model, target_words, result_container):
    """Run crew in a separate thread.

    Args:
        result_container: A mutable dict to store the result (avoids session state warnings)
    """
    result = run_crew_with_params(
        resume_pdf_bytes=resume_bytes,
        job_description=job_desc,
        api_key=api_key,
        model=model,
        target_words=target_words
    )

    # Store result in the provided container (thread-safe, no session state access)
    result_container['result'] = result
    result_container['completed'] = True


def get_current_progress():
    """Parse crew logs to determine current progress.

    Returns:
        tuple: (completed_count, agent_name, status_text, log_content)
    """
    log_file = Path(".crewai_temp/crew_logs.txt")

    if not log_file.exists():
        return (0, "Initializing", "Starting up...", "")

    log_content = log_file.read_text(encoding='utf-8')

    # Task mapping: task_name -> (position, agent_name, status_text)
    task_info = {
        "parse_resume_task": (1, "Resume PDF Parser", "Parsing your resume"),
        "analyze_job_task": (2, "Job Analyzer", "Analyzing the provided job description"),
        "optimize_resume_task": (3, "Resume Analyzer", "Identifying improvements to be made"),
        "generate_resume_task": (4, "Resume Writer", "Generating optimized resume"),
        "verify_resume_task": (5, "Fact Checker", "Verifying resume accuracy"),
        "harvard_format_task": (6, "Harvard Formatter", "Formatting resume structure"),
        "generate_report_task": (7, "Report Generator", "Generating final report")
    }

    # Find all task_name occurrences in logs
    import re
    task_matches = re.findall(r'task_name="([^"]+)"', log_content)

    if not task_matches:
        return (0, "Initializing", "Starting up...", log_content)

    # Last task found is the current executing task
    current_task = task_matches[-1]

    if current_task not in task_info:
        return (0, "Unknown", "Processing...", log_content)

    position, agent_name, status_text = task_info[current_task]

    # Completed count = current task position - 1
    completed_count = position - 1

    return (completed_count, agent_name, status_text, log_content)


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
    "Add the complete job posting",
    height=250,
    placeholder="Job description here",
    help="Include the full job description with requirements and responsibilities, the text formatting is not important"
)

# Options Section (collapsible)
with st.sidebar.expander("⚙️ Options", expanded=False):
    # API Key
    st.subheader("OpenAI API Key")
    api_key = st.text_input(
        "Your OpenAI API key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Your API key is never stored permanently"
    )

    # Model Selection
    st.subheader("Model Selection")

    # Get available models dynamically
    available_models = get_openai_chat_models()

    # Get default model from environment
    default_model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    # Find index of default model (fallback to 0 if not found)
    try:
        default_index = available_models.index(default_model)
    except ValueError:
        default_index = 0

    model = st.selectbox(
        "Choose AI model",
        options=available_models,
        index=default_index,
        help="Select the OpenAI model to use"
    )

    # Target Word Count
    st.subheader("Target Word Count")
    target_words = st.number_input(
        "Expected resume length",
        min_value=300,
        max_value=1000,
        value=int(os.getenv("TARGET_RESUME_WORDS", "400")),
        step=50,
        help="400-600 words for single page, 600-800 for two pages"
    )

    # Advanced Options
    st.subheader("Advanced Options")
    download_all = st.checkbox(
        "Download all output files",
        help="Include Markdown, JSON, and LaTeX files in addition to PDF"
    )
    allow_editing = st.checkbox(
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
    st.session_state.start_time = time.time()

    # Create a result container for thread communication
    st.session_state.thread_result = {'result': None, 'completed': False}

    # Start processing in background thread
    st.session_state.thread = threading.Thread(
        target=run_crew_thread,
        args=(
            uploaded_file.read(),
            job_description,
            api_key,
            model,
            target_words,
            st.session_state.thread_result
        )
    )
    st.session_state.thread.start()
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
st.title("📝 Resume Refiner Crew")
st.markdown("Transform your resume into a job-specific, ATS-optimized document")


# Fragment for auto-updating progress display
@st.fragment(run_every=1.0)
def show_processing_progress():
    """Auto-updating fragment that displays processing progress."""
    # Get current progress
    completed, agent_name, status_text, logs = get_current_progress()

    # Manual elapsed time display (replaces spinner)
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        elapsed_str = f"{int(elapsed//60)}m {int(elapsed%60)}s"
        st.info(f"⏳ Working on your resume... (Elapsed: {elapsed_str})")
    else:
        st.info("⏳ Working on your resume...")

        # Progress bar
    progress_value = completed / 7
    st.progress(progress_value, text=f"**Working Agent: {agent_name} ({completed+1}/7)**")

    # Checkbox to control log expansion (persists across fragment reruns)
    show_logs = st.checkbox("Show detailed logs", value=st.session_state.show_logs, key="show_logs_check")
    st.session_state.show_logs = show_logs

    # Status container
    with st.status(label=status_text, state="running", expanded=show_logs):
        if logs.strip():
            st.code(logs, language=None, wrap_lines=True)
        else:
            st.info("Initializing...")


# PROCESSING PHASE
if st.session_state.processing:
    # Check if thread has completed
    if st.session_state.thread_result and st.session_state.thread_result.get('completed'):
        # Thread finished - update session state from main thread
        st.session_state.result = st.session_state.thread_result.get('result')
        st.session_state.processing = False
        st.session_state.completed = True
        st.rerun()

    # Call fragment - auto-updates every 1 second
    show_processing_progress()

# RESULTS PHASE
elif st.session_state.completed:
    result = st.session_state.result

    if result and result['success']:
        st.success("✅ Your optimized resume is ready!")
        st.balloons()

        # Show elapsed time
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.info(f"⏱️ Processing completed in {int(elapsed//60)}m {int(elapsed%60)}s")

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
    3. **Process** and watch the multi-agent system optimize your resume
    4. **Download** your tailored, ATS-optimized resume

    The system uses 7 specialized AI agents to analyze, optimize, and format your resume.
    """)
