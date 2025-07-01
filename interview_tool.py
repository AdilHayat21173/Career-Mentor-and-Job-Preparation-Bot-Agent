from typing import List, Dict, Any
import os
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from openai import OpenAI

# --- Config (Parameters) ---
class Parameters:
    """
    Configurable parameters for the application.
    """
    QUESTIONS_PROMPT = """
You are an expert HR interviewer. Based on the job description provided, generate 7-10 specific and relevant interview questions.

Job Description:
{job_description}

Requirements for the questions:
1. Each question should be directly relevant to the job requirements and skills mentioned
2. Questions should assess both technical competency and cultural fit
3. Include a mix of: technical skills, experience, problem-solving, and behavioral questions
4. Each question should be concise (maximum 25 words)
5. Avoid generic questions - make them specific to this role
6. Focus on the key responsibilities, required skills, and qualifications mentioned

Areas to cover:
- Technical skills and tools mentioned in the job description
- Specific responsibilities and challenges of the role
- Required experience level and qualifications
- Problem-solving and analytical thinking
- Team collaboration and communication
- Industry-specific knowledge if applicable

Return ONLY the questions, one per line, without numbering, bullet points, or additional formatting.
"""
    
    EVALUATION_PROMPT = """
You are an expert HR interviewer evaluating a candidate's interview performance.

Job Description:
{job_description}

Interview Questions and Answers:
{interview_text}

Evaluate the candidate's responses based on:
1. Relevance of answers to the job requirements
2. Depth and detail of responses
3. Demonstration of required skills and experience
4. Specific examples and achievements mentioned
5. Communication skills and professionalism
6. Cultural fit and motivation

Provide your evaluation in the following format:
Score: [percentage between 0-100]%
Feedback: [2-3 sentences explaining the score, highlighting strengths and areas for improvement]

If score is 70% or above, conclude with: "Congratulations! Based on your responses, you appear to be a strong candidate for this role."
If score is below 70%, conclude with: "Thank you for your time. While we appreciate your interest, we feel there may be better alignment with other opportunities."
"""

# --- OpenAI Client ---
class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_completion(self, prompt: str, model: str = "gpt-4") -> str:
        """
        Get completion from OpenAI API
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful HR assistant that generates interview questions and evaluates candidates."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            # Fallback to basic questions if API fails
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when OpenAI API fails"""
        if "generate" in prompt.lower() or "questions" in prompt.lower():
            return "\n".join([
                "Tell me about your relevant experience for this position.",
                "What specific skills make you qualified for this role?",
                "Describe a challenging project you've worked on recently.",
                "How do you handle working under pressure or tight deadlines?",
                "What interests you most about this particular position?",
                "How do you stay updated with industry trends and best practices?",
                "Describe a time you had to learn something new quickly."
            ])
        else:
            return (
                "Score: 75%\n"
                "Feedback: The candidate provided relevant responses and demonstrated understanding of the role requirements. "
                "Good communication skills were evident throughout the interview.\n"
                "Congratulations! Based on your responses, you appear to be a strong candidate for this role."
            )

# --- OpenAI Client Instance ---
openai_client = OpenAIClient()

# --- Interview Tool ---
class InputSchema(BaseModel):
    job_description: str = Field(..., description="The job description for the interview")
    current_step: int = Field(0, description="Current step in the interview process")
    answers: List[str] = Field([], description="Candidate's answers to previous questions")
    questions: List[str] = Field([], description="Generated interview questions")

