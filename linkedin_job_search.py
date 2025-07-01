from langchain.tools import tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def linkedin_job_search(field: str = "python", geoid: str = "101022442", page: str = "1") -> str:
    """
    Search LinkedIn jobs using ScrapingDog API and return job listings with position, company, location, and links.
    """
    url = "https://api.scrapingdog.com/linkedinjobs"
    api_key = os.getenv("SCRAPINGDOG_API_KEY")
    if not api_key:
        return "❌ API key not found. Please set SCRAPINGDOG_API_KEY in your .env file."

    params = {
        "api_key": api_key,
        "field": field,
        "geoid": geoid,
        "page": page
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                results = []
                for job in data:
                    job_position = job.get('job_position', 'N/A')
                    job_link = job.get('job_link', '#')
                    company_name = job.get('company_name', 'N/A')
                    company_profile = job.get('company_profile', '#')
                    job_location = job.get('job_location', 'N/A')
                    job_posting_date = job.get('job_posting_date', 'N/A')
                    company_logo_url = job.get('company_logo_url', '#')
                    results.append(
                        f"Job Position: {job_position}\n"
                        f"Company: {company_name}\n"
                        f"Location: {job_location}\n"
                        f"Posted On: {job_posting_date}\n"
                        f"Company Profile: {company_profile}\n"
                        f"More Details: {job_link}\n"
                        f"Company Logo: {company_logo_url}\n"
                        + "-" * 50
                    )
                return "\n".join(results)
            else:
                return "No jobs found or invalid response format."
        else:
            return f"Request failed with status code: {response.status_code} | {response.text}"
    except Exception as e:
        return f"❌ Error fetching jobs: {str(e)}"