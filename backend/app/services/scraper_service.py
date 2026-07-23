import random
import json
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        # Fallbacks for safety
        self.fallback_restaurants = [
            {
                "name": "Nomad",
                "rating": 4.5,
                "price_level": "$$$",
                "distance": "0.3 km",
                "lat": 31.6271,
                "lng": -7.9875,
                "description": "Modern Moroccan cuisine with a beautiful rooftop overlooking the Medina."
            }
        ]

    def search_restaurants(self, base_location: str, limit: int = 3) -> list:
        """
        Fetches live restaurant data for Marrakech using DuckDuckGo Search (Direct).
        """
        print(f"ScraperService: Fetching live data for {base_location} via DuckDuckGo Direct...")
        
        try:
            query = f"top rated restaurants in {base_location} Marrakech ratings prices"
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=limit)]
            
            if not results:
                return random.sample(self.fallback_restaurants, 1)

            # Map results to our card format
            return [
                {
                    "name": r['title'],
                    "rating": 4.5, # Default since parsing is needed
                    "price_level": "Live Info",
                    "distance": "Medina",
                    "lat": 31.6295,
                    "lng": -7.9811,
                    "description": r['body'][:300] + "...",
                    "image_url": "https://img.freepik.com/free-photo/view-marrakech-morocco_23-2148283307.jpg",
                    "source": "DuckDuckGo Live",
                    "nav_clues": "Check Mahir's summary for specific directions."
                } for r in results
            ]
        except Exception as e:
            print(f"ScraperService: Direct Search failed: {e}")
            return random.sample(self.fallback_restaurants, 1)

    def search_live_prices(self, item: str) -> str:
        """
        Fetch live price information (Direct).
        """
        try:
            query = f"current price of {item} in Marrakech 2025 dirhams MAD"
            with DDGS() as ddgs:
                results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results) if results else "No live pricing found."
        except Exception as e:
            print(f"ScraperService: Price search failed: {e}")
            return "Unable to fetch live prices at the moment."

scraper_service = ScraperService()
