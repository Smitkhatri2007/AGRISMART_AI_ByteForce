"""
AgriSmart AI - Groq Agricultural Advisor Service
Uses Groq API (with LLaMA 3.3 70B) to:
1. Generate insightful, farmer-friendly descriptions of detected crop diseases.
2. Prompt the farmer if they want a comprehensive cure and treatment plan.
3. Prescribe customized organic & chemical treatment plans with exact dosages and recovery timelines.
Includes robust offline fallback to ensure reproducibility without requiring an API key.
"""

import json
from typing import Dict, Any, Optional
from app.config import settings
from model.class_catalog import CLASS_METADATA

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqAdvisorService:
    """
    Connects to Groq API for agronomic disease descriptions and cure planning.
    """
    
    LANG_MAP = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "gu": "Gujarati"
    }

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = Groq(api_key=self.api_key) if Groq and self.api_key else None

    def _call_groq(self, prompt: str, temperature: float = 0.4, is_json: bool = False) -> Optional[str]:
        """
        Direct call to Groq API using the groq SDK.
        """
        if not self.client:
            return None

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_completion_tokens=1000,
                top_p=1,
            )
            content = completion.choices[0].message.content
            return content.strip()
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None

    def describe_disease(
        self,
        disease_name: str,
        crop: str,
        severity: str = "Medium",
        is_healthy: bool = False,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Step 1: Generates an informative disease description and asks the farmer if they want a cure plan.
        """
        if is_healthy:
            return {
                "disease_name": "Healthy Plant",
                "crop": crop,
                "status": "Healthy",
                "description": (
                    f"Good news! Your {crop} plant appears healthy with no visible signs of pathogen attack or necrotic lesions. "
                    f"Leaves show normal chlorophyll distribution and cellular vitality."
                ),
                "potential_risks": "Seasonal humidity fluctuations or soil splash may introduce fungal spores.",
                "follow_up_prompt": f"Your {crop} is currently healthy. Would you like a preventative maintenance guide to protect it?",
                "requires_cure": False,
                "ai_provider": "AgriSmart AI (Healthy Status)"
            }

        full_lang = self.LANG_MAP.get(language, "English")
        prompt = (
            f"You are an expert agronomist speaking to a farmer. "
            f"The farmer's {crop} crop has been diagnosed with '{disease_name}' with {severity} severity. "
            f"Please provide:\n"
            f"1. A concise, clear 2-3 sentence description of this disease, what causes it (fungal/bacterial/viral), and how it affects yield.\n"
            f"2. Early signs to watch for on other leaves.\n"
            f"Respond in {full_lang} in plain, encouraging words suitable for a farmer."
        )

        response = self._call_groq(prompt)

        if response:
            description_text = response
            provider = f"Groq ({self.model})"
        else:
            meta = CLASS_METADATA.get(disease_name, {})
            precaution = meta.get("precaution", "Avoid overhead watering.")
            description_text = (
                f"{disease_name} is a common agricultural disease affecting {crop}. "
                f"It primarily attacks foliage, creating characteristic lesions that diminish photosynthetic capacity and reduce marketable crop yield. "
                f"Immediate cultural precaution: {precaution}"
            )
            provider = "AgriSmart Knowledge Base (Offline Fallback)"

        follow_up_question = f"Would you like a detailed step-by-step cure and treatment plan for {disease_name}?"

        return {
            "disease_name": disease_name,
            "crop": crop,
            "status": "Infected",
            "severity": severity,
            "description": description_text,
            "follow_up_prompt": follow_up_question,
            "requires_cure": True,
            "ai_provider": provider
        }

    def generate_cure_plan(
        self,
        disease_name: str,
        crop: str,
        growth_stage: str = "Growing",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Step 2: Generated when the farmer confirms they want a cure plan.
        Delivers phased treatment, recovery probability, exact dosages, and safety intervals.
        """
        meta = CLASS_METADATA.get(disease_name, {})
        is_healthy = meta.get("is_healthy", False)

        if is_healthy:
            return {
                "disease_name": disease_name,
                "crop": crop,
                "recovery_chance_pct": 100.0,
                "recovery_timeline": "No recovery needed - crop is healthy",
                "urgency_level": "MAINTENANCE",
                "organic_treatment": "Apply neem oil (1500 PPM) @ 3 ml/L water once every 20 days as a preventative measure.",
                "chemical_treatment": "No chemical fungicides needed.",
                "cultural_management": "Ensure regular weed control and balanced irrigation.",
                "safety_guidance": "Spray during cool morning hours.",
                "ai_provider": "AgriSmart AI (Healthy Maintenance)"
            }

        full_lang = self.LANG_MAP.get(language, "English")
        prompt = (
            f"You are a master agricultural scientist and crop physician. "
            f"A farmer's {crop} in the '{growth_stage}' stage is suffering from '{disease_name}'. "
            f"Provide a structured, step-by-step cure and recovery plan in JSON format with the following keys:\n"
            f"- 'recovery_chance_pct': (number between 60 and 95, representing recovery likelihood with prompt action)\n"
            f"- 'recovery_timeline': (e.g. '7–10 days with timely treatment')\n"
            f"- 'urgency_level': ('CRITICAL (Act within 24–48 hours)' or 'HIGH' or 'MODERATE')\n"
            f"- 'containment_action': (immediate physical/pruning steps)\n"
            f"- 'organic_treatment': (exact organic spray, brand/type, and dosage in ml/L or g/L)\n"
            f"- 'chemical_treatment': (exact chemical fungicide/bactericide and dosage in g/L, with safety withholding period)\n"
            f"- 'cultural_management': (irrigation adjustments, spacing, sanitizing tools)\n"
            f"- 'prognosis_summary': (encouraging 1-2 sentence summary for the farmer)\n"
            f"Respond ONLY with valid JSON. Ensure all text values within the JSON are translated to {full_lang}."
        )

        response = self._call_groq(prompt, temperature=0.2, is_json=True)

        if response:
            try:
                clean_json = response.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()

                parsed = json.loads(clean_json)
                parsed["disease_name"] = disease_name
                parsed["crop"] = crop
                parsed["ai_provider"] = f"Groq ({self.model})"
                return parsed
            except Exception:
                pass

        severity = meta.get("severity", "Medium")
        recovery_chance = 75.0 if severity == "High" else 88.0
        timeline = "10–14 days with intensive treatment" if severity == "High" else "5–7 days with standard treatment"
        urgency = "CRITICAL (Act within 24–48 hours)" if severity == "High" else "MODERATE (Act within 3–5 days)"

        return {
            "disease_name": disease_name,
            "crop": crop,
            "recovery_chance_pct": recovery_chance,
            "recovery_timeline": timeline,
            "urgency_level": urgency,
            "containment_action": f"Remove and burn infected leaves immediately. {meta.get('precaution', '')}",
            "organic_treatment": f"{meta.get('organic_remedy', 'Apply copper soap spray')}. Dosage: 4–5 ml/L water every 5 days.",
            "chemical_treatment": f"{meta.get('chemical_remedy', 'Apply registered fungicide')}. Dosage: 2–2.5 g/L water.",
            "cultural_management": "Switch to drip irrigation and avoid overhead sprinkling to prevent spreading spores.",
            "prognosis_summary": f"Your {crop} has an estimated {recovery_chance}% chance of full recovery if treatment begins promptly.",
            "ai_provider": "AgriSmart Knowledge Base (Offline Fallback)"
        }

    def _generate_local_chat_reply(
        self,
        message: str,
        disease_name: Optional[str],
        crop: Optional[str],
        language: str = "en"
    ) -> str:
        """
        Intelligent rule-based local agronomist dialogue engine.
        Enables natural, interactive conversation even when running offline or without an API key.
        """
        q = (message or "").lower().strip()
        c = crop if crop and crop.lower() not in ["none", "field crops", "unknown"] else "Crop"
        d = disease_name if disease_name and disease_name.lower() not in ["none", "general farm health", "unknown"] else None
        is_hi = language == "hi"

        # 1. Greetings & Bot Identity / Introduction
        if any(w in q for w in ["hi", "hello", "hey", "namaste", "namaskar", "kem cho", "who are you", "what are you", "your name", "help", "नमस्ते", "हेलो", "हाय"]):
            if is_hi:
                return (
                    "### 🌿 नमस्ते! मैं एग्रीस्मार्ट एआई (AgriBot) हूँ।\n\n"
                    "मैं आपका स्मार्ट डिजिटल कृषि सलाहकार हूँ। मैं निम्नलिखित में आपकी सहायता कर सकता हूँ:\n\n"
                    "1. **रोग निदान व उपचार**: अपनी पत्ती की फोटो अपलोड करें और तुरंत जैविक/रासायनिक उपचार जानें।\n"
                    "2. **सटीक छिड़काव खुराक**: 15 लीटर नैपसैक स्प्रेयर के लिए सही पानी व दवा का अनुपात।\n"
                    "3. **मौसम व छिड़काव विंडो**: हवा की गति और बारिश के आधार पर स्प्रे करने का सर्वोत्तम समय।\n"
                    "4. **स्मार्ट ड्रिप सिंचाई**: मिट्टी की नमी और मौसम पूर्वानुमान के अनुसार पानी की मात्रा।\n"
                    "5. **फसल चयन**: आपकी मिट्टी और मौसम के लिए सबसे उपयुक्त फसलें।\n\n"
                    "आप मुझसे खेती से जुड़ा कोई भी सवाल पूछ सकते हैं!"
                )
            return (
                "### 🌿 Hello! I am AgriBot AI, your Smart Agricultural Assistant.\n\n"
                "I'm here to help you maximize crop yields, protect plant health, and manage farm resources effectively. Here is what I can do:\n\n"
                "1. **Disease Diagnosis & Cure**: Upload a leaf image on the dashboard for instant disease identification and recovery plans.\n"
                "2. **Precision Spray Calculations**: Calculate exact knapsack tank dilutions and milliliters per acre to avoid chemical burn.\n"
                "3. **Weather-Optimized Spraying**: Check wind drift risks and optimal temperature windows before applying treatments.\n"
                "4. **Smart Irrigation Scheduling**: Calculate exact root-zone water demands based on FAO-56 standards.\n"
                "5. **Crop Rotation & Soil Selection**: Discover ideal crops for your soil texture and pH.\n\n"
                "How can I assist your farm today? Feel free to ask any farming or crop care question!"
            )

        # 2. Dosage & Spray Tank Dilution (Checked before weather so 'neem spray' or 'spray dosage' matches dosage)
        if any(w in q for w in ["dosage", "how much", "tank", "dilution", "dose", "ml", "gram", "rate", "neem", "recipe", "खुराक", "लीटर", "ग्राम", "नीम"]):
            c_name = c if c != "Crop" else "your crop"
            if is_hi:
                return (
                    f"### 🎯 15-लीटर स्प्रेयर टैंक के लिए खुराक गाइड ({c_name})\n\n"
                    "* **नीम का तेल (जैविक)**: 15 लीटर पानी की टंकी में **60–75 मिली** (4–5 मिली प्रति लीटर) + 2 मिली हल्का लिक्विड साबुन इमल्सीफायर के रूप में मिलाएं।\n"
                    "* **रासायनिक कवकनाशी (मैनकोज़ेब / कॉपर)**: 15 लीटर की टंकी में **30–37.5 ग्राम** (2–2.5 ग्राम प्रति लीटर) मिलाएं।\n"
                    "* **प्रति एकड़ आवश्यकता**: 1 एकड़ परिपक्व फसल के लिए आमतौर पर 10 से 12 स्प्रे टैंक (~150–180 लीटर पानी) की आवश्यकता होती है।\n"
                    "* **टिप**: पत्तियों की निचली सतह पर दवा अच्छी तरह पहुंचे, इसके लिए हॉलो-कोन नोजल का प्रयोग करें।"
                )
            return (
                f"### 🎯 Precision Spray Tank Dilution Guide ({c_name})\n\n"
                "* **Standard 15-Litre Knapsack Sprayer**:\n"
                "  - **Organic (Neem Oil 10,000 PPM / Bio-agents)**: Mix **60–75 ml** per 15L tank (4–5 ml/L water) + 2 ml mild liquid soap as an emulsifier.\n"
                "  - **Chemical Fungicides (e.g. Mancozeb 75% WP / Copper Oxychloride)**: Mix **30–37.5 g** per 15L tank (2–2.5 g/L water).\n"
                "* **Coverage per Acre**: Approximately 10 to 12 knapsack refills (~150 to 180 Litres total solution) are required for 1 acre of mature foliage.\n"
                "* **Application Tip**: Spray early in the morning using a hollow-cone nozzle, coating both upper and lower leaf surfaces."
            )

        # 3. Weather & Spraying Safety Window
        if any(w in q for w in ["weather", "rain", "wind", "forecast", "temp", "safe to spray", "when to spray", "मौसम", "बारिश", "हवा"]):
            if is_hi:
                return (
                    "### 🌦️ मौसम एवं छिड़काव विंडो दिशानिर्देश\n\n"
                    "* **हवा की गति**: हमेशा हवा की गति **15 किमी/घंटा से कम** होने पर ही स्प्रे करें। तेज हवा में 40%+ दवा उड़कर बर्बाद हो जाती है।\n"
                    "* **बारिश की संभावना**: दवा छिड़कने के बाद कम से कम **4 से 6 घंटे** बारिश नहीं होनी चाहिए ताकि दवा पत्तों पर चिपक सके।\n"
                    "* **तापमान**: छिड़काव के लिए सर्वोत्तम तापमान **18°C से 30°C** है। दोपहर की तेज धूप (>32°C) में पत्तियां झुलस सकती हैं, इसलिए सुबह 6:00 से 9:00 बजे या शाम को ही स्प्रे करें।"
                )
            return (
                "### 🌦️ Weather & Spraying Safety Guidelines\n\n"
                "* **Wind Speed Rule**: Only spray when wind speeds are below **15 km/h**. Higher winds cause spray drift onto non-target crops and waste over 40% of active ingredients.\n"
                "* **Rainfast Window**: Ensure no rainfall is forecast for at least **4 to 6 hours** post-application so systemic or contact fungicides adhere firmly.\n"
                "* **Optimal Temperature**: Apply between **18°C and 30°C**. Avoid spraying during peak afternoon heat (> 32°C) to prevent foliar chemical scorch. Early morning (6:00–9:00 AM) or late afternoon is ideal."
            )

        # 4. Soil Health, Preparation & Fertilizers
        if any(w in q for w in ["soil", "fertilizer", "npk", "urea", "compost", "dung", "manure", "मिट्टी", "खाद", "यूरिया"]):
            if is_hi:
                return (
                    "### 🌾 मिट्टी की उर्वरता एवं पोषक तत्व प्रबंधन\n\n"
                    "1. **जैविक सुधार**: बुवाई से 3-4 सप्ताह पहले प्रति एकड़ 4-5 टन अच्छी सड़ी हुई गोबर की खाद या 2 टन वर्मीकम्पोस्ट मिलाएं।\n"
                    "2. **संतुलित NPK**: मिट्टी परीक्षण के अनुसार ही नाइट्रोजन, फास्फोरस और पोटाश का उपयोग करें (सामान्य अनुपात 4:2:1)।\n"
                    "3. **जीवामृत प्रयोग**: हर 15-20 दिनों में सिंचाई के पानी के साथ 200 लीटर प्रति एकड़ जीवामृत देने से मिट्टी के सूक्ष्मजीव सक्रिय रहते हैं।\n"
                    "4. **पीएच (pH) स्तर**: अधिकांश फसलों के लिए 6.0 से 7.5 का pH सर्वोत्तम होता है। अधिक अम्लीय मिट्टी में चूना और क्षारीय मिट्टी में जिप्सम का प्रयोग करें।"
                )
            return (
                "### 🌾 Soil Fertility & Nutrient Management Best Practices\n\n"
                "1. **Organic Conditioning**: Incorporate 4–5 tonnes of well-rotted FYM (Farm Yard Manure) or 2 tonnes of vermicompost per acre 3 weeks before sowing to improve aeration and water retention.\n"
                "2. **Balanced NPK Nutrition**: Avoid excessive urea (Nitrogen), which creates succulent foliage prone to fungal spore penetration. Maintain balanced 4:2:1 NPK ratio based on soil test results.\n"
                "3. **Bio-Inoculants**: Seed treatment with *Rhizobium* (for legumes) or *Azotobacter* / *PSB* (for cereals) cuts synthetic fertilizer costs by 20–25%.\n"
                "4. **Soil pH Management**: Ideal pH for most crops is 6.0–7.2. Apply agricultural lime for soils below pH 5.5, or gypsum for sodic/alkaline soils above pH 8.2."
            )

        # 5. Smart Irrigation & Water Management
        if any(w in q for w in ["irrigation", "water", "drip", "moisture", "dry", "wilting", "सिंचाई", "पानी", "ड्रिप"]):
            if is_hi:
                return (
                    "### 💧 स्मार्ट सिंचाई एवं जल संरक्षण\n\n"
                    "* **ड्रिप सिंचाई**: फ्लड सिंचाई की तुलना में ड्रिप से 40-60% पानी की बचत होती है और पत्तियों पर पानी न पड़ने से फफूंद नहीं फैलती।\n"
                    "* **सिंचाई का समय**: हमेशा सुबह के समय पानी दें ताकि दोपहर तक वाष्पीकरण कम हो और जड़ों को पर्याप्त नमी मिले।\n"
                    "* **बारिश की चेतावनी**: यदि अगले 24-48 घंटों में बारिश का पूर्वानुमान है, तो सिंचाई रोक दें ताकि जलभराव और पोषक तत्वों का बहाव रोका जा सके।"
                )
            return (
                "### 💧 Smart Irrigation & Water Conservation\n\n"
                "* **Drip Precision**: Drip lines conserve 40–60% water compared to furrow flooding and keep foliage dry, directly cutting foliar fungal infection rates.\n"
                "* **Watering Time**: Irrigate early in the morning so root zones absorb moisture before peak midday heat.\n"
                "* **Rain Forecast Interlock**: If the Smart Advisory weather tab indicates >= 5mm rainfall within 24–48 hours, postpone irrigation to prevent root hypoxia and nutrient leaching."
            )

        # 6. Disease Spread & Quarantine Containment
        if any(w in q for w in ["spread", "contagious", "neighbor", "other plant", "quarantine", "फैल", "संक्रमण"]):
            d_name = d or "plant diseases"
            if is_hi:
                return (
                    f"### 🛡️ संक्रमण रोकने के उपाय ({d_name})\n\n"
                    "1. **रोगग्रस्त पत्तियों की छंटाई**: संक्रमित पत्तियों को तुरंत काटकर प्लास्टिक बैग में इकट्ठा करें और खेत से दूर गड्ढे में दबाएं या जला दें।\n"
                    "2. **औजारों का निसंक्रमण**: छंटाई के बाद कैंची/कटर को 70% अल्कोहल या डेटॉल से साफ करें।\n"
                    "3. **ड्रिप सिंचाई अपनाएं**: फव्वारे या ऊपर से पानी देने से फफूंद के बीजाणु (spores) छींटों के साथ दूसरे पौधों पर फैलते हैं।\n"
                    "4. **पड़ोसी पौधों की सुरक्षा**: 5 मीटर के दायरे में स्थित स्वस्थ पौधों पर सुरक्षात्मक नीम के तेल का हल्का स्प्रे करें।"
                )
            return (
                f"### 🛡️ Disease Containment Protocol ({d_name})\n\n"
                "1. **Sanitation Pruning**: Remove visibly spotted or blighted lower foliage using sanitized shears. Place in a bag immediately—never throw infected leaves onto farm pathways.\n"
                "2. **Tool Disinfection**: Wipe secateurs with 70% isopropyl alcohol or bleach solution between crop rows to eliminate mechanical transmission.\n"
                "3. **Stop Overhead Sprinkling**: Rain-splash and overhead sprinklers are the primary vector for fungal and bacterial dissemination. Switch to sub-canopy drip watering.\n"
                "4. **Protective Perimeter**: Apply a preventative foliar spray of organic bio-fungicide (Trichoderma or Neem 5ml/L) to adjacent healthy plants within a 5-meter radius."
            )

        # 7. Food Safety & Harvest Pre-Harvest Interval (PHI)
        if any(w in q for w in ["eat", "fruit", "harvest", "edible", "food", "safe", "consumption", "खाना", "फल", "उपभोग"]):
            c_name = c if c != "Crop" else "the crop"
            if is_hi:
                return (
                    f"### 🍎 फल सुरक्षा एवं कटाई (हार्वेस्ट) दिशानिर्देश ({c_name})\n\n"
                    "* **स्वस्थ फल**: जिन फलों पर दाग या सड़न नहीं है, वे अच्छी तरह धोने के बाद खाने के लिए सुरक्षित हैं।\n"
                    "* **रासायनिक प्रतीक्षा अवधि (PHI)**: यदि रासायनिक कवकनाशी का छिड़काव किया है, तो फल तोड़ने से पहले कम से कम **7 से 14 दिन** का अनिवार्य इंतजार करें।\n"
                    "* **संक्रमित फल**: सड़े हुए या भूरे धब्बों वाले फलों को नष्ट कर दें, उनका उपभोग न करें।"
                )
            return (
                f"### 🍎 Food Safety & Harvest Guidelines ({c_name})\n\n"
                "* **Asymptomatic Produce**: Fruits or vegetables free from necrotic lesions, spots, or soft rot are safe for consumption after washing thoroughly under running water.\n"
                "* **Mandatory Pre-Harvest Interval (PHI)**: If synthetic chemical fungicides (e.g. Mancozeb, Hexaconazole) were applied, you MUST observe a strict **7 to 14 day waiting period** before harvesting.\n"
                "* **Blighted / Spotted Fruit**: Discard fruits showing sunken brown rings or soft rot, as microbial enzymes alter fruit sugars and can produce harmful mycotoxins."
            )

        # 8. Specific Disease Diagnosis Cure (when disease context is present)
        if d:
            meta = CLASS_METADATA.get(d, {})
            org = meta.get("organic_remedy", "Cold-pressed Neem oil (10,000 PPM) @ 5 ml/L + Trichoderma viride")
            chem = meta.get("chemical_remedy", "Copper Oxychloride 50% WP @ 2.5 g/L water")
            rec = meta.get("recovery_rate", "85-90%")
            if is_hi:
                return (
                    f"### 💊 **{d}** ({c}) का सम्पूर्ण उपचार प्लान\n\n"
                    f"* **🌱 जैविक प्रथम उपचार**: {org}\n"
                    f"* **🧪 लक्षित रासायनिक विकल्प**: {chem}\n"
                    f"* **⏱️ सुधार की संभावना**: समय पर उपचार से **{rec}** सुधार की उम्मीद है।\n"
                    f"* **खेत की देखभाल**: रोगग्रस्त पत्तों को हटा दें और खेत में हवा का आवागमन बनाए रखें।"
                )
            return (
                f"### 💊 Tailored Recovery Plan for **{d}** on **{c}**\n\n"
                f"* **🌱 Recommended Organic Treatment**: {org}.\n"
                f"* **🧪 Target Chemical Option**: {chem}.\n"
                f"* **⏱️ Prognosis & Recovery**: {rec} recovery expected if foliar treatment is applied within 48 hours.\n"
                f"* **Immediate Cultural Care**: Prune lower necrotic leaves, maintain root-level drip irrigation, and avoid handling foliage when wet."
            )

        # 9. General Open-Ended Guidance Fallback
        if is_hi:
            return (
                "### 🌿 एग्रीस्मार्ट एआई (AgriSmart AI) कृषि सहायता\n\n"
                "मैं आपकी फसल की पूरी देखभाल में मदद करने के लिए तैयार हूँ:\n\n"
                "* **पत्ती की जांच**: होम स्क्रीन पर अपनी फसल की पत्ती की तस्वीर अपलोड करें।\n"
                "* **दवा की सही मात्रा**: 'स्मार्ट एडवाइजरी' टैब में जाकर अपनी जमीन के अनुसार स्प्रे टैंक की मात्रा निकालें।\n"
                "* **सिंचाई योजना**: अपनी मिट्टी के लिए सटीक पानी की मात्रा जानें।\n\n"
                "कृपया अपना सवाल पूछें, जैसे: *'टमाटर में ब्लाइट कैसे रोकें?'* या *'छिड़काव का सही समय क्या है?'*"
            )

        return (
            "### 🌿 AgriSmart AI Agronomic Assistant\n\n"
            "I'm ready to assist with your field management and crop protection:\n\n"
            "* **Analyze a Leaf**: Upload a clear leaf photo on the dashboard for instant disease identification.\n"
            "* **Calculate Spray Tanks**: Use the Smart Advisory tab to calculate exact dilution ratios for knapsack sprayers.\n"
            "* **Weather & Irrigation**: View live rain windows and automated FAO-56 irrigation schedules.\n\n"
            "Feel free to ask me anything, such as:\n"
            "- *'What are the best crops for sandy loam soil?'*\n"
            "- *'How to make an organic bio-fungicide at home?'*\n"
            "- *'When is the safest time to spray today?'*"
        )

    def chat_followup(
        self,
        message: str,
        disease_name: Optional[str],
        crop: Optional[str],
        conversation_history: list,
        language: str = "en"
    ) -> dict:
        """
        Multi-turn chatbot: answers farmer follow-up questions about their crop or general agronomy.
        Engages naturally using Groq (LLaMA 3.3 70B) when online, or the intelligent local agronomist engine when offline.
        """
        clean_disease = disease_name if disease_name and disease_name.lower() not in ["none", "unknown", "general farm health", ""] else None
        clean_crop = crop if crop and crop.lower() not in ["none", "unknown", "field crops", ""] else None

        # Offline / Local fallback path
        if not self.client:
            reply_text = self._generate_local_chat_reply(
                message=message,
                disease_name=clean_disease,
                crop=clean_crop,
                language=language
            )
            return {
                "reply": reply_text,
                "conversation_history": conversation_history + [
                    {"role": "user", "content": message},
                    {"role": "model", "content": reply_text}
                ]
            }

        full_lang = self.LANG_MAP.get(language, "English")
        if clean_disease:
            context_snippet = f"The farmer's {clean_crop or 'crop'} plant has been diagnosed with '{clean_disease}'."
        else:
            context_snippet = (
                f"The farmer is managing {clean_crop or 'their fields'} and having a general farming inquiry "
                "(soil health, crop rotation, organic remedies, weather protection, or precision irrigation)."
            )

        system_context = (
            f"You are AgriBot, an empathetic, expert agricultural Web AI assistant built into AgriSmart AI. "
            f"{context_snippet} "
            f"You can converse naturally, greet the farmer warmly, answer open-ended agricultural science questions, "
            f"and provide actionable plant protection and irrigation advice. "
            f"Format your output cleanly using markdown headings and bullet points. "
            f"CRITICAL INSTRUCTION: You MUST respond in {full_lang}. Do not reply in English unless {full_lang} is English."
        )

        messages = [
            {"role": "system", "content": system_context},
            {"role": "assistant", "content": "Hello! I'm AgriBot AI, ready to help you with crop care, disease recovery, and smart farm management."}
        ]

        for turn in conversation_history:
            role = "assistant" if turn.get("role") == "model" else turn.get("role", "user")
            messages.append({"role": role, "content": turn.get("content", "")})

        messages.append({"role": "user", "content": message})

        reply_text = None
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=700,
                top_p=1,
            )
            reply_text = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API Error in chat_followup: {e}")

        # If online API call failed, seamlessly fall back to local agronomist dialogue engine
        if not reply_text:
            reply_text = self._generate_local_chat_reply(
                message=message,
                disease_name=clean_disease,
                crop=clean_crop,
                language=language
            )

        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "model", "content": reply_text}
        ]

        return {"reply": reply_text, "conversation_history": updated_history}


# Instantiate the service singleton with the old name so we don't have to rewrite imports
gemini_advisor = GroqAdvisorService()
