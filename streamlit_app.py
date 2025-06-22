import streamlit as st
import requests
import re
from utils.pdf_utils import extract_text_from_pdf

st.set_page_config(page_title="ATS Resume Analyzer Bot", layout="wide")
st.title("📄 ATS Resume Analyzer")

st.markdown("Upload your **resume PDF** and paste the **job description**.")

def clean_text(text):
    # Remove control characters except \n and \t
    return re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""

uploaded_pdf = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_description = st.text_area("📋 Job Description", height=300, placeholder="Paste the job description here...")

resume_text = ""
if uploaded_pdf:
    try:
        resume_text = extract_text_from_pdf(uploaded_pdf)
        resume_text = clean_text(resume_text)
        st.success("✅ Resume text extracted successfully!")
        with st.expander("📃 View Extracted Resume Text"):
            st.write(resume_text)
    except Exception as e:
        st.error(f"❌ Failed to extract text from PDF: {str(e)}")

if st.button("🚀 Analyze Resume"):
    if resume_text and job_description:
        with st.spinner("Analyzing your resume..."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze-resume",
                    json={
                        "resume": resume_text,
                        "job_description": job_description
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        st.session_state.analysis_result = result.get("response", "No analysis provided")
                        st.session_state.analysis_done = True
                        st.success("✅ Analysis complete!")
                    else:
                        st.error("❌ Analysis failed")
                else:
                    st.error(f"❌ Server error: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the server. Make sure the FastAPI server is running on localhost:8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please upload a resume and provide a job description.")

# Display analysis results
if st.session_state.analysis_done and st.session_state.analysis_result:
    st.markdown("### 📊 ATS Analysis Result")
    st.markdown(st.session_state.analysis_result)
    
    # Course recommendation section
    st.markdown("---")
    st.markdown("### 🎓 Want to Learn Missing Skills?")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        skill_to_learn = st.text_input(
            "Enter a skill you want to learn:", 
            placeholder="e.g., Python, Machine Learning, React, etc."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        if st.button("🔍 Find Course"):
            if skill_to_learn:
                with st.spinner(f"Searching for {skill_to_learn} courses..."):
                    try:
                        course_response = requests.post(
                            "http://localhost:8000/find-course",
                            json={"skill": skill_to_learn},
                            timeout=30
                        )
                        
                        if course_response.status_code == 200:
                            course_result = course_response.json()
                            if course_result.get("status") == "success":
                                st.markdown("### 🎯 Recommended Course")
                                st.markdown(course_result.get("response", "No course found"))
                            else:
                                st.error("❌ Course search failed")
                        else:
                            st.error(f"❌ Course search error: {course_response.status_code}")
                            
                    except requests.exceptions.Timeout:
                        st.error("❌ Course search timed out. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to the server for course search.")
                    except Exception as e:
                        st.error(f"❌ Course search error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a skill to search for.")

# Sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Upload your resume** in PDF format
    2. **Paste the job description** you're applying for
    3. **Click 'Analyze Resume'** to get ATS feedback
    4. **Enter missing skills** to find relevant courses
    5. **Click 'Find Course'** to get Udemy recommendations
    """)
    
    st.markdown("### ⚙️ Requirements")
    st.markdown("""
    - Make sure the FastAPI server is running
    - Upload PDF files only
    - Provide complete job descriptions for better analysis
    """)