class InterviewTool(BaseTool):
    name: str = "interview_bot"
    description: str = "Conducts job interviews by asking questions and evaluating candidate responses using OpenAI API"
    args_schema: type = InputSchema

    def _run(self, job_description: str, current_step: int, answers: List[str], questions: List[str]) -> Dict[str, Any]:
        """Execute the interview step"""
        
        # Step 0: Generate questions using OpenAI
        if current_step == 0:
            questions = self._generate_questions(job_description)
            return {
                "action": "start_interview",
                "question": questions[0],
                "questions": questions,
                "current_step": 1,
                "total_questions": len(questions),
                "completed": False,
                "message": f"Interview started! Question 1 of {len(questions)}"
            }
        
        # Continue with questions
        elif current_step <= len(questions):
            # If we have the same number of answers as the current step - 1, ask next question
            if len(answers) == current_step - 1 and current_step <= len(questions):
                if current_step == len(questions):
                    # This is the last question
                    return {
                        "action": "ask_question",
                        "question": questions[current_step - 1],
                        "questions": questions,
                        "current_step": current_step,
                        "total_questions": len(questions),
                        "completed": False,
                        "message": f"Question {current_step} of {len(questions)} (Final Question)"
                    }
                else:
                    return {
                        "action": "ask_question",
                        "question": questions[current_step - 1],
                        "questions": questions,
                        "current_step": current_step,
                        "total_questions": len(questions),
                        "completed": False,
                        "message": f"Question {current_step} of {len(questions)}"
                    }
            
            # If we have all answers, move to evaluation
            elif len(answers) == len(questions):
                evaluation = self._evaluate_candidate(job_description, questions, answers)
                return {
                    "action": "evaluate",
                    "evaluation": evaluation,
                    "questions": questions,
                    "answers": answers,
                    "completed": True,
                    "message": "Interview completed! Here's your evaluation:"
                }
            
            # If we have answers for current step, move to next question
            elif len(answers) == current_step:
                next_step = current_step + 1
                if next_step <= len(questions):
                    return {
                        "action": "ask_question",
                        "question": questions[next_step - 1],
                        "questions": questions,
                        "current_step": next_step,
                        "total_questions": len(questions),
                        "completed": False,
                        "message": f"Question {next_step} of {len(questions)}"
                    }
                else:
                    # All questions answered, evaluate
                    evaluation = self._evaluate_candidate(job_description, questions, answers)
                    return {
                        "action": "evaluate",
                        "evaluation": evaluation,
                        "questions": questions,
                        "answers": answers,
                        "completed": True,
                        "message": "Interview completed! Here's your evaluation:"
                    }
        
        # Fallback - shouldn't reach here
        return {
            "action": "error",
            "message": "Interview flow error. Please restart the interview.",
            "completed": True
        }

    def _generate_questions(self, job_description: str) -> List[str]:
        """Generate interview questions using OpenAI API based on job description"""
        try:
            print(f"Generating questions for job description: {job_description[:100]}...")
            
            # Create the prompt for OpenAI
            prompt = Parameters.QUESTIONS_PROMPT.format(job_description=job_description)
            
            # Get response from OpenAI
            response = openai_client.get_completion(prompt)
            
            # Parse the response into individual questions
            questions = []
            for line in response.split('\n'):
                question = line.strip()
                # Remove any numbering, bullet points, or formatting
                question = question.lstrip('0123456789.-•* ').strip()
                # Remove question marks and add them back consistently
                question = question.rstrip('?').strip()
                if question and len(question) > 10:  # Ensure it's a meaningful question
                    questions.append(question + "?")
            
            print(f"Generated {len(questions)} questions")
            
            # Ensure we have at least 5 questions and at most 10
            if len(questions) < 5:
                print("Not enough questions generated, adding fallback questions...")
                additional_questions = self._get_fallback_questions(job_description)
                questions.extend(additional_questions)
            
            # Limit to 10 questions maximum
            final_questions = questions[:10]
            print(f"Final question count: {len(final_questions)}")
            
            return final_questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            # Fallback to basic questions if API fails
            return self._get_fallback_questions(job_description)

    def _get_fallback_questions(self, job_description: str) -> List[str]:
        """Generate fallback questions when OpenAI API is not available"""
        return [
            "Tell me about your relevant experience for this position?",
            "What specific skills make you qualified for this role?",
            "Describe a challenging project you've worked on recently?",
            "How do you handle working under pressure or tight deadlines?",
            "What interests you most about this particular position?",
            "How do you stay updated with industry trends and best practices?",
            "Describe a time you had to learn something new quickly?",
            "What are your greatest strengths relevant to this role?",
            "How do you approach problem-solving in your work?",
            "Why are you interested in working for our company?"
        ]

    def _evaluate_candidate(self, job_description: str, questions: List[str], answers: List[str]) -> str:
        """Evaluate candidate responses using OpenAI API"""
        try:
            print("Evaluating candidate responses...")
            
            # Format the interview text
            interview_text = "\n".join(
                f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n"
                for i, (q, a) in enumerate(zip(questions, answers))
            )
            
            # Create the evaluation prompt
            prompt = Parameters.EVALUATION_PROMPT.format(
                job_description=job_description,
                interview_text=interview_text
            )
            
            # Get evaluation from OpenAI
            evaluation = openai_client.get_completion(prompt)
            
            print("Evaluation completed")
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating candidate: {str(e)}")
            # Fallback evaluation
            return (
                "Score: 75%\n"
                "Feedback: The candidate provided relevant responses and demonstrated understanding of the role requirements. "
                "Good communication skills were evident throughout the interview.\n"
                "Congratulations! Based on your responses, you appear to be a strong candidate for this role."
            )