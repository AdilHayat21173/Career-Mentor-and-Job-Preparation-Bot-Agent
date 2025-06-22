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
import traceback

load_dotenv()

app = FastAPI()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define tools
tools = [ats_analysis, find_udemy_course]

# Pull the OpenAI Functions prompt from LangChain Hub
try:
    prompt = hub.pull("hwchase17/openai-functions-agent")
except:
    # Fallback prompt if hub pull fails
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can analyze resumes and find relevant courses."),
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

class ResumeRequest(BaseModel):
    resume: str
    job_description: str

class CourseRequest(BaseModel):
    skill: str

@app.get("/")
async def root():
    return {"message": "ATS Resume Analyzer API is running"}

@app.post("/analyze-resume")
async def analyze_resume(data: ResumeRequest):
    try:
        # Create a focused input for ATS analysis
        input_text = f"""
        Please analyze this resume against the job description and provide:
        1. ATS compatibility score (0-100%)
        2. Missing skills and keywords
        3. Specific recommendations for improvement
        
        Resume: {data.resume}
        
        Job Description: {data.job_description}
        
        After the analysis, ask if the user would like course recommendations for any missing skills.
        """
        
        result = agent_executor.invoke({"input": input_text})
        
        return {
            "response": result.get("output", "No response generated"),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/find-course")
async def find_course(data: CourseRequest):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)