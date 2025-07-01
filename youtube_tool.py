from langchain.tools import tool
import requests
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def find_youtube_videos(query: str) -> str:
    """
    Search YouTube for videos matching the query and return title, description, author, and link.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={api_key}"
    response = requests.get(url)
    data = response.json()
    results = []
    if "items" in data:
        for item in data["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"]["description"]
            author = item["snippet"]["channelTitle"]
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            results.append(
                f"Title: {title}\nDescription: {description}\nAuthor: {author}\nLink: {video_url}\n"
            )
        return "\n".join(results)
    else:
        return f"No items found. Error or quota issue: {data}"
