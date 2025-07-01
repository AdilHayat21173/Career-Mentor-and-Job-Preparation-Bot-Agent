# import streamlit as st
# import requests
# import re
# from utils.pdf_utils import extract_text_from_pdf
# import time

# st.set_page_config(page_title="Career Mentor Bot", layout="wide")
# st.title("🤖 Career Mentor & Job Preparation Bot")

# # Configuration
# API_BASE_URL = "http://localhost:8000"
# DEFAULT_TIMEOUT = 60  # Increased timeout

# def check_api_connection():
#     """Check if the FastAPI server is running"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/", timeout=5)
#         return response.status_code == 200
#     except:
#         return False

# def make_api_request(endpoint, data=None, timeout=DEFAULT_TIMEOUT):
#     """Make API request with proper error handling"""
#     try:
#         if data:
#             response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=timeout)
#         else:
#             response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=timeout)
        
#         if response.status_code == 200:
#             return response.json(), None
#         else:
#             return None, f"API returned status code: {response.status_code}"
#     except requests.exceptions.Timeout:
#         return None, "Request timed out. The server might be processing a large request."
#     except requests.exceptions.ConnectionError:
#         return None, "Cannot connect to the server. Make sure the FastAPI server is running on localhost:8000"
#     except requests.exceptions.RequestException as e:
#         return None, f"Request failed: {str(e)}"

# # Check API connection status
# if not check_api_connection():
#     st.error("⚠️ **Cannot connect to the FastAPI server!**")
#     st.markdown("""
#     **Please ensure:**
#     1. Your FastAPI server is running on `localhost:8000`
#     2. Run your FastAPI server with: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
#     3. Check if there are any errors in your FastAPI server logs
#     """)
#     st.stop()
# else:
#     st.success("✅ Connected to FastAPI server")

# # Initialize session state
# if "jobs" not in st.session_state:
#     st.session_state["jobs"] = []
# if "selected_job" not in st.session_state:
#     st.session_state["selected_job"] = None
# if "resume_text" not in st.session_state:
#     st.session_state["resume_text"] = None
# if "job_description" not in st.session_state:
#     st.session_state["job_description"] = None

# # --- 1. Job Search ---
# st.header("🔎 Search for Jobs")
# search_field = st.text_input("Enter job title or skill (e.g., Python Developer):")
# search_location = st.text_input("Enter location (optional):")

# if st.button("Search LinkedIn Jobs"):
#     if not search_field.strip():
#         st.error("Please enter a job title or skill to search for.")
#     else:
#         with st.spinner("Searching jobs... This may take a moment."):
#             data = {
#                 "field": search_field.strip(),
#                 "geoid": search_location.strip() or "101022442",
#                 "page": "1"
#             }
            
#             result, error = make_api_request("/find-linkedin-jobs", data, timeout=90)
            
#             if error:
#                 st.error(f"Failed to fetch jobs: {error}")
#                 st.info("💡 Try refreshing the page or check if your FastAPI server is running properly.")
#             elif result and result.get("status") == "success":
#                 jobs = result["response"]
#                 if isinstance(jobs, str):
#                     st.session_state["jobs"] = [job.strip() for job in jobs.split("\n\n") if job.strip()]
#                 else:
#                     st.session_state["jobs"] = jobs
#                 st.success(f"Found {len(st.session_state['jobs'])} jobs!")
#             else:
#                 st.error("No jobs found or invalid response from server.")

# # Display jobs if available
# if st.session_state["jobs"]:
#     st.subheader("Recent LinkedIn Jobs")
    
#     # Show jobs in a more user-friendly way
#     for i, job in enumerate(st.session_state["jobs"][:10]):  # Limit to first 10 jobs
#         with st.expander(f"Job {i+1}: {job[:100]}..."):
#             st.write(job)
#             if st.button(f"Select This Job", key=f"select_job_{i}"):
#                 st.session_state["selected_job"] = job
#                 st.success("Job selected!")
#                 st.rerun()

# # --- 2. Resume Upload ---
# if st.session_state["selected_job"]:
#     st.header("📄 Upload Your Resume")
#     st.info(f"**Selected Job:** {st.session_state['selected_job'][:200]}...")
    
#     uploaded_pdf = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
#     if uploaded_pdf:
#         try:
#             # Extract resume text
#             resume_text = extract_text_from_pdf(uploaded_pdf)
#             if resume_text.strip():
#                 st.session_state["resume_text"] = resume_text
#                 st.session_state["job_description"] = st.session_state["selected_job"]
#                 st.success("✅ Resume uploaded successfully!")
#             else:
#                 st.error("Could not extract text from the PDF. Please make sure it's a valid PDF with text content.")
#         except Exception as e:
#             st.error(f"Error processing PDF: {str(e)}")

# # --- 3. Resume Analysis ---
# if st.session_state.get("resume_text") and st.session_state.get("job_description"):
#     st.header("📊 Resume & Job Description Analysis")
    
