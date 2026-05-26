import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

# Streamlit is the library that creates the web UI (buttons, uploads, text, etc.)
import streamlit as st

# tempfile lets us create temporary files on disk from uploaded files
import tempfile

# importing your backend function that runs the entire NLP + matching pipeline
from match import match


# -------------------------
# PAGE CONFIGURATION
# -------------------------

# sets the browser tab title + page layout style
st.set_page_config(page_title="Resume ↔ Job Matcher", layout="centered")

# displays a large title at the top of the app
st.title("📄 AI Resume ↔ Job Description Matcher")

# displays a short description under the title
st.write("Upload a resume and a job description to get a match score.")


# -------------------------
# FILE UPLOAD SECTION
# -------------------------

# creates a file upload button for PDF resumes
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# creates a file upload button for job description text files
jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])


# -------------------------
# BUTTON TO RUN MODEL
# -------------------------

# creates a button; code inside runs ONLY when clicked
if st.button("Run Match"):

    # -------------------------
    # VALIDATION CHECK
    # -------------------------

    # if either file is missing, show error and stop execution
    if resume_file is None or jd_file is None:
        st.error("Please upload BOTH files.")

    # if both files exist, continue processing
    else:

        # -------------------------
        # SAVE UPLOADED FILES TEMPORARILY
        # -------------------------

        # create a temporary file for the PDF resume
        # delete=False means file stays after closing (needed for downstream use)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_resume:

            # write uploaded PDF bytes into temp file
            tmp_resume.write(resume_file.read())

            # store file path so match() can read it
            resume_path = tmp_resume.name


        # create a temporary file for job description text
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_jd:

            # write uploaded TXT bytes into temp file
            tmp_jd.write(jd_file.read())

            # store file path for backend processing
            jd_path = tmp_jd.name


        # -------------------------
        # CALL YOUR BACKEND PIPELINE
        # -------------------------

        # runs full NLP pipeline:
        # - extract resume
        # - extract JD
        # - compute embeddings
        # - compute scores
        result = match(resume_path, jd_path)


        # -------------------------
        # DISPLAY OUTPUTS
        # -------------------------

        # success message shown at top of results
        st.success("Match completed!")


        # shows the final weighted score (semantic + skill match)
        st.metric("Final Score", f"{result['final_score']:.2f}")

        # shows ONLY semantic similarity score (transformer-based)
        st.metric("Semantic Score", f"{result['semantic_score']:.2f}")

        # shows ONLY skill overlap score (rule-based)
        st.metric("Skill Score", f"{result['skill_score']:.2f}")


        # -------------------------
        # DEBUG / INSPECTION OUTPUT
        # -------------------------

        # section header for resume JSON output
        st.subheader("🔍 Resume Data")

        # prints structured resume dictionary (skills, education, etc.)
        st.json(result["resume_data"])


        # section header for job description JSON output
        st.subheader("📌 Job Description Data")

        # prints structured job description dictionary
        st.json(result["jd_data"])