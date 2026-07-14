from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
import os

app = FastAPI()

# CORS পলিসি এলাও করা
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
async def search_listings(
    type: Optional[str] = Query(None),
    rooms: Optional[int] = Query(None),
    area: Optional[str] = Query("Dhaka"),
    minBudget: Optional[int] = Query(None),
    maxBudget: Optional[int] = Query(None)
):
    # Vercel Environment Variables থেকে গুগলের কী জোড়া নেওয়া
    api_key = os.environ.get("GOOGLE_API_KEY")
    cx_id = os.environ.get("GOOGLE_CX_ID")

    # যদি API Key সেট করা না থাকে, তবে একটি ডেমো কার্ড দেখাবে যাতে সাইট ক্র্যাশ না করে
    if not api_key or not cx_id:
        return [
            {
                "id": "demo",
                "title": f"To Let: Flat/Mess in {area.capitalize()}",
                "description": "লাইভ ফেসবুক পোস্ট দেখতে আপনার Vercel ড্যাশবোর্ডে GOOGLE_API_KEY এবং GOOGLE_CX_ID সেট করুন।",
                "type": type or "Family/Bachelor",
                "rooms": rooms or 2,
                "budget": 12000,
                "area": area.capitalize(),
                "areaBengali": "ঢাকা",
                "url": "https://www.facebook.com"
            }
        ]

    # গুগলের সাহায্যে ফেসবুকে সার্চ করার জন্য কুয়েরি (Google Dorking)
    search_query = f'site:facebook.com "to let" {area}'
    if type:
        search_query += f' "{type}"'
    if rooms:
        search_query += f' "{rooms} room" OR "{rooms} bed"'

    google_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx_id}&q={search_query}"

    try:
        response = requests.get(google_url, timeout=6)
        search_results = response.json()
        items = search_results.get('items', [])
        
        real_listings = []
        for index, item in enumerate(items):
            snippet = item.get('snippet', '')
            
            # ফেসবুকের বিবরণ থেকে বাজেট (টাকা) অনুমান করার চেষ্টা
            budget_guess = 15000  # ব্যাকআপ বাজেট
            words = snippet.replace(',', '').split()
            for word in words:
                if word.isdigit() and 3000 <= int(word) <= 80000:
                    budget_guess = int(word)
                    break
            
            # ফ্রন্টএন্ডের বাজেট ফিল্টার চেক করা
            if minBudget and budget_guess < int(minBudget):
                continue
            if maxBudget and budget_guess > int(maxBudget):
                continue

            real_listings.append({
                "id": f"fb_{index}",
                "title": item.get('title', 'Facebook Post').replace(" | Facebook", ""),
                "description": snippet,
                "type": type or "Flat/Room",
                "rooms": rooms or "N/A",
                "budget": budget_guess,
                "area": area.capitalize(),
                "areaBengali": "ঢাকা",
                "url": item.get('link', 'https://www.facebook.com') # আসল ফেসবুক পোস্টের লিংক
            })
            
        return real_listings

    except Exception as e:
        return [{"error": str(e)}]