#     if st.button("Analyze Resume"):
#         with st.spinner("Analyzing resume... This may take up to 2 minutes."):
#             data = {
#                 "resume": st.session_state["resume_text"],
#                 "job_description": st.session_state["job_description"]
#             }
            
#             result, error = make_api_request("/analyze-resume", data, timeout=120)
            
#             if error:
#                 st.error(f"Analysis failed: {error}")
#             elif result and result.get("status") == "success":
#                 st.session_state["analysis_result"] = result["response"]
#                 st.success("✅ Analysis complete!")
#             else:
#                 st.error("Analysis failed. Please try again.")

#     # Display analysis result
#     if st.session_state.get("analysis_result"):
#         st.subheader("📋 Analysis Results")
#         st.markdown(st.session_state["analysis_result"])

#         # --- 4. Skill Learning ---
#         st.header("🎓 Learn Missing Skills")
#         skill = st.text_input("Enter a skill to learn (from missing/recommended skills above):")
        
#         if skill.strip():
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 if st.button("Find Udemy Course"):
#                     with st.spinner("Searching for courses..."):
#                         result, error = make_api_request("/find-course", {"skill": skill.strip()})
#                         if error:
#                             st.error(f"Course search failed: {error}")
#                         else:
#                             st.write(result.get("response", "No course found."))
            
#             with col2:
#                 if st.button("Find YouTube Videos"):
#                     with st.spinner("Searching for videos..."):
#                         result, error = make_api_request("/find-youtube", {"query": skill.strip()})
#                         if error:
#                             st.error(f"Video search failed: {error}")
#                         else:
#                             st.write(result.get("response", "No videos found."))

#         # --- 5. Interview Preparation ---
#         st.header("🗣️ Interview Preparation")
        
#         # Initialize interview session state variables
#         if "interview_started" not in st.session_state:
#             st.session_state["interview_started"] = False
#         if "interview_questions" not in st.session_state:
#             st.session_state["interview_questions"] = []
#         if "interview_answers" not in st.session_state:
#             st.session_state["interview_answers"] = []
#         if "current_question_index" not in st.session_state:
#             st.session_state["current_question_index"] = 0
#         if "interview_completed" not in st.session_state:
#             st.session_state["interview_completed"] = False
#         if "interview_evaluation" not in st.session_state:
#             st.session_state["interview_evaluation"] = ""
        
#         # Show current interview status
#         if st.session_state["interview_started"]:
#             total_questions = len(st.session_state["interview_questions"])
#             current_q = st.session_state["current_question_index"]
#             st.info(f"📊 Interview Progress: Question {current_q + 1} of {total_questions}")
        
#         # Start Interview Button
#         if not st.session_state["interview_started"] and not st.session_state["interview_completed"]:
#             if st.button("🚀 Start Interview Practice", type="primary"):
#                 with st.spinner("Preparing interview questions... This may take a moment."):
#                     data = {"job_description": st.session_state["job_description"]}
#                     result, error = make_api_request("/interview/start", data)
                    
#                     if error:
#                         st.error(f"❌ Failed to start interview: {error}")
#                         st.info("💡 Try checking your FastAPI server logs for more details.")
#                     elif result and result.get("status") == "success":
#                         # Handle different response formats
#                         if "questions" in result:
#                             questions = result["questions"]
#                         elif "response" in result and isinstance(result["response"], list):
#                             questions = result["response"]
#                         elif "response" in result and isinstance(result["response"], str):
#                             # If response is a string, try to parse it
#                             questions = [q.strip() for q in result["response"].split('\n') if q.strip()]
#                         else:
#                             questions = ["Tell me about yourself.", "Why are you interested in this position?", "What are your strengths?"]
                        
#                         st.session_state["interview_questions"] = questions
#                         st.session_state["interview_started"] = True
#                         st.session_state["current_question_index"] = 0
#                         st.session_state["interview_answers"] = []
#                         st.success(f"✅ Interview started! {len(questions)} questions prepared.")
#                         st.rerun()
#                     else:
#                         st.error("❌ Failed to start interview. Please try again.")
#                         st.write("**Debug:** Server response:", result)

#         # Reset Interview Button
#         if st.session_state["interview_started"] or st.session_state["interview_completed"]:
#             if st.button("🔄 Reset Interview"):
#                 # Clear all interview-related session state
#                 st.session_state["interview_started"] = False
#                 st.session_state["interview_questions"] = []
#                 st.session_state["interview_answers"] = []
#                 st.session_state["current_question_index"] = 0
#                 st.session_state["interview_completed"] = False
#                 st.session_state["interview_evaluation"] = ""
#                 st.success("Interview reset! You can start a new interview.")
#                 st.rerun()

# # --- 6. Interview Questions Section ---
# if st.session_state.get("interview_started") and not st.session_state.get("interview_completed"):
#     st.header("🎯 Interview in Progress")
    
