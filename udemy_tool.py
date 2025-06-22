from langchain.tools import tool
from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth

# Load API credentials
load_dotenv()
CLIENT_ID = os.getenv("UDEMY_CLIENT_ID")
CLIENT_SECRET = os.getenv("UDEMY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("Warning: Udemy CLIENT_ID or CLIENT_SECRET not set in .env")

# --- Udemy API Classes ---

class Udemy:
    __BASE_URL = "https://www.udemy.com/api-2.0/"
    
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.__client_id = client_id
        self.__client_secret = client_secret
    
    @property
    def url(self) -> str:
        return self.__BASE_URL
    
    def _get_full_url(self, resource: str, **kwargs) -> str:
        url = f"{self.url}{resource}/?"
        for param, value in kwargs.items():
            url += f"{param}={value}&"
        return url.rstrip('&')
    
    @property
    def _authentication(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.__client_id, self.__client_secret)

class UdemyAffiliate(Udemy):
    def courses(self, **kwargs) -> dict:
        try:
            response = requests.get(
                self._get_full_url("courses", **kwargs), 
                auth=self._authentication,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "results": []}
    
    def course_detail(self, id: int) -> dict:
        try:
            response = requests.get(
                self._get_full_url(f"courses/{id}"), 
                auth=self._authentication,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def public_curriculum(self, id: int, **kwargs) -> dict:
        try:
            response = requests.get(
                self._get_full_url(f"courses/{id}/public-curriculum-items", **kwargs), 
                auth=self._authentication,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "results": []}
    
    def course_reviews(self, id: int, **kwargs) -> dict:
        try:
            response = requests.get(
                self._get_full_url(f"courses/{id}/reviews", **kwargs), 
                auth=self._authentication,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "results": []}

# --- LangChain Tool Definition ---

@tool
def find_udemy_course(query: str) -> str:
    """
    Search Udemy for the top course related to the given skill. Returns title, link, curriculum, and reviews.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        return "❌ Udemy API credentials not configured. Please set UDEMY_CLIENT_ID and UDEMY_CLIENT_SECRET in your .env file."
    
    try:
        udemy = UdemyAffiliate(CLIENT_ID, CLIENT_SECRET)
        courses = udemy.courses(search=query, page_size=1)
        
        if "error" in courses:
            return f"❌ Error searching courses: {courses['error']}"
        
        if not courses.get("results"):
            return f"No courses found for '{query}'."
        
        course = courses["results"][0]
        course_id = course["id"]
        course_title = course["title"]
        course_url = f"https://www.udemy.com{course['url']}"
        course_price = course.get("price", "N/A")
        
        response = f"📘 **Course:** {course_title}\n💲 **Price:** {course_price}\n🔗 **Link:** {course_url}\n"
        
        # Get curriculum
        curriculum = udemy.public_curriculum(course_id, page_size=5)
        if curriculum.get("results") and not curriculum.get("error"):
            response += "\n📚 **Curriculum:**\n"
            for item in curriculum["results"][:5]:
                response += f"  • {item.get('title', 'N/A')}\n"
        
        # Get reviews
        reviews = udemy.course_reviews(course_id, page_size=3)
        if reviews.get("results") and not reviews.get("error"):
            response += "\n🗣 **Top Reviews:**\n"
            for review in reviews["results"][:3]:
                rating = review.get('rating', 'N/A')
                content = review.get('content', '')[:100]
                response += f"  • ⭐ {rating}/5: {content}...\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error fetching course: {str(e)}"