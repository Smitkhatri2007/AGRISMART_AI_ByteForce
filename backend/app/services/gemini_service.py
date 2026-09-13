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

    def chat_followup(
        self,
        message: str,
        disease_name: str,
        crop: str,
        conversation_history: list,
        language: str = "en"
    ) -> dict:
        """
        Multi-turn chatbot: answers farmer follow-up questions about their diagnosed crop.
        Maintains conversation context using OpenAI's multi-turn message format for Groq.
        """
        if not self.client:
            reply_text = (
                f"I'm currently in offline mode. Based on the diagnosis of {disease_name} on your {crop}, "
                "I recommend consulting your local agriculture extension officer for detailed advice. "
                "Please add a GROQ_API_KEY to your .env file to enable the live AI chatbot."
            )
            return {
                "reply": reply_text,
                "conversation_history": conversation_history + [
                    {"role": "user", "content": message},
                    {"role": "model", "content": reply_text}
                ]
            }

        full_lang = self.LANG_MAP.get(language, "English")
        if disease_name and disease_name.lower() not in ["unknown", "none", ""]:
            context_snippet = f"The farmer's {crop} plant has been diagnosed with '{disease_name}'."
        else:
            context_snippet = f"The farmer is managing a {crop or 'field'} crop and inquiring about crop care, weather intelligence, and smart irrigation."

        system_context = (
            f"You are AgriBot, an expert and empathetic agricultural advisor built into AgriSmart AI. "
            f"{context_snippet} "
            f"You provide practical, actionable advice on plant health, chemical/organic treatment dosages, "
            f"weather protection, and smart irrigation scheduling. "
            f"Be warm, concise, and use simple language suitable for a farmer. "
            f"CRITICAL INSTRUCTION: You MUST respond in {full_lang}. Do not reply in English unless {full_lang} is English."
        )

        messages = [
            {"role": "system", "content": system_context},
            {"role": "assistant", "content": "Understood! I'm ready to help with crop care, weather intelligence, and irrigation advisory."}
        ]

        # In previous format, role was 'user'/'model'. Groq uses 'user'/'assistant'
        for turn in conversation_history:
            role = "assistant" if turn["role"] == "model" else turn["role"]
            messages.append({"role": role, "content": turn["content"]})

        messages.append({"role": "user", "content": message})

        reply_text = None
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_completion_tokens=600,
                top_p=1,
            )
            reply_text = completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API Error: {e}")

        if not reply_text:
            reply_text = (
                f"I'm having trouble connecting right now. For {disease_name} on {crop}, "
                "the most important thing is to act quickly — remove infected leaves and apply treatment as advised."
            )

        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "model", "content": reply_text}  # Keeping 'model' so frontend logic stays intact
        ]

        return {"reply": reply_text, "conversation_history": updated_history}


# Instantiate the service singleton with the old name so we don't have to rewrite imports
gemini_advisor = GroqAdvisorService()