#     questions = st.session_state["interview_questions"]
#     current_index = st.session_state["current_question_index"]
    
#     if current_index < len(questions):
#         # Show current question
#         current_question = questions[current_index]
#         st.subheader(f"Question {current_index + 1} of {len(questions)}")
        
#         # Display the question in a nice format
#         st.markdown(f"""
#         <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
#             <h4 style="color: #1f77b4; margin: 0;">❓ {current_question}</h4>
#         </div>
#         """, unsafe_allow_html=True)
        
#         # Answer input
#         answer_key = f"interview_answer_{current_index}"
#         user_answer = st.text_area(
#             "💭 Your Answer:",
#             key=answer_key,
#             height=150,
#             placeholder="Take your time to provide a detailed answer..."
#         )
        
#         # Navigation buttons
#         col1, col2, col3 = st.columns([1, 1, 1])
        
#         with col1:
#             if current_index > 0:
#                 if st.button("⬅️ Previous Question"):
#                     st.session_state["current_question_index"] -= 1
#                     st.rerun()
        
#         with col2:
#             if st.button("✅ Submit Answer", type="primary", disabled=not user_answer.strip()):
#                 if user_answer.strip():
#                     # Save the answer
#                     if len(st.session_state["interview_answers"]) <= current_index:
#                         st.session_state["interview_answers"].extend([''] * (current_index + 1 - len(st.session_state["interview_answers"])))
#                     st.session_state["interview_answers"][current_index] = user_answer.strip()
                    
#                     # Move to next question or complete interview
#                     if current_index + 1 < len(questions):
#                         st.session_state["current_question_index"] += 1
#                         st.success("Answer saved! Moving to next question...")
#                         time.sleep(1)
#                         st.rerun()
#                     else:
#                         # Interview completed, get evaluation
#                         with st.spinner("🔄 Evaluating your interview performance..."):
#                             data = {
#                                 "job_description": st.session_state["job_description"],
#                                 "questions": st.session_state["interview_questions"],
#                                 "answers": st.session_state["interview_answers"]
#                             }
                            
#                             # Try different evaluation endpoints
#                             result, error = make_api_request("/interview/evaluate", data, timeout=120)
#                             if error:
#                                 # Try alternative endpoint
#                                 result, error = make_api_request("/interview/complete", data, timeout=120)
                            
#                             if error:
#                                 st.error(f"❌ Failed to evaluate interview: {error}")
#                                 # Provide basic completion without evaluation
#                                 st.session_state["interview_completed"] = True
#                                 st.session_state["interview_evaluation"] = "Interview completed! Unfortunately, we couldn't generate an evaluation at this time."
#                             elif result:
#                                 st.session_state["interview_completed"] = True
#                                 evaluation = result.get("evaluation") or result.get("response") or "Interview completed successfully!"
#                                 st.session_state["interview_evaluation"] = evaluation
                            
#                             st.success("🎉 Interview completed!")
#                             st.rerun()
#                 else:
#                     st.warning("⚠️ Please provide an answer before submitting.")
        
#         with col3:
#             if current_index + 1 < len(questions):
#                 if st.button("➡️ Next Question"):
#                     # Save current answer if provided
#                     if user_answer.strip():
#                         if len(st.session_state["interview_answers"]) <= current_index:
#                             st.session_state["interview_answers"].extend([''] * (current_index + 1 - len(st.session_state["interview_answers"])))
#                         st.session_state["interview_answers"][current_index] = user_answer.strip()
                    
#                     st.session_state["current_question_index"] += 1
#                     st.rerun()
        
#         # Show progress
#         progress = (current_index + 1) / len(questions)
#         st.progress(progress)
        
#         # Show answered questions summary
#         if st.session_state["interview_answers"]:
#             with st.expander("📝 Your Answers So Far"):
#                 for i, ans in enumerate(st.session_state["interview_answers"]):
#                     if ans:
#                         st.write(f"**Q{i+1}:** {questions[i]}")
#                         st.write(f"**A{i+1}:** {ans}")
#                         st.write("---")

# # --- 7. Interview Results ---
# if st.session_state.get("interview_completed"):
#     st.header("🎉 Interview Complete!")
    
#     # Show completion celebration
#     st.balloons()
    
#     st.success("Congratulations! You've completed the interview practice session.")
    
#     # Show evaluation if available
#     if st.session_state.get("interview_evaluation"):
#         st.subheader("📊 Interview Evaluation")
#         st.markdown(st.session_state["interview_evaluation"])
    
#     # Show full Q&A summary
#     st.subheader("📋 Complete Interview Summary")
#     questions = st.session_state.get("interview_questions", [])
#     answers = st.session_state.get("interview_answers", [])
    
#     for i, (question, answer) in enumerate(zip(questions, answers)):
#         with st.expander(f"Question {i+1}: {question[:50]}..."):
#             st.write(f"**Question:** {question}")
#             st.write(f"**Your Answer:** {answer}")
    
