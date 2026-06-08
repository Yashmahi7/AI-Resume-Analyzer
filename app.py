import os
import streamlit as st
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.title("AI Resume Analyzer")
st.write("Upload your resume and get ATS score, missing skills, and improvement suggestions.")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please add GEMINI_API_KEY in your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)


def get_working_model():
    try:
        available_models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]

        preferred_models = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-pro"
]

        for model_name in preferred_models:
            if model_name in available_models:
                return genai.GenerativeModel(model_name), model_name

        if available_models:
            return genai.GenerativeModel(available_models[0]), available_models[0]

        return None, None

    except Exception as e:
        st.error("Could not load Gemini models.")
        st.write(e)
        st.stop()


model, MODEL_NAME = get_working_model()

if model is None:
    st.error("No Gemini model available for your API key.")
    st.stop()

st.success(f"Using Gemini Model: {MODEL_NAME}")


uploaded_file = st.file_uploader("Upload your Resume PDF", type=["pdf"])

job_role = st.text_input("Enter Target Job Role", "Data Analyst")

job_description = st.text_area(
    "Paste Job Description Optional",
    placeholder="Paste job description here for better matching..."
)


def extract_text_from_pdf(file):
    text = ""

    pdf_reader = PyPDF2.PdfReader(file)

    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def analyze_resume(resume_text, job_role, job_description):
    resume_text = resume_text[:6000]
    job_description = job_description[:3000]

    prompt = f"""
You are an expert ATS Resume Analyzer and Career Coach.

Analyze the resume for this target role.

Target Job Role:
{job_role}

Job Description:
{job_description}

Resume Text:
{resume_text}

Give the answer in this exact format:

1. ATS Score out of 100

2. Resume Summary

3. Best Suitable Job Roles

4. Skills Found in Resume

5. Missing Skills for the Target Role

6. Missing Keywords

7. Resume Strengths

8. Resume Weaknesses

9. Project Improvement Suggestions

10. LinkedIn Profile Improvement Suggestions

11. Naukri Profile Improvement Suggestions

12. Interview Preparation Suggestions

13. Final Recommendation

Give clear, simple, and practical suggestions.
"""

    response = model.generate_content(prompt)
    return response.text


if uploaded_file is not None:
    st.success("Resume uploaded successfully!")

    resume_text = extract_text_from_pdf(uploaded_file)

    with st.expander("View Extracted Resume Text"):
        st.write(resume_text)

    if st.button("Analyze Resume"):
        if resume_text.strip() == "":
            st.error("Could not extract text from this PDF. Please upload a text-based resume PDF.")
        else:
            try:
                with st.spinner("Analyzing resume using Gemini AI..."):
                    result = analyze_resume(resume_text, job_role, job_description)

                st.subheader("AI Resume Analysis Result")
                st.write(result)

            except Exception as e:
                st.error("Something went wrong while analyzing the resume.")
                st.write(e)

else:
    st.info("Please upload your resume PDF to start analysis.")