"""Streamlit UI for Resume Refiner Crew.

A user-friendly graphical interface for the Resume Refiner multi-agent system.
Guides users through input, processing, and results phases.
"""

import json
import multiprocessing
import os
import re
import time
import zipfile
from io import BytesIO
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.resume_refiner_crew.constants import TASKS_INFO, TOTAL_TASKS
from src.resume_refiner_crew.streamlit_runner import run_crew_with_params
from src.resume_refiner_crew.tools.latex_generator import generate_resume_pdf_from_json

# Load environment variables
load_dotenv()

# Streamlit Configuration
DEFAULT_TARGET_WORDS = 400
MIN_TARGET_WORDS = 300
MAX_TARGET_WORDS = 1000

# Fallback model list for when OpenAI API is unavailable
FALLBACK_MODELS = [
    "gpt-5-pro", "gpt-5", "gpt-5-mini", "gpt-5-nano",
    "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
    "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-4",
    "gpt-3.5-turbo-16k", "gpt-3.5-turbo"
]


@st.cache_data
def get_openai_chat_models():
    """Fetch available OpenAI chat models dynamically.

    Returns a filtered, sorted list of chat model IDs.
    Falls back to hardcoded list on error.
    """
    from openai import OpenAI

    try:
        client = OpenAI()
        models = [m.id for m in client.models.list()]

        # Regex patterns for filtering
        inc_pattern = re.compile(r"^(gpt-\d)", re.IGNORECASE)
        end_date_pattern = re.compile(r"-\d{4}-\d{2}-\d{2}$")
        exclude_pattern = re.compile(
            r"(whisper|sora|dall-e|tts|audio|image|embed(?:ding)?|"
            r"moderation|realtime|search|transcribe|diarize|codex|"
            r"davinci|babbage|instruct)",
            re.IGNORECASE
        )

        # Filter and sort models
        chat_models = sorted(
            (mid for mid in models
             if inc_pattern.search(mid) and not end_date_pattern.search(mid)
             and not exclude_pattern.search(mid)),
            reverse=True
        )

        return chat_models if chat_models else FALLBACK_MODELS

    except Exception:
        return FALLBACK_MODELS


