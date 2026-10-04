"""
Local AI Engine: Integration with Ollama using the official Python client.
Provides 100% offline, local-first inference grounded with Infosys Mysore campus dictionary.
Includes an intelligent offline heuristic synthesizer when the Ollama daemon is offline.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import ollama
from backend.config import DEFAULT_OLLAMA_MODEL, FALLBACK_OLLAMA_MODELS, OLLAMA_HOST
from backend.dictionary_service import dictionary_service
from backend.models import DictionaryTerm, TranslationBreakdown

logger = logging.getLogger("ollama_service")


class OllamaService:
    def __init__(self, host: str = OLLAMA_HOST, default_model: str = DEFAULT_OLLAMA_MODEL):
        self.host = host
        self.default_model = default_model
        self.client = ollama.Client(host=self.host)

    def check_connection(self) -> Tuple[bool, List[str]]:
        """
        Pings local Ollama daemon and fetches the list of pulled models.
        Returns (is_connected, list_of_models).
        """
        try:
            response = self.client.list()
            # response in ollama v0.6+ is an object or dict with 'models'
            models: List[str] = []
            if hasattr(response, "models"):
                for m in response.models:
                    name = getattr(m, "model", None) or getattr(m, "name", "")
                    if name:
                        models.append(name.split(":")[0])
            elif isinstance(response, dict) and "models" in response:
                for m in response["models"]:
                    name = m.get("model") or m.get("name")
                    if name:
                        models.append(name.split(":")[0])
            # Remove duplicates preserving order
            unique_models = list(dict.fromkeys(models))
            return True, unique_models
        except Exception as e:
            logger.debug("Ollama ping failed at %s: %s", self.host, e)
            return False, []

    def get_preferred_model(self, requested_model: Optional[str] = None) -> Tuple[str, bool]:
        """
        Resolves the model to use.
        Returns (model_name, is_available_in_ollama).
        """
        is_connected, available_models = self.check_connection()
        if not is_connected:
            return requested_model or self.default_model, False

        candidate = requested_model or self.default_model
        # Check if candidate or candidate:latest matches
        for m in available_models:
            if m.lower() == candidate.lower() or m.lower().startswith(candidate.lower()):
                return m, True

        # Check fallback models
        for fallback in FALLBACK_OLLAMA_MODELS:
            for m in available_models:
                if m.lower() == fallback.lower() or m.lower().startswith(fallback.lower()):
                    return m, True

        # If any model is installed, use the first available one
        if available_models:
            return available_models[0], True

        return candidate, False

    def build_system_prompt(self, matched_terms: List[DictionaryTerm], context_hint: Optional[str] = None) -> str:
        grounding_data = dictionary_service.build_grounding_prompt_context(matched_terms)
        hint_text = f"\nUSER CONTEXT HINT: {context_hint}" if context_hint else ""

        return (
            "You are the 'DC Roommate Slang Bridge', an expert cultural translator and linguistic mentor "
            "for fresh engineering graduates training at the 337-acre Infosys Development Centre (DC) in Mysore, India.\n"
            "Roommates come from across India (Delhi, Bangalore, Kerala, Tamil Nadu, Andhra, Hyderabad, Mumbai, etc.) "
            "and live together in Employee Care Centre (ECC) hostels, study in GEC 1 & 2, eat at JC multiplex or Oasis/Fiesta messes, "
            "and navigate high-stakes Foundation Program (FP/FA) assessments.\n\n"
            f"{grounding_data}{hint_text}\n\n"
            "TASK: Analyze the user's input phrase, regional slang, or voice note transcript, and return a structured JSON object.\n"
            "You MUST output valid JSON matching this exact structure:\n"
            "{\n"
            '  "direct_meaning": "Clear, concise translation or explanation of the phrase.",\n'
            '  "vibe_and_tone": "The attitude, mood, urgency, stress level, or banter vibe (e.g. panic, cheeky, affectionate, passive-aggressive roommate friction).",\n'
            '  "on_campus_context": "Deep Infosys Mysore context: explains what GEC, JC, ECC, FA cutoff (65%), biometric punch, cycles, or messes mean here.",\n'
            '  "cultural_nuances": ["Bullet point 1 highlighting linguistic origin (Kannada, Malayalam, Hindi, Tamil, Telugu, etc.)", "Bullet point 2 regarding roommate dynamics"],\n'
            '  "roommate_reply_suggestion": "A witty, authentic, campus-appropriate reply the user can send back to their roommate!"\n'
            "}\n"
            "Do not output markdown codeblocks. Output only pure JSON."
        )

    def translate(
        self,
        text: str,
        model_name: Optional[str] = None,
        context_hint: Optional[str] = None,
    ) -> TranslationBreakdown:
        """
        Translates and breaks down slang.
        Tries Ollama first; if Ollama daemon is offline or model call fails,
        gracefully falls back to the local grounded heuristic engine.
        """
        matched_terms = dictionary_service.match_terms_in_text(text)
        term_names = [t.term for t in matched_terms]

        is_connected, available_models = self.check_connection()
        resolved_model, is_available = self.get_preferred_model(model_name)

        if is_connected and is_available:
            try:
                system_prompt = self.build_system_prompt(matched_terms, context_hint)
                user_prompt = f"Analyze this Infosys Mysore roommate message/slang:\n\"{text}\""

                logger.info("Calling local Ollama with model %s for text: %s", resolved_model, text)
                response = self.client.chat(
                    model=resolved_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    format="json",
                    options={"temperature": 0.2},
                )

                content = response.message.content if hasattr(response, "message") else response["message"]["content"]
                parsed = self._extract_json(content)

                if parsed and "direct_meaning" in parsed and "vibe_and_tone" in parsed:
                    direct_meaning = parsed.get("direct_meaning", "").strip()
                    vibe_and_tone = parsed.get("vibe_and_tone", "").strip()
                    on_campus_context = parsed.get("on_campus_context", "").strip()
                    cultural_nuances = parsed.get("cultural_nuances", [])
                    reply_suggestion = parsed.get("roommate_reply_suggestion")
                    model_label = f"ollama:{resolved_model}"

                    # Clean Markdown formatting without HTML div tags
                    terms_badges = " ".join([f"`{t}`" for t in term_names]) if term_names else "`Conversational Campus Lingo`"
                    nuances_md = "\n".join([f"- {item}" for item in cultural_nuances]) if cultural_nuances else "- Authentic campus cross-cultural dialogue"
                    reply_md = f"#### 💬 Suggested Roommate Response\n> *\"{reply_suggestion}\"*\n\n" if reply_suggestion else ""

                    formatted_markdown = (
                        f"### 📘 Direct Meaning / Translation\n"
                        f"> {direct_meaning}\n\n"
                        f"### 🎭 The Vibe & Tone\n"
                        f"**{vibe_and_tone}**\n\n"
                        f"### 🏛️ On-Campus Context (JC, GEC, or Hostel Life)\n"
                        f"{on_campus_context}\n\n"
                        f"---\n\n"
                        f"{reply_md}"
                        f"#### 🌐 Cultural & Linguistic Nuances\n"
                        f"{nuances_md}\n\n"
                        f"#### 🏷️ Detected Campus Terms\n"
                        f"{terms_badges}\n\n"
                        f"---\n"
                        f"*⚙️ **Engine:** {model_label}  |  🛡️ **Grounding:** Local Campus Dictionary  |  🔒 **100% Offline & Private***\n"
                    )

                    return TranslationBreakdown(
                        source_text=text,
                        direct_meaning=direct_meaning,
                        vibe_and_tone=vibe_and_tone,
                        on_campus_context=on_campus_context,
                        cultural_nuances=cultural_nuances,
                        matched_terms=term_names,
                        model_used=model_label,
                        is_offline_grounded=True,
                        roommate_reply_suggestion=reply_suggestion,
                        formatted_markdown=formatted_markdown,
                    )
            except Exception as e:
                logger.warning("Ollama chat generation failed: %s. Falling back to local offline heuristic.", e)

        # Fallback offline heuristic synthesizer
        return self._synthesize_offline_breakdown(
            text=text,
            matched_terms=matched_terms,
            model_info=f"Infosys-Mysore-Heuristic-Offline-Engine (Local Grounding, Ollama offline/standby)",
            context_hint=context_hint,
        )

    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Safely parses JSON even if wrapped in markdown formatting."""
        if not content:
            return None
        clean = content.strip()
        # Remove markdown code fences if present
        clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.MULTILINE)
        clean = re.sub(r"\s*```$", "", clean, flags=re.MULTILINE).strip()
        try:
            return json.loads(clean)
        except Exception:
            # Try finding first { and last }
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(clean[start : end + 1])
                except Exception:
                    pass
        return None

    def _synthesize_offline_breakdown(
        self,
        text: str,
        matched_terms: List[DictionaryTerm],
        model_info: str,
        context_hint: Optional[str] = None,
    ) -> TranslationBreakdown:
        """
        Deterministic, culturally grounded synthesizer for 100% offline reliability.
        Ensures the application works instantly even without Ollama installed or running.
        """
        text_lower = text.lower()
        matched_names = [t.term for t in matched_terms]

        # 1. Determine Direct Meaning
        meanings = []
        for t in matched_terms:
            meanings.append(f"'{t.term}': {t.meaning}")

        if meanings:
            direct_meaning = " | ".join(meanings)
        else:
            direct_meaning = (
                f"Conversational campus phrase: '{text}'. "
                "Commonly used among trainees during hostel discussions and training sessions."
            )

        # 2. Determine Vibe and Tone
        vibes = [t.vibe for t in matched_terms if t.vibe]
        if "contra" in text_lower or "pani paali" in text_lower or "kat gaya" in text_lower or "re-fa" in text_lower:
            vibe_and_tone = "🚨 High-stress alert / impending doom / humorous panic after an unexpected exam or lab setback."
        elif "sorted" in text_lower or "bombaat" in text_lower or "phod diya" in text_lower or "set aayi" in text_lower:
            vibe_and_tone = "🎉 Triumphant, relaxed celebration / post-assessment relief."
        elif "adjust" in text_lower or "macha" in text_lower or "guru" in text_lower or "aliya" in text_lower:
            vibe_and_tone = "🤝 Warm, fraternal roommate negotiation / casual day-to-day hostel bonding."
        elif vibes:
            vibe_and_tone = f"🎯 {', '.join(vibes[:2])}"
        else:
            vibe_and_tone = "💬 Casual everyday hostel banter / pragmatic trainee communication."

        # 3. Determine On-Campus Context (JC, GEC, ECC, FA, etc.)
        contexts = [t.campus_context for t in matched_terms if t.campus_context]
        if contexts:
            on_campus_context = " ".join(contexts[:2])
        else:
            on_campus_context = (
                "At Infosys Mysore DC, fresh trainees stay in ECC hostels and commute by campus cycle "
                "to GEC 1 & 2 for technical training. Roommates often plan evening meetups at JC multiplex "
                "or discuss assessments and educator feedback."
            )

        # 4. Cultural Nuances
        cultural_nuances = []
        languages_detected = set()
        for t in matched_terms:
            languages_detected.update(t.languages)

        if languages_detected:
            cultural_nuances.append(
                f"Linguistic crossover detected: {', '.join(sorted(languages_detected))} mixed with corporate trainee lingo."
            )
        else:
            cultural_nuances.append(
                "Cross-cultural Mysore DC communication: trainees quickly adopt terms from neighboring roommates."
            )

        cultural_nuances.append(
            "ECC Roommate Dynamics: Living in twin-sharing rooms brings together North, South, East, and West India cultures."
        )

        # 5. Suggested Roommate Reply
        if "jc" in text_lower or "dosa" in text_lower or "food" in text_lower:
            suggested_reply = "Done macha, 6:00 PM outside JC food court near the fountain. Butter masala dosa on you!"
        elif "fa" in text_lower or "exam" in text_lower or "test" in text_lower:
            suggested_reply = "Chill maar, we will group-study in ECC after dinner. 65% is all we need to clear."
        elif "cycle" in text_lower:
            suggested_reply = "Bhai I saw your cycle near GEC 2 gate. Grab it before the 9:15 biometric rush!"
        elif "adjust" in text_lower:
            suggested_reply = "AC set to 23°C and fan on medium, deal done aliya!"
        else:
            suggested_reply = "Scene sorted hai guru, let's meet at Oasis after the evening soft skills class!"

        # Construct clean Markdown formatting without HTML div tags
        terms_badges = " ".join([f"`{name}`" for name in matched_names]) if matched_names else "`Conversational Campus Lingo`"
        nuances_bullets = "\n".join([f"- {item}" for item in cultural_nuances])
        
        formatted_markdown = (
            f"### 📘 Direct Meaning / Translation\n"
            f"> {direct_meaning}\n\n"
            f"### 🎭 The Vibe & Tone\n"
            f"**{vibe_and_tone}**\n\n"
            f"### 🏛️ On-Campus Context (JC, GEC, or Hostel Life)\n"
            f"{on_campus_context}\n\n"
            f"---\n\n"
            f"#### 💬 Suggested Roommate Response\n"
            f"> *\"{suggested_reply}\"*\n\n"
            f"#### 🌐 Cultural & Linguistic Nuances\n"
            f"{nuances_bullets}\n\n"
            f"#### 🏷️ Detected Campus Terms\n"
            f"{terms_badges}\n\n"
            f"---\n"
            f"*⚙️ **Engine:** {model_info}  |  🛡️ **Grounding:** Local Campus Dictionary  |  🔒 **100% Offline & Private***\n"
        )

        return TranslationBreakdown(
            source_text=text,
            direct_meaning=direct_meaning,
            vibe_and_tone=vibe_and_tone,
            on_campus_context=on_campus_context,
            cultural_nuances=cultural_nuances,
            matched_terms=matched_names,
            model_used=model_info,
            is_offline_grounded=True,
            roommate_reply_suggestion=suggested_reply,
            formatted_markdown=formatted_markdown,
        )


# Global singleton instance
ollama_service = OllamaService()
