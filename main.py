import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain import hub
from ats_tool import ats_analysis
from udemy_tool import find_udemy_course
from youtube_tool import find_youtube_videos
from linkedin_job_search import linkedin_job_search
from interview_tool import InterviewTool  # Updated interview tool with OpenAI
from typing import List, Optional
import traceback

# Load environment variables
load_dotenv()

# Verify OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required")

app = FastAPI()

# Initialize the updated interview tool
interview_tool = InterviewTool()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define tools
tools = [
    ats_analysis,
    find_udemy_course,
    find_youtube_videos,
    linkedin_job_search,
    interview_tool
]

# Pull the OpenAI Functions prompt from LangChain Hub
try:
    prompt = hub.pull("hwchase17/openai-functions-agent")
except:
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can analyze resumes, find relevant courses, and conduct interviews."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

# Create agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    memory=memory, 
    verbose=True,
    handle_parsing_errors=True
)

# --- Request Models ---
class ResumeRequest(BaseModel):
    resume: str
    job_description: str

class CourseRequest(BaseModel):
    skill: str

class YouTubeRequest(BaseModel):
    query: str

class LinkedInJobRequest(BaseModel):
    field: str = "python"
    geoid: str = "101022442"
    page: str = "1"

class InterviewRequest(BaseModel):
    job_description: str
    current_step: int = 0  # 0 = start interview
    answer: Optional[str] = None  # None for first request
    questions: List[str] = []
    answers: List[str] = []

# --- API Endpoints ---
@app.get("/")
async def root():
    return {
        "message": "ATS Resume Analyzer API with OpenAI-powered Interview Bot is running",
        "features": [
            "Resume analysis with ATS scoring",
            "Course recommendations (Udemy)",
            "YouTube video search",
            "LinkedIn job search",
            "AI-powered interviews with OpenAI GPT-4"
        ]
    }

@app.post("/analyze-resume")
async def analyze_resume(data: ResumeRequest):
    try:
        input_text = f"""
        Please analyze this resume against the job description and provide:
        1. ATS compatibility score (0-100%)
        2. Missing skills and keywords
        3. Specific recommendations for improvement
        
        Resume: {data.resume}
        Job Description: {data.job_description}
        """
        result = agent_executor.invoke({"input": input_text})
        return {
            "response": result.get("output", "No response generated"),
            "status": "success"
        }
    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # Return the error message for debugging
        return {
            "response": f"Internal server error: {str(e)}",
            "status": "error"
        }

@app.post("/find-course")
async def find_course(data: CourseRequest):
    """Find Udemy course for specific skill"""
    try:
        input_text = f"Find me a Udemy course for learning: {data.skill}"
        result = agent_executor.invoke({"input": input_text})
        
        return {
            "response": result.get("output", "No course found"),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in find_course: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/find-youtube")
async def find_youtube(data: YouTubeRequest):
    """Find YouTube videos for learning"""
    try:
        input_text = f"Find YouTube videos about: {data.query}"
        result = agent_executor.invoke({"input": input_text})
        return {
            "response": result.get("output", "No videos found"),
            "status": "success"
        }
    except Exception as e:
        print(f"Error in find_youtube: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/find-linkedin-jobs")
async def find_linkedin_jobs(data: LinkedInJobRequest):
    """Find LinkedIn jobs"""
    try:
        # Call the tool directly, not through OpenAI
        result = linkedin_job_search.func(field=data.field, geoid=data.geoid, page=data.page)
        return {
            "response": result,
            "status": "success"
        }
    except Exception as e:
        print(f"Error in find_linkedin_jobs: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/interview")
async def interview_endpoint(request: InterviewRequest):
    """
    OpenAI-powered interview endpoint that handles the entire interview flow:
    1. Start interview (current_step=0, no answer) - Generates questions using OpenAI
    2. Submit answers (current_step>0, with answer) - Processes responses
    3. Get evaluation when complete - Uses OpenAI for evaluation
    """
    try:
        print(f"Interview request: step={request.current_step}, has_answer={request.answer is not None}")
        
        # If it's the start of interview (current_step=0 and no answer)
        if request.current_step == 0 and request.answer is None:
            print("Starting new interview with OpenAI question generation...")
            result = interview_tool._run(
                job_description=request.job_description,
                current_step=0,
                answers=[],
                questions=[]
            )
        else:
            # Add the new answer to existing answers if provided
            updated_answers = request.answers.copy()
            if request.answer:
                updated_answers.append(request.answer)
                print(f"Added answer: {request.answer[:50]}...")
            
            result = interview_tool._run(
                job_description=request.job_description,
                current_step=request.current_step,
                answers=updated_answers,
                questions=request.questions
            )
        
        print(f"Interview result: {result.get('action', 'unknown_action')}")
        
        return {
            "status": "success",
            "data": result,
            "powered_by": "OpenAI GPT-4"
        }
        
    except Exception as e:
        print(f"Error in interview_endpoint: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint with OpenAI status"""
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    
    return {
        "status": "healthy",
        "service": "ATS Resume Analyzer with OpenAI Interview Bot",
        "openai_api_key": openai_status,
        "available_endpoints": {
            "resume_analysis": "/analyze-resume",
            "course_finder": "/find-course", 
            "youtube_search": "/find-youtube",
            "job_search": "/find-linkedin-jobs",
            "interview": "/interview",
            "interview_test": "/interview/test"
        },
        "features": {
            "ai_powered_questions": "Uses OpenAI GPT-4 to generate job-specific interview questions",
            "intelligent_evaluation": "AI-powered candidate evaluation based on responses",
            "dynamic_content": "Questions and evaluations tailored to specific job descriptions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting ATS Resume Analyzer with OpenAI-powered Interview Bot...")
    print(f"OpenAI API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)