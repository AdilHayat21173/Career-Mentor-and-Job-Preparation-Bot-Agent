# from langchain.tools import tool
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# @tool
# def linkedin_job_search(field: str = "python", geoid: str = "101022442", page: str = "1") -> str:
#     """
#     Search LinkedIn jobs using ScrapingDog API and return job listings with position, company, location, and links.
#     """
#     url = "https://api.scrapingdog.com/linkedinjobs"
#     api_key = os.getenv("SCRAPINGDOG_API_KEY")
#     if not api_key:
#         return "❌ API key not found. Please set SCRAPINGDOG_API_KEY in your .env file."

#     params = {
#         "api_key": api_key,
#         "field": field,
#         "geoid": geoid,
#         "page": page
#     }

#     try:
#         response = requests.get(url, params=params, timeout=30)
#         if response.status_code == 200:
#             data = response.json()
#             if isinstance(data, list) and data:
#                 results = []
#                 for job in data:
#                     job_position = job.get('job_position', 'N/A')
#                     job_link = job.get('job_link', '#')
#                     company_name = job.get('company_name', 'N/A')
#                     company_profile = job.get('company_profile', '#')
#                     job_location = job.get('job_location', 'N/A')
#                     job_posting_date = job.get('job_posting_date', 'N/A')
#                     company_logo_url = job.get('company_logo_url', '#')
#                     results.append(
#                         f"Job Position: {job_position}\n"
#                         f"Company: {company_name}\n"
#                         f"Location: {job_location}\n"
#                         f"Posted On: {job_posting_date}\n"
#                         f"Company Profile: {company_profile}\n"
#                         f"More Details: {job_link}\n"
#                         f"Company Logo: {company_logo_url}\n"
#                         + "-" * 50
#                     )
#                 return "\n".join(results)
#             else:
#                 return "No jobs found or invalid response format."
#         else:
#             return f"Request failed with status code: {response.status_code} | {response.text}"
#     except Exception as e:
#         return f"❌ Error fetching jobs: {str(e)}"

from langchain.tools import tool
import requests
import os
from dotenv import load_dotenv
import time
import random

load_dotenv()

@tool
def linkedin_job_search(field: str = "python", geoid: str = "101022442", page: str = "1") -> str:
    """
    Search LinkedIn jobs using ScrapingDog API and return job listings with position, company, location, and links.
    Enhanced with better error handling and retry logic.
    """
    url = "https://api.scrapingdog.com/linkedinjobs"
    api_key = os.getenv("SCRAPINGDOG_API_KEY")
    
    if not api_key:
        return "❌ API key not found. Please set SCRAPINGDOG_API_KEY in your .env file."
    
    # Enhanced headers to mimic real browser requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    params = {
        "api_key": api_key,
        "field": field,
        "geoid": geoid,
        "page": page
    }
    
    # Retry logic with exponential backoff
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Add random delay to avoid rate limiting
            if attempt > 0:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            # Check if response is HTML (error page)
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type or response.text.strip().startswith('<!DOCTYPE'):
                if attempt < max_retries - 1:
                    print(f"Received HTML response (attempt {attempt + 1}), retrying...")
                    continue
                else:
                    return "❌ API is currently blocked by Cloudflare. Please try again later or contact ScrapingDog support."
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except requests.exceptions.JSONDecodeError:
                    return "❌ Invalid JSON response from API. Please try again."
                
                if isinstance(data, list) and data:
                    results = []
                    for job in data:
                        # Validate job data
                        if not isinstance(job, dict):
                            continue
                            
                        job_position = job.get('job_position', 'N/A')
                        job_link = job.get('job_link', '#')
                        company_name = job.get('company_name', 'N/A')
                        company_profile = job.get('company_profile', '#')
                        job_location = job.get('job_location', 'N/A')
                        job_posting_date = job.get('job_posting_date', 'N/A')
                        job_description = job.get('job_description', 'No description available')
                        
                        # Skip if essential fields are missing
                        if job_position == 'N/A' and company_name == 'N/A':
                            continue
                        
                        job_info = (
                            f"🔹 Job Position: {job_position}\n"
                            f"🏢 Company: {company_name}\n"
                            f"📍 Location: {job_location}\n"
                            f"📅 Posted On: {job_posting_date}\n"
                            f"🔗 Job Link: {job_link}\n"
                            f"🏢 Company Profile: {company_profile}\n"
                            f"📝 Description: {job_description[:200]}{'...' if len(job_description) > 200 else ''}\n"
                            + "=" * 60
                        )
                        results.append(job_info)
                    
                    if results:
                        return f"✅ Found {len(results)} jobs:\n\n" + "\n\n".join(results)
                    else:
                        return "❌ No valid job listings found in the response."
                        
                elif isinstance(data, dict):
                    # Handle different response formats
                    if 'error' in data:
                        return f"❌ API Error: {data['error']}"
                    elif 'jobs' in data:
                        return linkedin_job_search_format_jobs(data['jobs'])
                    else:
                        return f"❌ Unexpected response format: {data}"
                else:
                    return "❌ No jobs found or invalid response format."
                    
            elif response.status_code == 403:
                if attempt < max_retries - 1:
                    print(f"403 Forbidden (attempt {attempt + 1}), retrying...")
                    continue
                else:
                    return "❌ Access forbidden (403). Your IP might be blocked or API key invalid."
                    
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    print(f"Rate limited (attempt {attempt + 1}), retrying...")
                    continue
                else:
                    return "❌ Rate limit exceeded. Please try again later."
                    
            else:
                return f"❌ Request failed with status code: {response.status_code}"
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout (attempt {attempt + 1}), retrying...")
                continue
            else:
                return "❌ Request timeout. Please try again later."
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"Connection error (attempt {attempt + 1}), retrying...")
                continue
            else:
                return "❌ Connection error. Please check your internet connection."
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error (attempt {attempt + 1}): {str(e)}, retrying...")
                continue
            else:
                return f"❌ Unexpected error: {str(e)}"
    
    return "❌ All retry attempts failed. Please try again later."

def linkedin_job_search_format_jobs(jobs_data):
    """Helper function to format job data consistently"""
    if not jobs_data:
        return "❌ No jobs found."
    
    results = []
    for job in jobs_data:
        if isinstance(job, dict):
            job_position = job.get('job_position', job.get('title', 'N/A'))
            company_name = job.get('company_name', job.get('company', 'N/A'))
            job_location = job.get('job_location', job.get('location', 'N/A'))
            job_posting_date = job.get('job_posting_date', job.get('posted_date', 'N/A'))
            job_link = job.get('job_link', job.get('url', '#'))
            
            job_info = (
                f"🔹 Job Position: {job_position}\n"
                f"🏢 Company: {company_name}\n"
                f"📍 Location: {job_location}\n"
                f"📅 Posted On: {job_posting_date}\n"
                f"🔗 Job Link: {job_link}\n"
                + "=" * 60
            )
            results.append(job_info)
    
    return f"✅ Found {len(results)} jobs:\n\n" + "\n\n".join(results)