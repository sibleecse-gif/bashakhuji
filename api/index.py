from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
from bs4 import BeautifulSoup
import time

app = FastAPI()

# CORS Error এড়ানোর জন্য
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrape_real_data(area: str):
    """
    এটি একটি ডেমো স্ক্র্যাপিং ফাংশন। 
    বাস্তবে এখানে Bikroy বা অন্য কোনো সাইটের URL এবং সঠিক HTML ট্যাগ ব্যবহার করতে হবে।
    """
    scraped_listings = []
    
    # ডেমো হিসেবে আমরা একটি ফেক স্ট্রাকচার বানাচ্ছি। 
    # রিয়েল স্ক্র্যাপিংয়ের জন্য নিচের কমেন্ট করা লাইনের মতো কোড লিখতে হবে:
    # url = f"https://example-real-estate-site.com/search?location={area}"
    # response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # for item in soup.find_all('div', class_='listing-card'): ...
    
    # যেহেতু রিয়েল সাইটগুলো বট ব্লক করে, তাই টেস্টিংয়ের জন্য আমরা কিছু জেনারেটেড ডেটা পাঠাচ্ছি
    scraped_listings = [
        {
            "id": int(time.time()),
            "title": f"Live Scraped: 2 BHK Flat in {area.capitalize() if area else 'Dhaka'}",
            "description": "This data was fetched dynamically by the Python backend.",
            "type": "Family",
            "rooms": 2,
            "budget": 25000,
            "area": area.capitalize() if area else "Dhaka",
            "areaBengali": "ঢাকা"
        },
        {
            "id": int(time.time()) + 1,
            "title": f"Live Scraped: Bachelor Room in {area.capitalize() if area else 'Dhaka'}",
            "description": "Scraped from web sources.",
            "type": "Bachelor",
            "rooms": 1,
            "budget": 8000,
            "area": area.capitalize() if area else "Dhaka",
            "areaBengali": "ঢাকা"
        }
    ]
    return scraped_listings

@app.get("/api/search")
async def search_listings(
    type: Optional[str] = Query(None),
    rooms: Optional[int] = Query(None),
    area: Optional[str] = Query(None),
    minBudget: Optional[int] = Query(None),
    maxBudget: Optional[int] = Query(None)
):
    # 1. ইন্টারনেট থেকে ডেটা স্ক্র্যাপ করা (বা ডেটাবেস থেকে আনা)
    raw_data = scrape_real_data(area)
    
    # 2. ইউজার এর দেওয়া ফিল্টার অনুযায়ী ডেটা ফিল্টার করা
    filtered_data = []
    for item in raw_data:
        matched = True
        
        if type and type.lower() != item.get("type", "").lower():
            matched = False
        if rooms and int(rooms) != item.get("rooms"):
            matched = False
        if minBudget and item.get("budget", 0) < int(minBudget):
            matched = False
        if maxBudget and item.get("budget", 0) > int(maxBudget):
            matched = False
            
        if matched:
            filtered_data.append(item)
            
    return filtered_data