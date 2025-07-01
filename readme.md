# Career Mentor & Job Preparation Bot

## Overview

**Career Mentor Bot** is an AI-powered web application that helps users with:
- 🔍 **Job Search** (via LinkedIn through ScrapingDog API)
- 📄 **Resume Analysis** (ATS compatibility, missing/recommended skills)
- 🎓 **Skill Learning** (find Udemy courses & YouTube tutorials)
- 🗣️ **Interview Preparation** (job-specific, AI-generated questions & evaluation)

Built with **Streamlit** (frontend) and **FastAPI** (backend), it leverages OpenAI for resume/interview intelligence and ScrapingDog for job search.

---

## Project Flow

1. **Job Search**
   - User enters a job title/skill and (optionally) location.
   - The app fetches recent LinkedIn jobs using the ScrapingDog API.
   - User selects a job from the list.

2. **Resume Upload & Analysis**
   - User uploads their resume (PDF).
   - The app extracts text and analyzes it against the selected job description using OpenAI.
   - The user receives:
     - ATS compatibility score
     - Missing and recommended skills
     - Suggestions for improvement

3. **Skill Learning**
   - User can search for missing/recommended skills.
   - The app fetches relevant Udemy courses and YouTube tutorials for the skill.

4. **Interview Preparation**
   - User can start interview practice for the selected job.
   - The app generates 5–10 job-specific interview questions using OpenAI.
   - User answers each question step-by-step.
   - After completion, the app provides an AI-powered evaluation and feedback.

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd Career-Mentor-and-Job-Preparation-Bot
```

### 2. Install Dependencies

```sh
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
pip install -r requirements.txt
```


### 4. Start the Backend (FastAPI)

```sh
uvicorn main:app --reload
```

### 5. Start the Frontend (Streamlit)

```sh
streamlit run streamlit_app.py
```

---

## Usage Flow

1. **Start the app** and enter your query (e.g., "Search for Python developer jobs in Pakistan").
2. **Select a job** from the list.
3. **Upload your resume** (PDF).
4. **View resume analysis** (ATS score, missing skills, recommendations).
5. **Search for learning resources** for any missing skill.
6. **Start interview practice** and answer AI-generated questions.
7. **Get your interview evaluation** and download your summary.

---

## API Endpoints

- `/find-linkedin-jobs` — Search LinkedIn jobs (ScrapingDog)
- `/analyze-resume` — Resume & job description analysis (OpenAI)
- `/find-course` — Find Udemy courses for a skill
- `/find-youtube` — Find YouTube tutorials for a skill
- `/interview` — AI-powered interview Q&A and evaluation

---

## Technologies Used

- **Streamlit** — Interactive frontend
- **FastAPI** — Backend API
- **OpenAI** — Resume & interview intelligence
- **ScrapingDog** — LinkedIn job search
- **Udemy API** — Course search
- **YouTube Data API** — Video search
- **python-dotenv** — Environment variable management

---

## License

MIT License

---

## Author
Adil Hayat