#     # Download option
#     if st.button("📥 Download Interview Summary"):
#         summary = "# Interview Practice Summary\n\n"
#         summary += f"**Job Description:** {st.session_state['job_description'][:200]}...\n\n"
#         summary += "## Questions and Answers\n\n"
        
#         for i, (question, answer) in enumerate(zip(questions, answers)):
#             summary += f"### Question {i+1}\n{question}\n\n"
#             summary += f"**Answer:** {answer}\n\n"
        
#         if st.session_state.get("interview_evaluation"):
#             summary += "## Evaluation\n\n"
#             summary += st.session_state["interview_evaluation"]
        
#         st.download_button(
#             label="Download as Text File",
#             data=summary,
#             file_name="interview_practice_summary.txt",
#             mime="text/plain"
#         )

# # Sidebar with instructions
# with st.sidebar:
#     st.markdown("### 📋 Instructions")
#     st.markdown("""
#     1. **Search for jobs** using keywords and location
#     2. **Select a job** from the LinkedIn job listings
#     3. **Upload your resume** in PDF format
#     4. **Click 'Analyze Resume'** to get ATS feedback
#     5. **Enter missing skills** to find relevant courses or videos
#     6. **Prepare for interviews** with the interview practice feature
#     """)
    
#     st.markdown("### ⚙️ Requirements")
#     st.markdown("""
#     - FastAPI server must be running on localhost:8000
#     - Upload PDF files only
#     - Provide complete job descriptions for better analysis
#     """)
    
#     st.markdown("### 🛠️ Troubleshooting")
#     st.markdown("""
#     - If you see timeout errors, wait and try again
#     - Check FastAPI server logs for errors
#     - Restart the FastAPI server if needed
#     """)

# # Debug information
# with st.expander("🔧 Debug Information"):
#     st.write("**Session State Keys:**", list(st.session_state.keys()))
#     st.write("**API Base URL:**", API_BASE_URL)
#     st.write("**Server Status:**", "✅ Connected" if check_api_connection() else "❌ Disconnected")

import streamlit as st
import requests
import re
from utils.pdf_utils import extract_text_from_pdf
import time
import json

st.set_page_config(page_title="Career Mentor Chat Bot", layout="wide", page_icon="🤖")

# Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 60

def check_api_connection():
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_api_request(endpoint, data=None, timeout=DEFAULT_TIMEOUT):
    """Make API request with proper error handling"""
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=timeout)
        else:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=timeout)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API returned status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "Request timed out. The server might be processing a large request."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the server. Make sure the FastAPI server is running on localhost:8000"
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {str(e)}"

class CareerMentorBot:
    def __init__(self):
        self.states = {
            "WELCOME": "welcome",
            "JOB_SEARCH": "job_search", 
            "JOB_SELECTION": "job_selection",
            "RESUME_UPLOAD": "resume_upload",
            "RESUME_ANALYSIS": "resume_analysis",
            "SKILL_LEARNING": "skill_learning",
            "INTERVIEW_PREP": "interview_prep",
            "INTERVIEW_QUESTIONS": "interview_questions",
            "INTERVIEW_COMPLETE": "interview_complete"
        }
    
    def get_welcome_message(self):
        return """
👋 **Welcome to Career Mentor Bot!** 

I'm here to help you with your job search and career preparation. I can assist you with:

🔍 **Job Search** - Find recent LinkedIn jobs
📄 **Resume Analysis** - Check ATS compatibility and get improvement suggestions  
🎓 **Skill Learning** - Find courses and tutorials for missing skills
🗣️ **Interview Preparation** - Practice with job-specific questions

**To get started, please type what you're looking for. For example:**
- "I want to search for Python developer jobs"
- "Find software engineer jobs in New York" 
- "Search for data analyst positions"

What would you like to do today?
"""

    def process_job_search(self, query):
        """Extract job title and location from user query"""
        # Simple keyword extraction - you can make this more sophisticated
        query_lower = query.lower()
        
        # Common job titles
        job_titles = ['developer', 'engineer', 'analyst', 'manager', 'designer', 'consultant', 
                     'specialist', 'coordinator', 'administrator', 'technician', 'scientist']
        
        job_title = ""
        location = ""
        
        for title in job_titles:
            if title in query_lower:
                # Extract surrounding words
                words = query.split()
                for i, word in enumerate(words):
                    if title in word.lower():
                        # Get 1-2 words before the title
                        start = max(0, i-2)
                        end = min(len(words), i+2)
                        job_title = " ".join(words[start:end])
                        break
                break
        
        # Extract location if mentioned
        location_keywords = ['in ', 'at ', 'from ']
        for keyword in location_keywords:
            if keyword in query_lower:
                parts = query_lower.split(keyword)
                if len(parts) > 1:
                    location = parts[-1].strip()
                    break
        
        if not job_title:
            job_title = query  # Use entire query as job title if no specific match
            
        return job_title.strip(), location.strip()

    def format_jobs_response(self, jobs):
        """Format jobs list for display"""
        if not jobs:
            return "❌ No jobs found. Please try with different keywords."
        
        response = f"🎉 **Found {len(jobs)} recent LinkedIn jobs!**\n\n"
        
        for i, job in enumerate(jobs[:10], 1):  # Show max 10 jobs
            # Truncate long job descriptions
            job_preview = job[:200] + "..." if len(job) > 200 else job
            response += f"**Job {i}:**\n{job_preview}\n\n"
        
        response += "📝 **To select a job, simply type:** 'Select job 1' or 'I want job 3', etc.\n"
        response += "🔄 **To search again:** Type 'search for [job title]'"
        
        return response

    def extract_job_number(self, user_input):
        """Extract job number from user selection"""
        import re
        numbers = re.findall(r'\d+', user_input.lower())
        if numbers:
            return int(numbers[0]) - 1  # Convert to 0-based index
        return None

    def get_job_description_for_analysis(self, job):
        """Convert job dict to string format for analysis"""
        if isinstance(job, dict):
            # Create a comprehensive job description from the structured data
            job_description = f"""
Job Position: {job.get('job_position', 'N/A')}
Company: {job.get('company_name', 'N/A')}
Location: {job.get('job_location', 'N/A')}
Posted Date: {job.get('job_posting_date', 'N/A')}
Job Link: {job.get('job_link', '#')}
Company Profile: {job.get('company_profile', '#')}

Job Requirements and Description:
{job.get('job_description', 'No detailed description available')}
"""
            return job_description
        else:
            # Return as-is if it's already a string
            return str(job)
        
