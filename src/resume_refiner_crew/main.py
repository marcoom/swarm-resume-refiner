#!/usr/bin/env python
import os
import shutil
import warnings

from resume_refiner_crew.crew import ResumeRefinerCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {}

    try:
        storage_dir = "./.crewai_temp"
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)
        os.makedirs(storage_dir)
        os.environ["CREWAI_STORAGE_DIR"] = storage_dir

        crew = ResumeRefinerCrew().crew()
        crew.kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    
if __name__ == "__main__":
    run()