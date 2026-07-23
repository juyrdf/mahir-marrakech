import requests
from app.core.config import settings
from typing import List, Dict, Any

# Top Marrakech restaurants - Local fallback data (always available)
LOCAL_MARRAKECH_RESTAURANTS = [
    {"place_id": "local_001", "name": "Café Argana", "address": "Place Jemaa El Fna, Marrakech", "rating": 4.3, "reviews": 8240, "summary": "Legendary rooftop terrace overlooking Jemaa El Fna. Famous for sunset views and traditional tagines.", "is_restaurant": True},
    {"place_id": "local_002", "name": "Restaurant Toubkal", "address": "3 Rue de la Recette, Médina, Marrakech", "rating": 4.5, "reviews": 1820, "summary": "Authentic Moroccan cuisine in the heart of the Medina. Known for their rich harira and couscous.", "is_restaurant": True},
    {"place_id": "local_003", "name": "El Gnaouia", "address": "Rue Kennaria, Marrakech Médina", "rating": 4.4, "reviews": 2100, "summary": "Popular local restaurant with live Gnaoua music. Top spot for mechoui and traditional pastilla.", "is_restaurant": True},
    {"place_id": "local_004", "name": "Le Jardin", "address": "32 Souk Sidi Abdelaziz, Marrakech", "rating": 4.5, "reviews": 4560, "summary": "Garden restaurant set in a stunning riad. Mediterranean and Moroccan fusion in a green oasis.", "is_restaurant": True},
    {"place_id": "local_005", "name": "Nomad", "address": "1 Derb Aarjan, Marrakech", "rating": 4.6, "reviews": 7200, "summary": "Modern Moroccan rooftop restaurant near the spice souks. Best views and contemporary twist.", "is_restaurant": True},
    {"place_id": "local_006", "name": "Café de France", "address": "Place Jemaa El Fna, Marrakech", "rating": 4.1, "reviews": 5300, "summary": "Iconic café on the main square. Perfect for people-watching over mint tea and msemen.", "is_restaurant": True},
    {"place_id": "local_007", "name": "Al Baraka", "address": "1 Place de la Kissaria, Marrakech", "rating": 4.4, "reviews": 1950, "summary": "Traditional Dar with intricate zellige decor. Perfect for a formal Moroccan dinner experience.", "is_restaurant": True},
    {"place_id": "local_008", "name": "Henna Café", "address": "93 Arset Aouzal, Marrakech", "rating": 4.7, "reviews": 3100, "summary": "Cozy rooftop vegetarian café. Community-driven, serves traditional Moroccan breakfast and lunch.", "is_restaurant": True},
    {"place_id": "local_009", "name": "Terrasse des Épices", "address": "15 Souk Cherifia, Marrakech", "rating": 4.3, "reviews": 3800, "summary": "Rooftop terrace in the souks serving tagines and salads. Great for a peaceful lunch escape.", "is_restaurant": True},
    {"place_id": "local_010", "name": "Amal Center", "address": "Rue Ibn Sina, Guéliz, Marrakech", "rating": 4.6, "reviews": 2200, "summary": "Non-profit restaurant run by women. Authentically prepared traditional Moroccan lunch buffet.", "is_restaurant": True},
    {"place_id": "local_011", "name": "Panna e Cioccolato", "address": "Rue de la Liberté, Guéliz, Marrakech", "rating": 4.5, "reviews": 1400, "summary": "Best Italian and dessert café in Guéliz. Known for their freshly made gelato and pasta.", "is_restaurant": True},
    {"place_id": "local_012", "name": "Restaurant Dar Zitoun", "address": "Derb Sidi Ahmed Ou Moussa, Marrakech", "rating": 4.6, "reviews": 890, "summary": "Hidden gem riad restaurant. Exclusive 4-course Moroccan tasting menu in a private setting.", "is_restaurant": True},
    {"place_id": "local_013", "name": "Grand Café de la Poste", "address": "Boulevard El Mansour Eddahbi, Guéliz", "rating": 4.2, "reviews": 3400, "summary": "Historic French brasserie from 1925. Colonial charm with excellent brunch and French classics.", "is_restaurant": True},
    {"place_id": "local_014", "name": "Jnane Tamsna Restaurant", "address": "Douar Abiad, Palmeraie, Marrakech", "rating": 4.8, "reviews": 670, "summary": "Luxury Palmeraie garden restaurant. Farm-to-table organic Moroccan cuisine by the pool.", "is_restaurant": True},
    {"place_id": "local_015", "name": "Kosybar", "address": "47 Place des Ferblantiers, Marrakech", "rating": 4.4, "reviews": 2900, "summary": "Chic rooftop bar-restaurant near the Mellah. Moroccan and Asian fusion with stunning stork views.", "is_restaurant": True},
]


class PlacesService:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def search_restaurants(self, query: str = "top restaurants in Marrakech") -> List[Dict[str, Any]]:
        """
        Tries Google Places API first, falls back to local curated dataset.
        """
        # Try live Google API first
        if self.api_key:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.types,places.editorialSummary"
                }
                payload = {
                    "textQuery": query,
                    "locationBias": {
                        "circle": {
                            "center": {"latitude": 31.6295, "longitude": -7.9811},
                            "radius": 5000.0
                        }
                    }
                }
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=8)
                response.raise_for_status()
                data = response.json()

                places = data.get("places", [])
                if places:
                    results = []
                    for p in places:
                        results.append({
                            "place_id": p.get("id"),
                            "name": p.get("displayName", {}).get("text", "Unknown"),
                            "address": p.get("formattedAddress"),
                            "rating": p.get("rating"),
                            "reviews": p.get("userRatingCount"),
                            "price_level": p.get("priceLevel"),
                            "summary": p.get("editorialSummary", {}).get("text", ""),
                            "is_restaurant": "restaurant" in p.get("types", [])
                        })
                    print(f"Places Service: Google API returned {len(results)} results.")
                    return results

                print("Places Service: Google API returned 0 places. Falling back to local data.")
            except Exception as e:
                print(f"Places Service: Google API Error ({e}). Falling back to local data.")

        # Filter local data based on query keywords
        query_lower = query.lower()
        filtered = LOCAL_MARRAKECH_RESTAURANTS

        # Simple keyword filtering for areas
        if "gueliz" in query_lower or "guéliz" in query_lower:
            filtered = [r for r in LOCAL_MARRAKECH_RESTAURANTS if "Guéliz" in (r["address"] or "") or "Guéliz" in (r["address"] or "")]
        elif "medina" in query_lower or "médina" in query_lower:
            filtered = [r for r in LOCAL_MARRAKECH_RESTAURANTS if "Médina" in (r["address"] or "") or "Médina" in (r["address"] or "")]
        elif "palmeraie" in query_lower:
            filtered = [r for r in LOCAL_MARRAKECH_RESTAURANTS if "Palmeraie" in (r["address"] or "")]

        if not filtered:
            filtered = LOCAL_MARRAKECH_RESTAURANTS  # Return all if no match

        print(f"Places Service: Using local data. Returning {len(filtered)} results.")
        return filtered


places_service = PlacesService()