def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "bot" not in st.session_state:
        st.session_state.bot = CareerMentorBot()
    if "current_state" not in st.session_state:
        st.session_state.current_state = "welcome"
    if "jobs_list" not in st.session_state:
        st.session_state.jobs_list = []
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "interview_answers" not in st.session_state:
        st.session_state.interview_answers = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "waiting_for_resume" not in st.session_state:
        st.session_state.waiting_for_resume = False
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False

def add_message(role, content):
    """Add message to chat history"""
    st.session_state.messages.append({"role": role, "content": content})

def display_chat_messages():
    """Display all chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def start_interview():
    """Start interview using the /interview endpoint"""
    with st.spinner("🎯 Generating interview questions..."):
        data = {
            "job_description": st.session_state.selected_job,
            "current_step": 0,
            "answer": None,
            "answers": [],
            "questions": []
        }
        
        result, error = make_api_request("/interview", data)
        
        if error:
            return f"❌ Failed to start interview: {error}", False
        elif result and result.get("status") == "success":
            interview_data = result.get("data", {})
            
            if interview_data.get("action") == "ask_question":
                questions = interview_data.get("questions", [])
                current_question = interview_data.get("current_question", "")
                
                st.session_state.interview_questions = questions
                st.session_state.current_question_index = 0
                st.session_state.interview_answers = []
                st.session_state.interview_started = True
                st.session_state.current_state = "interview_questions"
                
                return f"""
🎯 **Interview Started Successfully!**

I've prepared {len(questions)} questions for you based on the job description.

**Question 1 of {len(questions)}:**
❓ {current_question}

Please provide your answer, and I'll move to the next question.

**Commands:**
- Type your answer naturally
- "**skip**" to skip this question
- "**finish**" to complete interview early
""", True
            else:
                return "❌ Unexpected response from interview API", False
        else:
            return "❌ Failed to start interview. Please try again.", False

def submit_interview_answer(answer):
    """Submit an answer to the current interview question"""
    current_step = st.session_state.current_question_index + 1
    updated_answers = st.session_state.interview_answers.copy()
    
    # Ensure answers list is long enough
    while len(updated_answers) <= st.session_state.current_question_index:
        updated_answers.append("")
    
    updated_answers[st.session_state.current_question_index] = answer
    
    data = {
        "job_description": st.session_state.selected_job,
        "current_step": current_step,
        "answer": answer,
        "answers": updated_answers,
        "questions": st.session_state.interview_questions
    }
    
    result, error = make_api_request("/interview", data)
    
    if error:
        return f"❌ Failed to submit answer: {error}", False
    elif result and result.get("status") == "success":
        interview_data = result.get("data", {})
        action = interview_data.get("action")
        
        # Update stored answers
        st.session_state.interview_answers = updated_answers
        
        if action == "ask_question":
            # Move to next question
            st.session_state.current_question_index += 1
            next_question = interview_data.get("current_question", "")
            
            return f"""
✅ **Answer saved!**

**Question {st.session_state.current_question_index + 1} of {len(st.session_state.interview_questions)}:**
❓ {next_question}

Please provide your answer.

