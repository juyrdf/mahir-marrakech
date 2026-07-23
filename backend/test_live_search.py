import os
import sys

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the current directory so we can import 'app' directly
sys.path.append(current_dir)

try:
    from app.services.scraper_service import scraper_service
    from app.services.ai_service import AIService
except ImportError:
    # If starting from root, add current_dir to path and try again
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    from app.services.scraper_service import scraper_service
    from app.services.ai_service import AIService

def test_scraper():
    print("Testing Scraper Live Search...")
    # Test restaurant search
    results = scraper_service.search_restaurants("Medina Marrakech")
    print(f"Restaurant Search Results: {results}")
    
    # Test price search
    price_info = scraper_service.search_live_prices("taxi from airport to Jemaa El Fna")
    print(f"\nPrice Search Results (Snippet):\n{price_info[:300]}...")

if __name__ == "__main__":
    try:
        test_scraper()
        print("\n--- PASSED ---")
    except Exception as e:
        print(f"\n--- FAILED: {e} ---")
        import traceback
        traceback.print_exc()
