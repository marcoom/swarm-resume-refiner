# Multi-stage Dockerfile for Resume Refiner Crew
# This container runs the Streamlit web interface for AI-powered resume optimization

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# - LaTeX for PDF generation (texlive-latex-base, texlive-latex-extra)
# - curl for health checks and potential future use
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager for fast dependency resolution
RUN pip install uv

# Create non-root user for security
# Using UID 1000 which is standard for first non-root user on most systems
RUN useradd -m -u 1000 -s /bin/bash crewai

# Set working directory
WORKDIR /app

# Copy all project files (exclusions handled by .dockerignore)
COPY . .

# Install Python dependencies using UV
RUN uv pip install --system -e .

# Create necessary directories and set ownership
# .crewai_temp: CrewAI temporary storage (created at runtime)
# knowledge: Input directory for resumes and job descriptions
# output: Output directory for generated files
RUN mkdir -p .crewai_temp knowledge output && \
    chown -R crewai:crewai /app

# Make start script executable
RUN chmod +x start.sh

# Expose Streamlit default port
EXPOSE 8501

# Switch to non-root user
USER crewai

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit application via start script
CMD ["./start.sh"]