**Progress:** {st.session_state.current_question_index + 1}/{len(st.session_state.interview_questions)} questions completed
""", True
            
        elif action == "interview_complete":
            # Interview finished, show evaluation
            st.session_state.current_state = "interview_complete"
            evaluation = interview_data.get("evaluation", "Interview completed successfully!")
            
            return f"""
🎉 **Interview Complete!**

📊 **Evaluation:**
{evaluation}

📋 **Interview Summary:**
- **Total Questions:** {len(st.session_state.interview_questions)}
- **Questions Answered:** {len([a for a in st.session_state.interview_answers if a.strip()])}

**What would you like to do next?**
- **"new job search"** - Find more opportunities
- **"learn skills"** - Improve identified weak areas
- **"practice again"** - Do another interview round
""", True
        else:
            return f"Unexpected response: {action}", False
    else:
        return "❌ Failed to process answer. Please try again.", False

def process_user_input(user_input):
    """Process user input based on current state"""
    bot = st.session_state.bot
    current_state = st.session_state.current_state
    
    user_input_lower = user_input.lower()
    
    # Welcome state
    if current_state == "welcome":
        if any(word in user_input_lower for word in ["search", "find", "job", "position"]):
            job_title, location = bot.process_job_search(user_input)
            
            # Make API call to search jobs
            with st.spinner("🔍 Searching for jobs..."):
                data = {
                    "field": job_title,
                    "geoid": location or "101022442",
                    "page": "1"
                }
                
                result, error = make_api_request("/find-linkedin-jobs", data, timeout=90)
                
                if error:
                    return f"❌ **Job search failed:** {error}\n\nPlease try again or check if the server is running."
                elif result and result.get("status") == "success":
                    jobs = result["response"]
                    if isinstance(jobs, str):
                        st.session_state.jobs_list = [job.strip() for job in jobs.split("\n\n") if job.strip()]
                    else:
                        st.session_state.jobs_list = jobs
                    
                    st.session_state.current_state = "job_selection"
                    return bot.format_jobs_response(st.session_state.jobs_list)
                else:
                    return "❌ No jobs found. Please try with different keywords."
        else:
            return bot.get_welcome_message()
    
    # Job selection state
    elif current_state == "job_selection":
        if "search" in user_input_lower and any(word in user_input_lower for word in ["job", "find"]):
            # New search
            st.session_state.current_state = "welcome"
            return process_user_input(user_input)
        
        job_index = bot.extract_job_number(user_input)
        if job_index is not None and 0 <= job_index < len(st.session_state.jobs_list):
            st.session_state.selected_job = st.session_state.jobs_list[job_index]
            st.session_state.current_state = "resume_upload"
            st.session_state.waiting_for_resume = True
            
            return f"""
✅ **Great! You've selected:**
{st.session_state.selected_job[:300]}...

📄 **Next Step: Upload Your Resume**

Please upload your resume (PDF format) using the file uploader below so I can analyze it against this job description.

Once uploaded, I'll:
- Check ATS compatibility 
- Identify missing skills
- Provide improvement recommendations
- Help you prepare for interviews
"""
        else:
            return f"""
❌ **Invalid selection.** Please select a job by typing:
- "Select job 1" 
- "I want job 2"
- etc.

Or type "search for [new job title]" to start a new search.
"""
    
    # Resume analysis state
    elif current_state == "resume_analysis":
        if "skill" in user_input_lower and ("learn" in user_input_lower or "course" in user_input_lower or "youtube" in user_input_lower):
            # Extract skill from input
            skill = user_input.replace("learn", "").replace("skill", "").replace("course", "").strip()
            st.session_state.current_state = "skill_learning"
            
            return f"""
🎓 **Great! Let me find learning resources for: {skill}**

What type of resources would you prefer?
- Type "**udemy course**" for Udemy courses
- Type "**youtube videos**" for YouTube tutorials  
- Type "**both**" for both options

Or specify another skill you'd like to learn.
"""
        
        elif "interview" in user_input_lower and ("prepare" in user_input_lower or "practice" in user_input_lower):
            st.session_state.current_state = "interview_prep" 
            
            return """
🗣️ **Excellent! Let's prepare you for the interview.**

I'll generate relevant interview questions based on the job description you selected.

**Ready to start?** Type:
- "**start interview**" to begin practice
- "**generate questions**" to see the questions first

The interview will include 5-10 questions covering:
- Technical skills
- Behavioral questions  
- Job-specific scenarios
"""
        
        else:
            job_desc = st.session_state.bot.get_job_description_for_analysis(st.session_state.selected_job)
            return f"""
📊 **Your resume analysis is complete!** 

{st.session_state.analysis_result}

**What would you like to do next?**