# Page configuration
st.set_page_config(
    page_title="Resume Refiner Crew",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize all session state variables with default values."""
    defaults = {
        'processing': False,
        'completed': False,
        'result': None,
        'edited_json': None,
        'original_json': None,
        'process': None,
        'result_queue': None,
        'start_time': None,
        'elapsed_time': None,
        'show_logs': False,
        'balloons_shown': False,
        'show_reset_toast': False,
        'show_apply_toast': False,
        'editor_key': 0,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# Initialize session state
init_session_state()


def reset_session():
    """Reset session state for a new run."""
    st.session_state.processing = False
    st.session_state.completed = False
    st.session_state.result = None
    st.session_state.edited_json = None
    st.session_state.original_json = None
    st.session_state.process = None
    st.session_state.result_queue = None
    st.session_state.start_time = None
    st.session_state.elapsed_time = None
    st.session_state.show_logs = False
    st.session_state.balloons_shown = False
    st.session_state.show_reset_toast = False
    st.session_state.show_apply_toast = False
    st.session_state.editor_key = 0


def run_crew_process(resume_bytes, job_desc, api_key, model, target_words, result_queue):
    """Run crew in a separate process.

    Args:
        resume_bytes: Resume PDF bytes.
        job_desc: Job description text.
        api_key: OpenAI API key.
        model: OpenAI model name.
        target_words: Target word count.
        result_queue: multiprocessing.Queue for result communication.
    """
    result = run_crew_with_params(
        resume_pdf_bytes=resume_bytes,
        job_description=job_desc,
        api_key=api_key,
        model=model,
        target_words=target_words
    )

    # Put result in queue for main process to retrieve
    result_queue.put(result)


def get_current_progress():
    """Parse crew logs to determine current progress.

    Returns:
        tuple: (completed_count, agent_name, status_text, log_content)
    """
    log_file = Path(".crewai_temp/crew_logs.txt")

    if not log_file.exists():
        return (0, "Initializing", "Starting up...", "")

    log_content = log_file.read_text(encoding='utf-8')
    task_matches = re.findall(r'task_name="([^"]+)"', log_content)

    if not task_matches:
        return (0, "Initializing", "Starting up...", log_content)

    current_task = task_matches[-1]

    if current_task not in TASKS_INFO:
        return (0, "Unknown", "Processing...", log_content)

    position, agent_name, status_text = TASKS_INFO[current_task]
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


@st.dialog("📊 Optimization Report", width="large")
def show_optimization_report():
    """Display the optimization report in a modal dialog."""
    report_path = Path("output/final_report.md")

    if report_path.exists():
        report_content = report_path.read_text(encoding='utf-8')
        st.markdown(report_content)
    else:
        st.warning("Report file not found")

    # Close button at the end
    if st.button("Close", type="primary", use_container_width=True):
        st.rerun()


# ===== SIDEBAR: INPUTS =====

# Job Description
st.sidebar.subheader("1. Job Description")
job_description = st.sidebar.text_area(
    "Add the complete job posting",
    height=150,
    placeholder="Add the complete job description here",
    label_visibility="collapsed",
    help="Include the full job description with requirements and responsibilities, the text formatting is not important"
)

# Upload Resume
st.sidebar.subheader("2. Upload Resume")
uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=['pdf'],
    help="Upload your current resume in PDF format",
    label_visibility="collapsed"
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
        min_value=MIN_TARGET_WORDS,
        max_value=MAX_TARGET_WORDS,
        value=int(os.getenv("TARGET_RESUME_WORDS", str(DEFAULT_TARGET_WORDS))),
        step=50,
        help="400-600 words for single page, 600-800 for two pages"
    )

# Validate inputs
inputs_valid = (
    uploaded_file is not None
    and len(job_description.strip()) > 0
    and len(api_key.strip()) > 0
)

# Show input validation hints
if not inputs_valid:
    st.sidebar.warning("⚠️ Please complete all required inputs above")
else:
    st.sidebar.write("&nbsp;")

# Process Button
if st.sidebar.button(
    "🚀 Process Resume",
    type="primary",
    disabled=not inputs_valid or st.session_state.processing or st.session_state.completed,
    use_container_width=True
):
    # Safety check (should never be None due to button disabled state)
    if uploaded_file is not None:
        reset_session()
        st.session_state.processing = True
        st.session_state.start_time = time.time()

        # Create a queue for process communication
        st.session_state.result_queue = multiprocessing.Queue()

        # Start processing in background process (process isolation = automatic resource cleanup)
        st.session_state.process = multiprocessing.Process(
            target=run_crew_process,
            args=(
                uploaded_file.read(),
                job_description,
                api_key,
                model,
                target_words,
                st.session_state.result_queue
            )
        )
        st.session_state.process.start()
        st.rerun()
    else:
        st.error("No file uploaded")

# Reset Button
if st.sidebar.button("🔄 Start Over", disabled=not st.session_state.completed, use_container_width=True):
    reset_session()
    st.rerun()


# ===== MAIN CONTENT AREA =====

# Show title
st.title("📝 Resume Refiner Crew")
st.markdown("Transform your resume into a job-specific, ATS-optimized document")


# Fragment for auto-updating progress display
@st.fragment(run_every=1.0)
def show_processing_progress():
    """Auto-updating fragment that displays processing progress."""
    # Check if process has completed (checked every 1 second via fragment auto-refresh)
    if st.session_state.result_queue and not st.session_state.result_queue.empty():
        # Process finished - get result from queue
        result = st.session_state.result_queue.get()
        st.session_state.result = result
        st.session_state.processing = False
        st.session_state.completed = True

        # Terminate the process to release all resources (ChromaDB connections, file handles, etc.)
        if st.session_state.process and st.session_state.process.is_alive():
            st.session_state.process.terminate()
            st.session_state.process.join(timeout=5)
            # Force kill if it didn't terminate gracefully
            if st.session_state.process.is_alive():
                st.session_state.process.kill()

        # Store the elapsed time once when processing completes
        if st.session_state.start_time:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time
        st.rerun()

    # Get current progress
    completed, agent_name, status_text, logs = get_current_progress()

    # Manual elapsed time display (replaces spinner)
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        elapsed_str = f"{int(elapsed//60)}m {int(elapsed%60)}s"
        st.info(f"⏳ Working on your resume... (Elapsed: {elapsed_str})")
    else:
        st.info("⏳ Working on your resume...")

    # Crew image
    st.image("./media/agents-flow.png")

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
    # Call fragment - auto-updates every 1 second and checks for completion
    show_processing_progress()

# RESULTS PHASE
elif st.session_state.completed:
    result = st.session_state.result

    if result and result['success']:

        col_success, col_time = st.columns(2)

        with col_success:

            # Success message
            st.success("✅ Your optimized resume is ready!")
            if not st.session_state.balloons_shown:
                st.balloons()
                st.session_state.balloons_shown = True
        
        with col_time:
        # Show elapsed time
            if st.session_state.elapsed_time:
                elapsed = st.session_state.elapsed_time
                st.info(f"⏱️ Processing completed in {int(elapsed//60)}m {int(elapsed%60)}s")

        # OPTIMIZATION REPORT BUTTON
        if st.button("📊 View Optimization Report", use_container_width=True, type="secondary"):
            show_optimization_report()

        # COLLAPSIBLE EDIT RESUME SECTION
        with st.expander("✏️ Edit Structured Resume (Optional)", expanded=False):
            # Display toast messages after rerun
            if st.session_state.show_reset_toast:
                st.toast("Changes reset to original", icon="↩️")
                st.session_state.show_reset_toast = False

            if st.session_state.show_apply_toast:
                st.toast("PDF regenerated successfully", icon="✅")
                st.session_state.show_apply_toast = False

            json_path = Path("output/structured_resume.json")

            if json_path.exists():
                # Load original JSON if not already loaded
                if st.session_state.original_json is None:
                    original_content = json_path.read_text(encoding='utf-8')
                    # Format JSON for better readability
                    formatted_json = json.dumps(json.loads(original_content), indent=2)
                    st.session_state.original_json = formatted_json
                    st.session_state.edited_json = formatted_json

                st.info("Edit the structured resume data below and apply changes to regenerate the PDF")

                # JSON editor
                edited_json = st.text_area(
                    "Structured Resume JSON",
                    value=st.session_state.edited_json,
                    height=400,
                    key=f"json_editor_{st.session_state.editor_key}",
                    label_visibility="collapsed"
                )

                # Update session state
                st.session_state.edited_json = edited_json

                # Validate JSON
                try:
                    if edited_json is not None:
                        json.loads(edited_json)
                        json_valid = True
                        json_error = None
                    else:
                        json_valid = False
                        json_error = "No JSON content"
                except json.JSONDecodeError as e:
                    json_valid = False
                    json_error = str(e)

                # Show validation error
                if not json_valid:
                    st.error(f"Invalid JSON: {json_error}")

                # Buttons
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("↺ Reset Changes", use_container_width=True):
                        # Reload original JSON from file
                        original_content = json_path.read_text(encoding='utf-8')
                        formatted_json = json.dumps(json.loads(original_content), indent=2)
                        st.session_state.original_json = formatted_json
                        st.session_state.edited_json = formatted_json
                        st.session_state.editor_key += 1  # Force re-render

                        # Regenerate PDF from original JSON
                        with st.spinner("Regenerating PDF from original resume..."):
                            pdf_path = generate_resume_pdf_from_json(
                                json_path=str(json_path)
                            )
                            if pdf_path and st.session_state.result is not None:
                                st.session_state.result['pdf_path'] = pdf_path
                                st.session_state.show_reset_toast = True
                                st.rerun()
                            else:
                                st.error("PDF generation failed")

                with col2:
                    if st.button(
                        "✓ Apply Changes",
                        disabled=not json_valid,
                        type="primary",
                        use_container_width=True
                    ):
                        # Save edited JSON to new file (validated via button disabled state)
                        if edited_json is not None:
                            modified_json_path = Path("output/structured_resume_modified.json")
                            modified_json_path.write_text(edited_json, encoding='utf-8')

                            # Regenerate PDF from modified JSON
                            with st.spinner("Regenerating PDF from modified resume..."):
                                pdf_path = generate_resume_pdf_from_json(
                                    json_path=str(modified_json_path)
                                )
                                if pdf_path and st.session_state.result is not None:
                                    st.session_state.result['pdf_path'] = pdf_path
                                    st.session_state.show_apply_toast = True
                                    st.rerun()
                                else:
                                    st.error("PDF generation failed")
                        else:
                            st.error("No JSON content to save")
            else:
                st.warning("structured_resume.json not found")

        # DOWNLOAD BUTTONS (always visible)
        st.write("&nbsp;")
        col1, col2 = st.columns(2)

        # PDF Download
        with col1:
            pdf_path = Path(result['pdf_path'])
            if pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="📄 Download Optimized Resume PDF",
                        data=f.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
            else:
                st.error("PDF file not found")

        # ZIP Download (all artifacts)
        with col2:
            st.download_button(
                label="📦 Download All Artifacts",
                data=create_zip_archive(),
                file_name="resume_optimization_complete.zip",
                mime="application/zip",
                type="secondary",
                use_container_width=True
            )

        st.divider()

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
    1. **Paste** the complete job description
    2. **Upload** your current resume (PDF format)
    3. **Process** and watch the multi-agent system optimize your resume
    4. **Download** your tailored, ATS-optimized resume

    The system uses 7 specialized AI agents to analyze, optimize, and format your resume.
    """)
