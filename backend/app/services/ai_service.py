import random
from sqlalchemy.orm import Session
from app.models import ReferencePrice, Place
from langchain_openai import ChatOpenAI
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
import json
import os
import httpx  # For calling n8n
from pathlib import Path

class AIService:
    def __init__(self):
        # Simulated Knowledge Base (Places)
        self.knowledge_base = {
            "jemaa_el_fnaa": {
                "description": "The beating heart of Marrakech. A theater under the stars where history, food, and magic collide.",
                "safety_note": "WARNING: Keep your phone in your front pocket. Avoid 'gift' henna; agree on a price first (approx 50-100 MAD)."
            },
            "koutoubia": {
                "description": "The spiritual lighthouse of the city. Its minaret has guided travelers for 800 years.",
                "safety_note": "The gardens are free and safe. Beware of 'closed today' scams near the entrance."
            },
            "bahia_palace": {
                "description": "A masterpiece of woodcarving and tiles. Built to be the greatest palace of its time.",
                "safety_note": "Official tickets are at the gate. Don't believe anyone outside saying tickets are sold elsewhere."
            },
            "majorelle_garden": {
                "description": "An electric blue oasis. The legacy of Yves Saint Laurent and the soul of Berber art.",
                "safety_note": "Online booking is MANDATORY. Do not go there without a QR code."
            },
            "ben_youssef": {
                "description": "A sanctuary of knowledge. Where thousands of students once memorized the secrets of the universe.",
                "safety_note": "The narrow streets leading here are beautiful but confusing. Follow the signs, not self-appointed guides."
            }
        }

        # Spatial Navigation & Landmark Connectivity Graph (Medina Confusing Alleys Logic)
        self.medina_alley_routes = {
            ("jemaa_el_fnaa", "bahia_palace"): {
                "route": "عبر رياض الزيتون الجديد والملاح",
                "clue": "من الساحة، دخل مع رياض الزيتون الجديد وتبع نيشان. ملي توصل للسبع لويات دخل مع زقاق الملاح. رد بالك من الدراري لي تيجريو بالموتورات في الدرب، وزيد حتى يبان ليك باب القصر.",
                "warning": "درع الحماية: كاينين مرشدين عشوائيين واقفين جيهت درب ضباشة غادي يقولو ليك القصر ساد اليوم باش يديوك لبلاصة خرى. ما تيق بحد، كمل طريقك!"
            },
            ("jemaa_el_fnaa", "ben_youssef"): {
                "route": "عبر سوق السمارين والرحبة القديمة",
                "clue": "دخل مع سوق السمارين، كمل حتى لرحبة القمح ومن بعد دور على اليمن لجهة سوق الجلد. مدرسة بن يوسف كاينة في درب الصاغة.",
                "warning": "تنبيه: أزقة درب ضباشة فيها بزاف د التفرعات المربكة. ديما تبع البلاكات الرسمية المعلقة في الحيط ولا سول مول حانوت جالس."
            },
            ("jemaa_el_fnaa", "koutoubia"): {
                "route": "عبر ممر عرصة البيلك",
                "clue": "طريق نيشان وساهل. غير خرج من الساحة جيهت ساحة الحنطة وعبر الشارع الرئيسي لعرصة البيلك. المنارة تتبان واضحة من الساحة.",
                "warning": "نصيحة: الحدائق زوينة وآمنة للراحة، ولكن حضي مع أصحاب الكوتشيات (العربات) فاش تبغي تعبر الشارع."
            },
            ("jemaa_el_fnaa", "majorelle_garden"): {
                "route": "عبر حافلة ALSA رقم 1 أو 19",
                "clue": "خرج من الساحة لجيهت عرصة البيلك، خود طوبيس رقم 1 بـ 4 دراهم ولا طاكسي صغير بـ 15-20 درهم حتى لشارع يعقوب المنصور.",
                "warning": "هام جداً: حديقة ماجوريل ما يمكنش تدخل ليها بلا حجز مسبق من الأنترنت بالـ QR code. البوليس تما ما تيخلي حد يدوز بلا بيه."
            }
        }

        
        # Initialize AI Provider
        self.llm = None
        
        # 1. Try Google Gemini (Primary)
        if settings.GOOGLE_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    api_key=settings.GOOGLE_API_KEY,
                    temperature=0.7
                )
                print("AI Service: Connected to Google Gemini AI")
            except Exception as e:
                print(f"AI Service: Failed to connect to Gemini: {e}")

        # 2. Try DeepSeek (Secondary Fallback)
        if not self.llm and settings.DEEPSEEK_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model="deepseek-chat",
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com",
                    temperature=0.7
                )
                print("AI Service: Connected to DeepSeek AI")
            except Exception as e:
                print(f"AI Service: Failed to connect to DeepSeek: {e}")
        
        # Load external recommendations
        self.recommendations = {}
        try:
            res_path = Path(__file__).parent.parent / "resources" / "external_recommendations.json"
            if res_path.exists():
                with open(res_path, 'r', encoding='utf-8') as f:
                    self.recommendations = json.load(f)
        except Exception as e:
            print(f"AI Service: Error loading recommendations: {e}")

        # n8n Configuration
        self.n8n_webhook_url = os.getenv("N8N_AI_AGENT_URL")
        print(f"AI Service: n8n integration {'enabled' if self.n8n_webhook_url else 'disabled (N8N_AI_AGENT_URL not set)'}")

    def _normalize(self, text: str) -> str:
        if not text: return ""
        text = text.lower()
        for char in ["أ", "إ", "آ"]:
            text = text.replace(char, "ا")
        text = text.replace("ة", "ه")
        text = text.replace("ى", "ي")
        text = text.replace("ال", "")
        return text

    def _normalize_darija_and_multi_lang(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        
        # Dictionary of Moroccan Darija to Standard Arabic/English
        darija_map = {
            # Transport
            "طوبيس": "حافلة",
            "طوبيسات": "حافلات",
            "طاكسي": "تاكسي",
            "طاكسيات": "تاكسي",
            "لاكار": "قطار",
            "تران": "قطار",
            "ترانات": "قطارات",
            "كيلميتراج": "كيلومترات",
            "كرويلة": "عربة",
            "فرشي": "دراجة نارية",
            "موتور": "دراجة نارية",
            "كار": "حافلة كبيرة",
            
            # Pricing / Transactions
            "بشحال": "سعر",
            "شحال": "سعر",
            "بكم": "سعر",
            "كيدير": "يكلف",
            "داير": "يكلف",
            "ثمن": "سعر",
            "أثمنة": "أسعار",
            "غالي": "مرتفع",
            "رخيص": "منخفض",
            "تقدية": "تسوق",
            "صرف": "نقود",
            "فلوس": "مال",
            "أورو": "يورو",
            "ريال": "عملة",
            
            # Food / Cafe
            "ماكلة": "طعام",
            "شواية": "شواء",
            "طاجين": "طاجين",
            "طواجن": "طواجن",
            "كسكس": "كسكس",
            "كول": "أكل",
            "ناكل": "أكل",
            "بغيت": "أريد",
            "جيعان": "جائع",
            "شبعان": "شبعان",
            "قهوة": "قهوة",
            "أتاي": "شاي",
            "براد": "إبريق شاي",
            "حريرة": "شوربة",
            "مسمن": "فطائر",
            "بغرير": "فطائر",
            
            # Directions / Navigation / Location
            "فين": "أين",
            "بلاصة": "مكان",
            "بلايص": "أماكن",
            "طريق": "طريق",
            "كيفاش": "كيف",
            "نمشي": "أذهب",
            "حومة": "حي",
            "درب": "زقاق",
            "دربنا": "زقاقنا",
            "سويقة": "سوق",
            "الرباط": "مكان",
            "الجامع": "مسجد",
            "كتبية": "الكتبية",
            "فندق": "فندق",
            "رياض": "رياض",
            "الرياض": "رياض",
            
            # Safety / Scams
            "مضرور": "متضرر",
            "خفت": "خوف",
            "خايف": "خوف",
            "خايفة": "خوف",
            "حضي": "احذر",
            "نصاب": "محتال",
            "نصابين": "محتالين",
            "نصب": "احتيال",
            "شفار": "سارق",
            "شفارة": "سارقين",
            "سرقة": "سرقة",
            "بوليس": "شرطة",
            "عاونوني": "مساعدة",
            "عاوني": "مساعدة",
            "مساعدة": "مساعدة",
            "تودرت": "ضائع",
            "ودرت": "ضعت",
            "وضيع": "ضائع",
            "مخطر": "خطر",
            
            # Story / Curious / History
            "حكاية": "قصة",
            "خرافة": "أسطورة",
            "صومعة": "منارة",
            "تاريخ": "تاريخ",
            "قالي": "أخبرني",
            "عاود": "احك",
            "حكي": "احك",
            "قول": "قل",
        }
        
        # French mixtures mapping
        french_map = {
            "resto": "restaurant",
            "gare": "train station",
            "taxi": "taxi",
            "prix": "price",
            "cher": "expensive",
            "gratis": "free",
            "danger": "danger",
            "vol": "theft",
            "police": "police",
            "securite": "safety",
            "chambre": "room",
            "hotel": "hotel",
            "billet": "ticket",
            "bus": "bus",
            "train": "train",
            "manger": "eat",
            "faim": "hungry",
            "peur": "afraid",
            "perdu": "lost",
            "aider": "help",
            "histoire": "history",
            "legende": "legend",
        }

        # 1. Clean up characters and map slang
        words = text.split()
        normalized_words = []
        for word in words:
            # Basic Arabic letter normalization
            for char in ["أ", "إ", "آ"]:
                word = word.replace(char, "ا")
            word = word.replace("ة", "ه")
            word = word.replace("ى", "ي")
            
            # Smart prefix removal for "ال" (only for words that are not recognized names)
            if word.startswith("ال") and len(word) > 4:
                if word not in ["الكتبية", "البهية", "الباهية"]:
                    word = word[2:]
            
            # Map Darija
            if word in darija_map:
                word = darija_map[word]
            # Map French mix
            elif word in french_map:
                word = french_map[word]
                
            normalized_words.append(word)
            
        return " ".join(normalized_words)

    def _detect_sentiment(self, text: str) -> str:
        """Detect user's emotional state to adapt Sahbi's tone using upgraded Darija engine."""
        norm = self._normalize_darija_and_multi_lang(text)
        if any(w in norm for w in ["خوف", "خطر", "مشكل", "worried", "scared", "unsafe", "help", "مساعدة", "احتيال", "سارق", "محتال", "afraid"]):
            return "worried"
        if any(w in norm for w in ["تعبان", "مللت", "tired", "boring", "stressed"]):
            return "tired"
        if any(w in norm for w in ["كيفاش", "علاش", "تاريخ", "history", "curious", "tell me", "قصة", "حكاية", "أسطورة", "legend", "احك"]):
            return "curious"
        if any(w in norm for w in ["نروح", "نكشف", "adventure", "explore", "hidden", "مغامرة", "جديد"]):
            return "adventurous"
        return "neutral"

    def _detect_intents(self, text: str) -> list:
        """Classify the user's primary intent(s) using upgraded Darija engine."""
        norm = self._normalize_darija_and_multi_lang(text)
        intents = []
        if any(w in norm for w in ["أين", "فين", "طريق", "زقاق", "حي", "direction", "navigate", "كيف", "وصول", "lost", "perdu", "adresse", "chemin"]):
            intents.append("navigation")
        if any(w in norm for w in ["مطعم", "أكل", "طعام", "restaurant", "food", "طاجين", "كسكس", "قهوة", "شاي", "شوربة", "فطائر", "eat", "cafe", "hungry", "faim", "manger"]):
            intents.append("food")
        if any(w in norm for w in ["رياض", "فندق", "hotel", "stay", "نبات", "room", "chambre"]):
            intents.append("accommodation")
        if any(w in norm for w in ["تاكسي", "حافلة", "قطار", "bus", "transport", "مواصلات", "سيارة أجرة"]):
            intents.append("transport")
        if any(w in norm for w in ["سعر", "ثمن", "أسعار", "يكلف", "مرتفع", "منخفض", "مال", "نقود", "price", "cost", "expensive", "cher", "how much"]):
            intents.append("pricing")
        if any(w in norm for w in ["خطر", "احتيال", "محتال", "سارق", "أمان", "شرطة", "scam", "safe", "police", "danger", "theft", "peur"]):
            intents.append("safety")
        if any(w in norm for w in ["تاريخ", "أسطورة", "قصة", "معلم", "landmark", "مسجد", "قصر", "museum", "monument", "history", "legend"]):
            intents.append("exploration")
        if not intents:
            intents.append("general")
        return intents

    def _save_chat_log(self, db: Session, request: ChatRequest, response_text: str, sentiment: str, intents: list) -> str:
        """Persist conversation to DB for the learning loop."""
        log_id = str(__import__('uuid').uuid4())
        try:
            from app.models import AIChatLog
            import json
            log = AIChatLog(
                id=log_id,
                user_query=request.message,
                ai_response=response_text[:2000],
                topic_tag=json.dumps(intents, ensure_ascii=False),
                sentiment=sentiment
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"AI Service: Chat log save failed: {e}")
        return log_id

    async def get_response(self, request: ChatRequest, db: Session) -> ChatResponse:
        """
        Processes the user message and returns an AI response with DB context.
        """
        cards_data = []
        # 0. Detect Sentiment & Intent (NLP Layer)
        detected_sentiment = self._detect_sentiment(request.message)
        detected_intents = self._detect_intents(request.message)
        print(f"AI NLP | Sentiment: {detected_sentiment} | Intents: {detected_intents}")

        # 1. Retrieve Place Context (Semantic Vector Search with Pinecone + Local Similarity Fallback)
        from app.services.pinecone_service import pinecone_service
        semantic_pois = pinecone_service.search_pois(request.message, limit=1)
        
        if semantic_pois:
            context_data = semantic_pois[0]
            context_desc = context_data.get("description", "A beautiful place in Marrakech.")
            safety_note = context_data.get("safety_note", "")
            # Align context_location for downstream lookups
            request.context_location = context_data.get("id", request.context_location)
            logger_name = context_data.get("name", "Unknown")
            print(f"AI RAG | Semantic POI Match: {logger_name}")
        else:
            context_key = request.context_location.lower().replace(" ", "_")
            context_data = self.knowledge_base.get(context_key, {})
            context_desc = context_data.get("description", "A beautiful place in Marrakech.")
            safety_note = context_data.get("safety_note", "")

        # Incorporate accurate Location if available
        location_context = ""
        if request.location:
            location_context = f"The user is at precise coordinates: {request.location.latitude}, {request.location.longitude}."

        # 2. Retrieve Price Context (Dynamic RAG + Live Web Search)
        price_context = ""
        msg_norm = self._normalize_darija_and_multi_lang(request.message)
        
        # KEYWORD MATCHING (English + Arabic Normalized)
        keywords = ["price", "cost", "how much", "expensive", "taxi", "buy", "mad", "fare", "سعر", "تاكسي", "مواصلات", "حافلة", "باص", "قطار", "محطة"]
        if any(self._normalize_darija_and_multi_lang(kw) in msg_norm for kw in keywords):
            # 2.1 Check DB for certified prices
            from app.services.scraper_service import scraper_service
            prices = db.query(ReferencePrice).all()
            found_prices = []
            for p in prices:
                if self._normalize_darija_and_multi_lang(p.item_name) in msg_norm:
                    found_prices.append(f"{p.item_name}: {p.min_price}-{p.max_price} {p.currency} ({p.unit})")
            
            if found_prices:
                price_context = "CERTIFIED FAIR PRICES: " + " | ".join(found_prices)
            
            # 2.2 FETCH LIVE WEB PRICES (New Integration)
            try:
                live_price_data = scraper_service.search_live_prices(request.message)
                price_context += f"\nLIVE WEB PRICE INFO: {live_price_data}"
            except Exception as e:
                print(f"AI Service: Live Price Search Failed: {e}")

        # 2.3 Spatial Neighborhood & Medina Confusing Alleys Navigation Logic (Graph Mapping)
        spatial_route_context = ""
        detected_landmarks = []
        if any(kw in msg_norm for kw in ["ساحه", "جامع الفنا", "fna", "jemaa"]):
            detected_landmarks.append("jemaa_el_fnaa")
        if any(kw in msg_norm for kw in ["باهيه", "palace", "bahia"]):
            detected_landmarks.append("bahia_palace")
        if any(kw in msg_norm for kw in ["يوسف", "school", "madrasa", "youssef"]):
            detected_landmarks.append("ben_youssef")
        if any(kw in msg_norm for kw in ["كتبيه", "koutoubia", "mosque"]):
            detected_landmarks.append("koutoubia")
        if any(kw in msg_norm for kw in ["ماجوريل", "garden", "majorelle"]):
            detected_landmarks.append("majorelle_garden")
            
        if len(detected_landmarks) >= 2:
            pair = (detected_landmarks[0], detected_landmarks[1])
            reverse_pair = (detected_landmarks[1], detected_landmarks[0])
            route_info = self.medina_alley_routes.get(pair) or self.medina_alley_routes.get(reverse_pair)
            if route_info:
                spatial_route_context = (
                    f"\nMEDINA SPATIAL NEIGHBORHOOD ROUTING CLUES (GRAPH CONNECTIVITY):\n"
                    f"Recommended Medina Route: {route_info['route']}\n"
                    f"Alley Navigation Detail: {route_info['clue']}\n"
                    f"Local Safety Alert: {route_info['warning']}\n"
                    f"Inject these exact pathing details and warning into your response to ensure the user gets safe, alley-level guidance."
                )

        # 2.5 Recommendation Context (Booking/TripAdvisor with Location & User Preference Logic)
        recommendation_context = ""
        
        # Detect Area
        detected_area = None
        if any(kw in msg_norm for kw in ["مدينة", "قديمة", "medina", "old city"]):
            detected_area = "Medina"
        elif any(kw in msg_norm for kw in ["جيليز", "كيليز", "gueliz", "new town"]):
            detected_area = "Gueliz"
        elif any(kw in msg_norm for kw in ["هيفيرناج", "هايفيرناج", "hivernage", "luxury area"]):
            detected_area = "Hivernage"

        is_asking_rec = any(kw in msg_norm for kw in [
            "riad", "hotel", "stay", "رياض", "فندق", "مطعم", "طعام", "restaurant", "food", "eat",
            "عشاء", "فطور", "غداء", "قهوة", "شاي", "cafe", "مقهى"
        ])
        
        if is_asking_rec:
            # 1. Scrape Live from Mocked Tripadvisor/Booking aggregator
            try:
                from app.services.scraper_service import scraper_service
                cards_data = scraper_service.search_restaurants(request.context_location or detected_area or "Jemaa el-Fnaa")
                
                # 2. Apply User Preference Weight Boosting (Continuous Learning Loop)
                try:
                    from app.models import UserPreference
                    prefs = db.query(UserPreference).all()
                    pref_map = {p.category.lower(): p.weight for p in prefs}
                    
                    if pref_map:
                        for c in cards_data:
                            desc_lower = c.get('description', '').lower()
                            name_lower = c.get('name', '').lower()
                            boost_score = 1.0
                            
                            for category, weight in pref_map.items():
                                if category in desc_lower or category in name_lower:
                                    boost_score *= weight
                            
                            c['boost_score'] = boost_score
                            if boost_score > 1.1:
                                # Decorate item name and description to visually signify personalized recommendations in UI
                                c['name'] = "⭐ " + c['name']
                                c['description'] = "[صاحبي كيقترحها حيت كتعجبك هاد الميزة] " + c['description']
                        
                        # Sort cards by boost score descending so favored items appear first
                        cards_data.sort(key=lambda x: x.get('boost_score', 1.0), reverse=True)
                except Exception as pref_err:
                    print(f"AI Service: Preference Boosting failed: {pref_err}")
                
                # Create a concise formatted string for LLM so it generates the right Arabic summary
                names = [f"{c['name']} ({c['rating']} stars, {c['distance']})" for c in cards_data]
                recommendation_context = (
                    f"LIVE DISCOVERY DATA (DuckDuckGo/TripAdvisor): {', '.join(names)}. "
                    f"RAW WEB SEARCH CONTEXT: {cards_data[0]['description'] if cards_data else ''}. "
                    "In your response, focus on real, current information. Mention that the user can TAP the card for navigation."
                )
            except Exception as e:
                print(f"AI Service: Scraper API Failed: {e}")
                cards_data = []
                recommendation_context = "SEARCH UNAVAILABLE. Rely on internal knowledge."

        # 2.6 Partner Injection (The Money Engine)
        # We fetch partners from the DB to prioritize them in the AI's response.
        partner_context = ""
        try:
            from app.core.database import SessionLocal
            with SessionLocal() as db_session:
                partners = db_session.query(Place).filter(Place.is_partner == True).all()
                if partners:
                    partner_list = [f"{p.name} ({p.category}): {p.description or 'Premium partner'}. Address: {p.address}" for p in partners]
                    partner_context = "MAHIR'S CERTIFIED PARTNERS (HIGH PRIORITY - PITCH THESE): " + " | ".join(partner_list)
        except Exception as e:
            print(f"AI Service: Partner Injection Failed: {e}")

        # 3. Try n8n Agent (Optional - if set as production-agent)
        if self.n8n_webhook_url and "n8n" in os.getenv("AI_EXECUTION_MODE", "").lower():
            try:
                async with httpx.AsyncClient() as client:
                    n8n_payload = {
                        "message": request.message,
                        "location": {
                            "lat": request.location.latitude if request.location else None,
                            "lng": request.location.longitude if request.location else None
                        },
                        "context_location": request.context_location,
                        "language": request.language,
                        "user_id": "test_user_id" # Replace with real user ID if needed
                    }
                    
                    response = await client.post(
                        self.n8n_webhook_url,
                        json=n8n_payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        n8n_data = response.json()
                        # n8n response should follow our standard ChatResponse schema
                        return ChatResponse(
                            response=n8n_data.get("response", "No response from n8n"),
                            conversation_id=request.conversation_id,
                            safety_alert=n8n_data.get("safety_status", "Green") != "Green",
                            results_cards=n8n_data.get("results_cards", cards_data)
                        )
                    else:
                        print(f"AI Service: n8n returned error {response.status_code}")
            except Exception as e:
                print(f"AI Service: n8n connection failed: {e}")

        # 4. Fallback to Direct AI (Existing Logic)
        if self.llm:
            try:
                # GET CURRENT TIME FOR CONTEXT
                from datetime import datetime
                current_time = datetime.now().strftime("%H:%M")
                
                # Build mood directive based on detected sentiment
                mood_directives = {
                    "worried": "The user seems WORRIED or unsafe. Be PROTECTIVE, calm, and immediately focused on safety. Tell them the nearest safe spot.",
                    "tired": "The user seems TIRED or stressed. Be BRIEF, gentle, and suggest comfort options: a hammam, a quiet riad cafe, or a reliable taxi.",
                    "curious": "The user is CURIOUS! Activate HAKAWATI (Storyteller) MODE. Use evocative, poetic language to tell stories. Prefix stories with [STORY].",
                    "adventurous": "The user is ADVENTUROUS! Be energetic, suggest hidden gems, street food, or off-the-beaten-path experiences.",
                    "neutral": "Be warm, balanced, and helpful."
                }
                active_mood = mood_directives.get(detected_sentiment, mood_directives["neutral"])

                system_prompt = (
                    f"You are Sahbi (صاحبي), a hyper-intelligent, charismatic, and deeply intuitive local guide from Marrakech. "
                    f"Your name 'Sahbi' means 'My Friend' in Darija, and you act as a loyal, protective, and world-class companion. "

                    f"DETECTED USER MOOD: [{detected_sentiment.upper()}] — {active_mood}\n\n"

                    f"CORE INTELLIGENCE DIRECTIVES:\n"
                    f"0. DATA FIDELITY: You have access to the 'Marrakech Official Knowledge Base'. DO NOT hallucinate. Use ONLY the provided 'Contextual Data' for specific prices, partner names, and safety warnings. If data is missing, admit it.\n"
                    f"1. MOOD-AWARE RESPONSE: {active_mood} "
                    f"- If the user is TIRED/STRESSED: Be brief, calming, and focus on comfort (Hammam, quiet cafes, reliable transport). "
                    f"- If the user is ADVENTUROUS: Be energetic and suggest hidden gems, bustling markets, or street food. "
                    f"- If the user is CURIOUS: Activate 'HAKAWATI MODE' (Storyteller). Tell legends and historical secrets about Marrakech. "
                    f"- If the user is WORRIED: Be protective, firm, and safety-focused. "
                    
                    f"2. THE HAKAWATI (STORYTELLER) MODE: When discussing landmarks or history, don't just give facts. "
                    f"Use evocative language. (Example: 'The Koutoubia isn't just a tower; it's the heartbeat of the city that has seen a thousand years of sunsets'). "
                    f"IMPORTANT: Prefix every historical legend or long story with the marker [STORY] so the UI can format it properly. "
                    
                    f"3. CONTEXTUAL INFERENCE: Read between the lines. If the user is vague, infer their need. "
                    f"(Example: 'It's too much' -> Suggest a nearby garden or a quiet Riad). "
                    
                    f"4. SPATIAL & TIME AWARENESS: Use the location context ({request.context_location}) and current time ({current_time}). "
                    f"User GPS Location: {location_context}. "
                    
                    f"5. PROACTIVE PROTECTION: Immediately recognize 'Fake Guide' or 'Scam' scenarios and provide firm, protective advice. "
                    
                    f"6. THE BARGAINING MASTER: When the user asks about prices or how to negotiate, give them a specific strategy. "
                    f"Teach them 1-2 Darija phrases (e.g., 'Ghalia bezzat!' - Too expensive, 'Akher taman?' - Last price?). "
                    f"Explain the '50% Rule': start at 50% of the offer and aim for 60-70%. "
                    
                    f"7. PERSONALITY & LANGUAGE BLENDING: You are sophisticated, warm (Bahja style), and highly hospitable. "
                    f"REPLY IN THE USER'S PREFERRED LANGUAGE ({request.language}). "
                    f"- When responding in Arabic/Darija: Blend Standard Arabic with elegant, welcoming Moroccan Darija phrases naturally (e.g. 'أهلاً بصاحبي', 'مرحبا بك في البهجة', 'الله يحفظك', 'بصحة وراحة'). "
                    f"- When responding in English/French/others: Keep the tone highly natural and standard in that language, but warmly sprinkle authentic Moroccan Darija terms where they add beautiful local color, and immediately provide a brief, friendly English/French translation or explanation in brackets (e.g. 'Marhaban bikum!' [Welcome!], 'Bseha' [Enjoy/To your health], 'Sahbi' [My friend]). Always make the user feel welcomed and safe. "

                    
                    f"8. RECOMMENDATIONS: Always suggest exactly 3 options. "
                    f"CRITICAL: If relevant partners are available ({partner_context}), YOU MUST PRIORITIZE THEM as your top choices (Top 1 and 2). "
                    
                    f"9. INTUITIVE SAFETY: If the user says 'I feel unsafe', don't ask 'Why?'. Immediately tell them "
                    f"where the nearest safe police point or verified place is based on their GPS.\n\n"
                    
                    f"10. SCAM-SHIELD OCR MODE (VISION): If an image is provided, you are now in 'Scam-Shield' mode. "
                    f"Extract items and prices from the image. Compare them with the CERTIFIED FAIR PRICES: {price_context}. "
                    f"Be very specific. (Example: 'You paid 100 MAD for a taxi ride that should cost 30 MAD. This is a scam.'). "
                    f"Always maintain your protective 'Sahbi' persona."
                )
                
                # Multi-modal support if image is present
                if request.image_url:
                    from langchain_core.messages import HumanMessage
                    content = [
                        {"type": "text", "text": request.message or "Analyze this receipt/menu for fair pricing."},
                        {"type": "image_url", "image_url": {"url": request.image_url}}
                    ]
                    messages = [
                        ("system", system_prompt + f"\nContextual Data: {partner_context} {price_context}"),
                        HumanMessage(content=content)
                    ]
                else:
                    messages = [
                        ("system", system_prompt + f"\nContextual Data: {partner_context} {price_context} {recommendation_context} {spatial_route_context}"),
                        ("human", request.message)
                    ]
                response = await self.llm.ainvoke(messages)
                
                # Check for safety alert based on content + logic
                # response.content can be a list for multi-modal responses, coerce to str
                raw_content = response.content
                if isinstance(raw_content, list):
                    response_content = " ".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in raw_content
                    )
                else:
                    response_content = str(raw_content)
                
                safety_note_str = str(safety_note) if safety_note else ""
                has_security_keyword = any(
                    kw in response_content.lower() or kw in request.message.lower()
                    for kw in ["scam", "danger", "warning", "fake", "نصب", "خطر", "تحذير", "unsafe", "police"]
                )
                
                # Save to DB for Learning Loop
                log_id = self._save_chat_log(db, request, response_content, detected_sentiment, detected_intents)
                final = ChatResponse(
                    id=log_id,
                    response=response_content,
                    conversation_id=request.conversation_id,
                    safety_alert=has_security_keyword or "warning" in safety_note_str.lower(),
                    results_cards=cards_data
                )
                return final
            except Exception as gemini_err:
                import traceback
                print(f"🔴 AI Error (Primary LLM): {type(gemini_err).__name__}: {gemini_err}")
                
                # Attempt runtime fallback to DeepSeek if available
                if settings.DEEPSEEK_API_KEY:
                    print("🔄 Attempting runtime fallback to DeepSeek...")
                    try:
                        from langchain_openai import ChatOpenAI
                        fallback_llm = ChatOpenAI(
                            model="deepseek-chat",
                            api_key=settings.DEEPSEEK_API_KEY,
                            base_url="https://api.deepseek.com",
                            temperature=0.7
                        )
                        response = await fallback_llm.ainvoke(messages)
                        raw_content = response.content
                        if isinstance(raw_content, list):
                            response_content = " ".join(
                                part.get("text", "") if isinstance(part, dict) else str(part)
                                for part in raw_content
                            )
                        else:
                            response_content = str(raw_content)
                        has_security_keyword = any(kw in response_content.lower() or kw in request.message.lower() 
                                                 for kw in ["scam", "danger", "warning", "fake", "نصب", "خطر", "تحذير", "unsafe", "police"])
                        
                        log_id = self._save_chat_log(db, request, response_content, detected_sentiment, detected_intents)
                        safety_note_str = str(safety_note) if safety_note else ""
                        final = ChatResponse(
                            id=log_id,
                            response=response_content,
                            conversation_id=request.conversation_id,
                            safety_alert=has_security_keyword or "warning" in safety_note_str.lower(),
                            results_cards=cards_data
                        )
                        return final
                    except Exception as deepseek_err:
                        print(f"🔴 DeepSeek Fallback also failed: {deepseek_err}")

        # 4. Fallback Logic (Final Stand)
        err_msg = ""
        if "gemini_err" in locals(): err_msg += f"Gemini Error: {gemini_err}. "
        if "deepseek_err" in locals(): err_msg += f"DeepSeek Error: {deepseek_err}. "
        
        if err_msg:
            print(f"⚠️ Both primary and fallback LLMs failed: {err_msg}. Falling back to offline smart response.")
            
        return self._get_fallback_response(request, context_data, price_context, cards_data, db=db)

    def _get_fallback_response(self, request: ChatRequest, context_data: dict, price_context: str, cards_data: list, db=None) -> ChatResponse:
        msg = self._normalize_darija_and_multi_lang(request.message)
        response_text = ""
        safety_alert = False
        
        # Use explicit language preference or detect fallback
        is_arabic = request.language.startswith('ar') or any(char in msg for char in "آابتثجحخدذرزسشصضطظعغفقكلمنهوي")

        # 1. Price Context
        if price_context:
            if is_arabic:
                response_text = f"حسب بياناتي، هذه هي الأسعار العادلة: {price_context}. إذا طلبوا أكثر، غالباً نصب!"
            else:
                response_text = f"According to my records, here are the fair prices: {price_context}. If you are quoted more, it might be a scam!"
            safety_alert = True
        
        # 2. Taxi
        elif any(w in msg for w in ["taxi", "تاكسي"]):
            if is_arabic:
                response_text = "ديما اطلب 'الكونتور' (العداد). التوصيلة وسط المدينة ما لازم تفوت 20-30 درهم."
            else:
                response_text = "Always insist on the taxi meter (Compteur). A typical ride within the city allows cost between 20-40 MAD."
            safety_alert = True
            
        # 3. Bus / Transport
        elif any(w in msg for w in ["bus", "حافلة", "طوبيس", "transport"]):
            if is_arabic:
                response_text = "حافلات ألزا (ALSA) نظيفة ورخيصة (4 دراهم). رقم 5 تدي للمحطة (لاكار)، ورقم 19 للمطار (30 درهم)."
            else:
                response_text = "ALSA buses are great. #5 goes to Train Station (4 MAD), #19 to Airport (30 MAD). Pay in coins."

        # 4. Train / Station
        elif any(w in msg for w in ["train", "station", "قطار", "محطة", "لاكار"]):
            if is_arabic:
                response_text = "محطة القطار (لاكار) كاينة في شارع الحسن الثاني. خود طوبيس رقم 5 من الساحة (جامع الفنا) بـ 4 دراهم."
            else:
                response_text = "The Train Station (Gare ONCF) is on Hassan II Avenue. Take Bus #5 from Jemaa el-Fna (4 MAD)."

        # 5. Fish & Seafood (حوت / سمك)
        elif any(w in msg for w in ["حوت", "سمك", "fish", "poisson", "seafood"]):
            # Specific Jemaa El-Fnaa fish stalls recommendation
            if any(w in msg for w in ["جامع", "فنا", "fna", "ساحه", "square"]):
                if is_arabic:
                    response_text = (
                        "🐟 الحوت في جامع الفنا زوين بزاف وسخون! كنصحك تمشي لـ **كشك رقم 14 (الحاج الأمين)** هو أشهر واحد تما في الحوت المقلي المتنوع (الصول، الكلمار، الميرلا والشرن).\n\n"
                        "⚠️ **درع الحماية (نصيحة صاحبي):**\n"
                        "- ديما حضي مع الحساب والأسعار المكتوبة في المنيو.\n"
                        "- اطلب الماكلة بالعبار (مثلاً ربع كيلو أو نصف كيلو) باش ما تجيكش الفاتورة غالية بزاف.\n"
                        "- المشروبات والسلطات الجانبية اللي كيحطوها بلا ما تطلبها كتكون بالفلوس، إذا ما بغيتيهاش قول ليهم يحيدوها."
                    )
                else:
                    response_text = (
                        "🐟 Eating fish at Jemaa el-Fnaa is a must-try experience! I recommend going to **Stall #14 (Haj Al-Amin)**, the most famous spot for fried fish (sole, squid, whiting).\n\n"
                        "⚠️ **Sahbi's Safety Tip:**\n"
                        "- Always check the bill and compare it with the menu prices.\n"
                        "- Order by weight (e.g., 250g or 500g) rather than letting them prepare an open plate, to avoid surprises on the bill.\n"
                        "- Side salads and bread they bring without you asking are NOT free. If you don't want them, ask them to take them back."
                    )
            else:
                # General fish recommendation
                if is_arabic:
                    response_text = (
                        "🐟 إذا بغيت تاكل الحوت (السمك) في مراكش:\n"
                        "1. **Patron de la Mer** (في جيليز/هيفيرناج): مطعم راقٍ وممتاز للأسماك الطازجة والبايلّا (Paella).\n"
                        "2. **كشك رقم 14** في جامع الفنا: تجربة شعبية رائعة للسمك المقلي.\n"
                        "منطقة هيفيرناج هي الأفضل للمطاعم الراقية للأسماك."
                    )
                else:
                    response_text = (
                        "🐟 If you want to eat fish/seafood in Marrakech:\n"
                        "1. **Patron de la Mer** (in Gueliz/Hivernage): A premium sit-down restaurant famous for fresh fish, paella, and grilled seafood.\n"
                        "2. **Stall #14** at Jemaa el-Fnaa: A lively street food experience for diverse fried fish.\n"
                        "Let me know if you want directions to any of these!"
                    )

        # 6. General Food / Eat / Restaurant / Riad
        elif any(w in msg for w in ["riad", "hotel", "stay", "رياض", "فندق", "مطعم", "طعام", "restaurant", "food", "eat", "أكل", "ناكل", "ماكلة", "طاجين", "كسكس"]):
            # Detect area, including Jemaa El-Fnaa -> Medina mapping
            da = None
            if any(kw in msg for kw in ["مدينة", "قديمة", "medina", "old city", "جامع", "فنا", "fna", "ساحه", "square"]): 
                da = "Medina"
            elif any(kw in msg for kw in ["جيليز", "كيليز", "gueliz", "new town"]): 
                da = "Gueliz"
            elif any(kw in msg for kw in ["هيفيرناج", "هايفيرناج", "hivernage", "luxury area"]): 
                da = "Hivernage"

            if not da:
                da = "Medina" # Default to Medina if unspecified but asking about food

            category = "riads" if any(w in msg for w in ["riad", "hotel", "رياض"]) else "restaurants"
            items = self.recommendations.get(da, {}).get(category, [])[:3]
            if items:
                options = ""
                if is_arabic:
                    options = "\n".join([f"- **{i['name']}**: {i['quality']} ({i['distance']}). الأمان: {i['safety']}" for i in items])
                    response_text = f"🍽️ إليك أفضل الاقتراحات الموثوقة والمعتمدة في **{da}**:\n\n{options}\n\nيمكنك الضغط على بطاقة المطعم في شاشة المطاعم لمعرفة الموقع وطريق الوصول!"
                else:
                    options = "\n".join([f"- **{i['name']}**: {i['quality']} ({i['distance']}). Safety: {i['safety']}" for i in items])
                    response_text = f"🍽️ Here are the top vetted recommendations in the **{da}** area:\n\n{options}\n\nYou can also tap the restaurant card in the Dining tab for directions!"
            else:
                if is_arabic:
                    response_text = "أي منطقة تهمك؟ (المدينة القديمة، جيليز، أو هيفيرناج؟) لكي أعطيك أفضل الاقتراحات الموثوقة."
                else:
                    response_text = "Which area are you interested in? (Medina, Gueliz, or Hivernage?) so I can give you the best vetted recommendations."

        # 6. Safety / Scams
        elif any(w in msg for w in ["safety", "safe", "scam", "danger", "police", "أمان", "سرقة", "خطر", "احتيال", "lost", "help"]):
            if is_arabic:
                response_text = f"مراكش آمنة، ولكن رد بالك في الزحام. {context_data.get('safety_note', '')}"
            else:
                response_text = f"Marrakech is generally safe. {context_data.get('safety_note', '')}"
        
        # 7. Greetings
        elif any(w in msg for w in ["hello", "hi", "salam", "hola", "سلام", "مرحبا", "اهلين"]):
            if is_arabic:
                response_text = "وعليكم السلام! أنا ماهر. سولني على أي بلاصة، ثمن، أو كول (أكل) في مراكش."
            else:
                response_text = "Salam! I'm Mahir. Ask me about prices, directions, food, or buses in Marrakech!"

        # 8. Where / Location (General)
        elif any(w in msg for w in ["where", "location", "فين", "أين", "بلاصة", "طريق", "way", "directions"]):
            if is_arabic:
                response_text = "في مراكش، أحسن طريقة هي تسول 'مول الحانوت' (البقال). هما كيعرفوا الزناقي كثر من Google Maps! واش كتقلب على شي بلاصة محددة؟"
            else:
                response_text = "In Marrakech, the best GPS is asking a local shopkeeper (Moul Hanout). They know the Medina better than Google Maps! Are you looking for a specific landmark?"

        # 9. General Info / About Marrakech / What to do
        elif any(w in msg for w in ["marrakech", "مراكش", "visit", "do", "see", "نشوف", "بلايص", "landmarks"]):
            if is_arabic:
                response_text = "مراكش مدينة السحر! كننصحك بـ جامع الفنا، مدرسة بن يوسف، وحدائق ماجوريل. كاين بزاف ما يتشاف!"
            else:
                response_text = "Marrakech is magical! I recommend Jemaa el-Fna, Ben Youssef Madrasa, and Majorelle Garden. There's so much to explore!"

        # Default "Smart" Fallback (Instead of Error)
        else:
            if is_arabic:
                response_text = "أنا ماهر، مرشدك المحلي. واخا ما فهمتش سؤالك مزيان، نقدر نعاونك في ثمن التاكسي، الماكلة الزوينة، ولا نوري الطريق. عاود طرح سؤالك بطريقة أخرى؟"
            else:
                response_text = "I'm Mahir, your local guide. I didn't quite catch that, but I can help with fair prices, safe food, or directions. Could you try rephrasing your question?"

        if cards_data and not response_text.startswith("إليك أفضل 3"):
            response_text = "إليك أفضل النتائج التي وجدتها قريبة منك:"

        log_id = None
        if db is not None:
            detected_sentiment = self._detect_sentiment(request.message)
            detected_intents = self._detect_intents(request.message)
            log_id = self._save_chat_log(db, request, response_text, detected_sentiment, detected_intents)

        final_response = ChatResponse(id=log_id, response=response_text + "\n\n[v2.2-AreaSearch]", conversation_id=request.conversation_id, safety_alert=safety_alert, results_cards=cards_data)
        return final_response


    async def generate_itinerary(self, num_days: int, interests: list, language: str = "ar") -> list:
        """
        Generates a structured daily itinerary using Gemini AI.
        """
        if not self.llm:
            return [] # Fallback to hardcoded logic in router

        try:
            interest_str = ", ".join(interests)
            lang_prompt = "Arabic (Darija style description)" if language == "ar" else "English"
            
            prompt = (
                f"Generate a {num_days}-day travel itinerary for Marrakech, Morocco. "
                f"The traveler's interests are: {interest_str}. "
                f"RESPONSE MUST BE A VALID JSON LIST of objects matching this structure: "
                "{"
                "  'day_number': int, "
                "  'title': 'short title', "
                "  'activities': [{"
                "    'time': 'HH:MM', "
                "    'place_name': 'name', "
                "    'description': 'short description', "
                "    'category': 'one of [history, food, shopping, nature, culture]', "
                "    'duration_minutes': int"
                "  }]"
                "} "
                f"Please provide {lang_prompt} names and descriptions. "
                "Include hidden gems, safety tips for specific areas, and authentic local experiences. "
                "Return ONLY the JSON list, no markdown formatting."
            )
            
            response = self.llm.invoke(prompt)
            # Clean possible markdown formatting
            clean_content = response.content.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_content)
        except Exception as e:
            print(f"AI Itinerary Error: {e}")
            return []

ai_service = AIService()