🎓 **Learn Skills:** Type "learn [skill name]" (e.g., "learn Python")
🗣️ **Interview Prep:** Type "prepare for interview" 
🔍 **New Job Search:** Type "search for [job title]"
"""
    
    # Skill learning state  
    elif current_state == "skill_learning":
        if "udemy" in user_input_lower:
            # Get skill from previous context or extract from input
            skill_to_search = user_input.replace("udemy", "").replace("course", "").strip()
            if not skill_to_search:
                return "Please specify which skill you'd like to find Udemy courses for."
            
            with st.spinner("🔍 Finding Udemy courses..."):
                result, error = make_api_request("/find-course", {"skill": skill_to_search})
                if error:
                    return f"❌ Course search failed: {error}"
                else:
                    course_info = result.get("response", "No courses found.")
                    return f"📚 **Udemy Courses for {skill_to_search}:**\n\n{course_info}\n\n**Need more help?** Type 'youtube videos' for video tutorials or 'learn [another skill]'."
        
        elif "youtube" in user_input_lower:
            skill_to_search = user_input.replace("youtube", "").replace("videos", "").strip()
            if not skill_to_search:
                return "Please specify which skill you'd like to find YouTube videos for."
            
            with st.spinner("🔍 Finding YouTube videos..."):
                result, error = make_api_request("/find-youtube", {"query": skill_to_search})
                if error:
                    return f"❌ Video search failed: {error}"
                else:
                    video_info = result.get("response", "No videos found.")
                    return f"🎥 **YouTube Videos for {skill_to_search}:**\n\n{video_info}\n\n**Need more help?** Type 'udemy course' for structured courses or 'learn [another skill]'."
        
        elif "both" in user_input_lower:
            # Get both Udemy and YouTube resources
            return """
🎓 **I'll find both Udemy courses and YouTube videos for you!**

Please specify the skill name, for example:
- "both for Python"
- "both for machine learning" 
- "both for React"
"""
        
        elif "interview" in user_input_lower:
            st.session_state.current_state = "interview_prep"
            return process_user_input(user_input)
        
        else:
            # Extract skill name and provide options
            skill = user_input.replace("learn", "").strip()
            return f"""
🎓 **Finding resources for: {skill}**

What would you prefer?
- **"udemy course"** - Structured paid courses
- **"youtube videos"** - Free video tutorials
- **"both"** - Both options

Or type **"prepare for interview"** if you're ready for interview practice.
"""
    
    # Interview preparation state
    elif current_state == "interview_prep":
        if "start" in user_input_lower or "begin" in user_input_lower or "generate" in user_input_lower:
            response, success = start_interview()
            return response
        else:
            return """
🗣️ **Interview Preparation Ready!**

I'll create personalized questions based on your selected job using OpenAI. 

**Ready to start?** Type:
- "**start interview**" to begin
- "**generate questions**" to start

The practice will include 5-10 relevant questions covering technical and behavioral aspects.
"""
    
    # Interview questions state
    elif current_state == "interview_questions":
        if user_input_lower in ["skip", "next"]:
            # Skip current question
            if st.session_state.current_question_index + 1 < len(st.session_state.interview_questions):
                # Add empty answer for skipped question
                while len(st.session_state.interview_answers) <= st.session_state.current_question_index:
                    st.session_state.interview_answers.append("")
                st.session_state.interview_answers[st.session_state.current_question_index] = "[Skipped]"
                
                st.session_state.current_question_index += 1
                next_question = st.session_state.interview_questions[st.session_state.current_question_index]
                
                return f"""
⏭️ **Question skipped.**

**Question {st.session_state.current_question_index + 1} of {len(st.session_state.interview_questions)}:**
❓ {next_question}

Please provide your answer.
"""
            else:
                return "You're already on the last question. Type 'finish' to complete the interview."
        
        elif user_input_lower == "finish":
            # Force complete interview
            st.session_state.current_state = "interview_complete"
            return """
🎉 **Interview completed early!**

**What would you like to do next?**
- **"new job search"** - Find more opportunities
- **"learn skills"** - Improve identified weak areas
- **"practice again"** - Do another interview round
"""
        
        else:
            # Submit answer using the API
            response, success = submit_interview_answer(user_input)
            return response
    
    # Interview complete state
    elif current_state == "interview_complete":
        if "new" in user_input_lower and "search" in user_input_lower:
            # Reset for new job search
            st.session_state.current_state = "welcome"
            st.session_state.jobs_list = []
            st.session_state.selected_job = None
            st.session_state.resume_text = None
            st.session_state.analysis_result = None
            st.session_state.interview_started = False
            st.session_state.interview_questions = []
            st.session_state.interview_answers = []
            return bot.get_welcome_message()
        elif "practice again" in user_input_lower:
            # Reset interview for practice again
            st.session_state.current_state = "interview_prep"
            st.session_state.interview_started = False
            st.session_state.interview_questions = []
            st.session_state.interview_answers = []
            st.session_state.current_question_index = 0
            return process_user_input("start interview")
        else:
            return """
🎉 **Interview practice completed!**

