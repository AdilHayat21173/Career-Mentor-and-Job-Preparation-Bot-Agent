import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import tool

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Define the ATS prompt template directly in the code
ats_prompt_text = """# ATS Evaluation Prompt
You are an ATS (Applicant Tracking System) resume evaluator.

Given a user's resume and a job description:

1. Rate how ATS-friendly the resume is (0 to 100%).
2. List important skills/keywords missing from the resume.
3. Recommend improvements to make it more ATS-optimized.

Respond in this format:
- ATS Score: X%
- Missing Skills: [list the missing skills/keywords]
- Recommendations: [provide specific recommendations]

Resume: {resume}

Job Description: {job_description}"""

prompt = PromptTemplate.from_template(ats_prompt_text)
ats_analysis_chain = prompt | llm

@tool
def ats_analysis(resume: str, job_description: str) -> str:
    """
    Analyze the resume against the job description and return missing content, recommendations, and ATS score.
    """
    try:
        result = ats_analysis_chain.invoke({
            "resume": resume,
            "job_description": job_description
        })
        return result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        return f"Error in ATS analysis: {str(e)}"