#!/usr/bin/env python3
"""
Test script for Udemy API connection
Run this to debug Udemy API issues
"""

import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

def test_udemy_api():
    print("🔍 Testing Udemy API Connection...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    client_id = os.getenv("UDEMY_CLIENT_ID")
    client_secret = os.getenv("UDEMY_CLIENT_SECRET")
    
    print(f"CLIENT_ID found: {'✅' if client_id else '❌'}")
    print(f"CLIENT_SECRET found: {'✅' if client_secret else '❌'}")
    
    if not client_id or not client_secret:
        print("\n❌ Missing API credentials!")
        print("\nTo fix this:")
        print("1. Go to https://www.udemy.com/developers/")
        print("2. Create a developer account")
        print("3. Create an application")
        print("4. Add credentials to your .env file:")
        print("   UDEMY_CLIENT_ID=your_client_id")
        print("   UDEMY_CLIENT_SECRET=your_client_secret")
        return False
    
    # Test API connection
    try:
        print(f"\nTesting API with CLIENT_ID: {client_id[:10]}...")
        
        url = "https://www.udemy.com/api-2.0/courses/?search=python&page_size=1"
        auth = HTTPBasicAuth(client_id, client_secret)
        
        print(f"Making request to: {url}")
        
        response = requests.get(url, auth=auth, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection Successful!")
            print(f"Found {len(data.get('results', []))} courses")
            
            if data.get('results'):
                course = data['results'][0]
                print(f"Sample course: {course.get('title', 'N/A')}")
                return True
            else:
                print("⚠️  No courses returned")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication Failed!")
            print("Check your CLIENT_ID and CLIENT_SECRET")
            print(f"Response: {response.text}")
            return False
            
        elif response.status_code == 403:
            print("❌ Access Forbidden!")
            print("Your API credentials might not have the required permissions")
            print(f"Response: {response.text}")
            return False
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        print("Check your internet connection")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error!")
        print("Check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_search_query(query="python"):
    """Test a specific search query"""
    print(f"\n🔍 Testing search for: '{query}'")
    print("=" * 50)
    
    load_dotenv()
    client_id = os.getenv("UDEMY_CLIENT_ID")
    client_secret = os.getenv("UDEMY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ No API credentials found")
        return
    
    try:
        url = f"https://www.udemy.com/api-2.0/courses/?search={query}&page_size=3&ordering=most-reviewed"
        auth = HTTPBasicAuth(client_id, client_secret)
        
        response = requests.get(url, auth=auth, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            courses = data.get('results', [])
            
            print(f"✅ Found {len(courses)} courses for '{query}'")
            
            for i, course in enumerate(courses, 1):
                print(f"\n{i}. {course.get('title', 'N/A')}")
                print(f"   Price: {course.get('price', 'N/A')}")
                print(f"   Rating: {course.get('avg_rating', 'N/A')}/5")
                print(f"   Students: {course.get('num_subscribers', 'N/A')}")
                print(f"   URL: https://www.udemy.com{course.get('url', '')}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Search error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Udemy API Test Suite")
    print("=" * 50)
    
    # Test basic connection
    success = test_udemy_api()
    
    if success:
        # Test specific searches
        test_queries = ["python", "machine learning", "react", "data science"]
        
        for query in test_queries:
            test_search_query(query)
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")