**What would you like to do next?**
- **"new job search"** - Search for different positions
- **"analyze resume"** - Review resume analysis again  
- **"learn skills"** - Find more learning resources
- **"practice again"** - Do another interview round

Type your choice to continue!
"""
    
    # Default fallback
    return "I'm not sure how to help with that. Could you please rephrase or choose from the available options?"

def main():
    # Check API connection first
    if not check_api_connection():
        st.error("⚠️ **Cannot connect to the FastAPI server!**")
        st.markdown("""
        **Please ensure:**
        1. Your FastAPI server is running on `localhost:8000`
        2. Run your FastAPI server with: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
        """)
        st.stop()
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 Career Mentor Chat Bot")
    st.caption("Your AI-powered career assistant for job search, resume analysis, and interview preparation")
    
    # Show welcome message if first time
    if len(st.session_state.messages) == 0:
        welcome_msg = st.session_state.bot.get_welcome_message()
        add_message("assistant", welcome_msg)
    
    # Display chat messages
    display_chat_messages()
    
    # File upload section (show only when waiting for resume)
    if st.session_state.waiting_for_resume and st.session_state.current_state == "resume_upload":
        st.markdown("---")
        uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"], key="resume_upload")
        
        if uploaded_file is not None:
            try:
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text.strip():
                    st.session_state.resume_text = resume_text
                    st.session_state.waiting_for_resume = False
                    
                    # Analyze resume automatically
                    with st.spinner("📊 Analyzing your resume..."):
                        data = {
                            "resume": resume_text,
                            "job_description": st.session_state.selected_job
                        }
                        
                        result, error = make_api_request("/analyze-resume", data, timeout=120)
                        
                        if error:
                            response = f"❌ Resume analysis failed: {error}"
                        elif result and result.get("status") == "success":
                            st.session_state.analysis_result = result["response"]
                            st.session_state.current_state = "resume_analysis"
                            response = f"""
✅ **Resume uploaded and analyzed successfully!**

📊 **Analysis Results:**
{result["response"]}

**What would you like to do next?**
🎓 **Learn Skills:** Type "learn [skill name]" 
🗣️ **Interview Prep:** Type "prepare for interview" 
"""
                        else:
                            response = "❌ Resume analysis failed. Please try again."
                    
                    add_message("assistant", response)
                    st.rerun()
                else:
                    st.error("Could not extract text from PDF. Please ensure it's a valid PDF with text content.")
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        add_message("user", prompt)
        
        # Process input and get response
        with st.spinner("Thinking..."):
            response = process_user_input(prompt)
        
        # Add bot response
        add_message("assistant", response)
        
        # Rerun to update display
        st.rerun()
    
    # Sidebar with help
    with st.sidebar:
        st.markdown("### 💡 Quick Help")
        
        current_state = st.session_state.current_state
        if current_state == "welcome":
            st.markdown("""
            **Getting Started:**
            - "Search for Python developer jobs"
            - "Find marketing jobs in pakistan"
            - "Software engineer positions"
            """)
        elif current_state == "job_selection":
            st.markdown("""
            **Select a Job:**
            - "Select job 1"
            - "I want job 3"
            - "Job number 2"
            """)
        elif current_state == "resume_analysis":
            st.markdown("""
            **Next Steps:**
            - "Learn Python programming"
            - "Prepare for interview"  
            - "Find courses for data analysis"
            """)
        elif current_state == "skill_learning":
            st.markdown("""
            **Learning Resources:**
            - "Udemy course for Python"
            - "YouTube videos for React"
            - "Both for machine learning"
            """)
        elif current_state == "interview_questions":
            st.markdown("""
            **Interview Commands:**
            - Type your answer naturally
            - "skip" - Skip current question
            - "finish" - Complete interview early
            """)
        
        st.markdown("---")
        
        if st.button("🔄 Start New Session"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("### 📊 Session Info")
        st.write(f"**Current State:** {st.session_state.current_state}")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        if st.session_state.selected_job:
            st.write("**Job Selected:** ✅")
        if st.session_state.resume_text:
            st.write("**Resume Uploaded:** ✅")
        if st.session_state.interview_started:
            st.write("**Interview Started:** ✅")
            st.write(f"**Questions:** {len(st.session_state.interview_questions)}")
            if st.session_state.current_state == "interview_questions":
                st.write(f"**Progress:** {st.session_state.current_question_index + 1}/{len(st.session_state.interview_questions)}")
        
        # Debug section
        with st.expander("🔧 Debug Info"):
            st.write("**API Endpoints Available:**")
            st.code("""
            - /find-linkedin-jobs
            - /analyze-resume  
            - /find-course
            - /find-youtube
            - /interview (OpenAI-powered)
            """)
            
            st.write("**Interview API Request Format:**")
            st.code("""
            {
                "job_description": "string",
                "current_step": 0,
                "answer": null,
                "answers": [],
                "questions": []
            }
            """)

if __name__ == "__main__":
    main()