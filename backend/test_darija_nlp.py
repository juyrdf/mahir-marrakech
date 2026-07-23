import sys
from pathlib import Path

# Prevent UnicodeEncodeError on Windows stdout with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend root to path
sys.path.append(str(Path(__file__).resolve().parent))

from app.services.ai_service import ai_service

def test_darija_normalization():
    print("🧪 Testing Darija Normalization...")
    
    # Test case 1: Darija transport words
    t1 = "بشحال الطاكسي من لاكار ل ليروبور"
    norm_t1 = ai_service._normalize_darija_and_multi_lang(t1)
    print(f"  Input: '{t1}'\n  Normalized: '{norm_t1}'")
    assert "سعر" in norm_t1
    assert "تاكسي" in norm_t1
    assert "قطار" in norm_t1

    # Test case 2: Darija dining words
    t2 = "بغيت ناكل شي طاجين زوين"
    norm_t2 = ai_service._normalize_darija_and_multi_lang(t2)
    print(f"  Input: '{t2}'\n  Normalized: '{norm_t2}'")
    assert "أريد" in norm_t2
    assert "أكل" in norm_t2
    assert "طاجين" in norm_t2

    # Test case 3: French mixtures
    t3 = "فين كاين شي resto قريب"
    norm_t3 = ai_service._normalize_darija_and_multi_lang(t3)
    print(f"  Input: '{t3}'\n  Normalized: '{norm_t3}'")
    assert "restaurant" in norm_t3
    assert "أين" in norm_t3

    print("✅ Normalization tests passed!")

def test_intent_detection():
    print("\n🧪 Testing Intent Detection...")
    
    # Pricing + Transport
    query1 = "بشحال الطاكسي"
    intents1 = ai_service._detect_intents(query1)
    print(f"  Query: '{query1}' -> Intents: {intents1}")
    assert "pricing" in intents1
    assert "transport" in intents1

    # Food + Navigation
    query2 = "فين كاين شي مطعم زوين كيدير طاجين"
    intents2 = ai_service._detect_intents(query2)
    print(f"  Query: '{query2}' -> Intents: {intents2}")
    assert "food" in intents2
    assert "navigation" in intents2

    # Safety
    query3 = "خايف من النصابين والشفارة في السويقة"
    intents3 = ai_service._detect_intents(query3)
    print(f"  Query: '{query3}' -> Intents: {intents3}")
    assert "safety" in intents3

    print("✅ Intent detection tests passed!")

def test_sentiment_detection():
    print("\n🧪 Testing Sentiment Detection...")
    
    # Worried
    s1 = "أنا خايف بزاف من الشفار"
    sentiment1 = ai_service._detect_sentiment(s1)
    print(f"  Query: '{s1}' -> Sentiment: {sentiment1}")
    assert sentiment1 == "worried"

    # Curious (Hakawati Mode)
    s2 = "عاود ليا قصة تاريخ صومعة الكتبية"
    sentiment2 = ai_service._detect_sentiment(s2)
    print(f"  Query: '{s2}' -> Sentiment: {sentiment2}")
    assert sentiment2 == "curious"

    print("✅ Sentiment detection tests passed!")

if __name__ == "__main__":
    print("==================================================")
    print("🚀 Running Mahir Marrakech Darija & NLP Tests")
    print("==================================================")
    try:
        test_darija_normalization()
        test_intent_detection()
        test_sentiment_detection()
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 100% SUCCESS 🎉")
    except AssertionError as e:
        print(f"\n❌ Assertion Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)
