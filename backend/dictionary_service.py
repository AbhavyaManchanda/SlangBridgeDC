"""
Dictionary Service: Manages Infosys Mysore Campus Context and Slang Lexicon.
Provides fast in-memory indexing, search, term matching, and grounding prompt generation.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.config import DICTIONARY_PATH
from backend.models import AddTermRequest, DictionaryTerm

logger = logging.getLogger("dictionary_service")


class DictionaryService:
    def __init__(self, dictionary_path: Path = DICTIONARY_PATH):
        self.path = dictionary_path
        self._data: Dict[str, Any] = {}
        self._terms_cache: List[DictionaryTerm] = []
        self._categories_cache: List[Dict[str, str]] = []
        self.load_dictionary()

    def load_dictionary(self) -> None:
        """Loads or reloads the campus dictionary from disk."""
        if not self.path.exists():
            logger.warning("Dictionary file not found at %s. Creating empty shell.", self.path)
            self._data = {
                "campus_info": {"campus_name": "Infosys Mysore DC"},
                "categories": [],
                "terms": [],
            }
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)

            self._categories_cache = self._data.get("categories", [])
            raw_terms = self._data.get("terms", [])
            self._terms_cache = [DictionaryTerm(**term) for term in raw_terms]
            logger.info("Loaded %d campus terms across %d categories from %s",
                        len(self._terms_cache), len(self._categories_cache), self.path)
        except Exception as e:
            logger.error("Failed to parse dictionary JSON: %s", e)
            self._terms_cache = []

    def get_all_terms(self) -> List[DictionaryTerm]:
        return self._terms_cache

    def get_categories(self) -> List[Dict[str, str]]:
        return self._categories_cache

    def get_term_by_name(self, name: str) -> Optional[DictionaryTerm]:
        name_lower = name.strip().lower()
        for t in self._terms_cache:
            if t.term.lower() == name_lower:
                return t
            if any(alias.lower() == name_lower for alias in t.aliases):
                return t
        return None

    def search_terms(self, query: str, category_id: Optional[str] = None) -> List[DictionaryTerm]:
        """Search dictionary with keyword matching and optional category filter."""
        q = query.strip().lower()
        results: List[DictionaryTerm] = []

        for term in self._terms_cache:
            if category_id and category_id.lower() != "all" and term.category != category_id:
                continue

            if not q:
                results.append(term)
                continue

            # Check matches across term, aliases, keywords, meaning, and campus_context
            if (
                q in term.term.lower()
                or any(q in alias.lower() for alias in term.aliases)
                or any(q in kw.lower() for kw in term.keywords)
                or q in term.meaning.lower()
                or q in term.campus_context.lower()
            ):
                results.append(term)

        return results

    def match_terms_in_text(self, text: str) -> List[DictionaryTerm]:
        """
        Extracts all dictionary terms that appear in the input sentence.
        Uses boundary-aware matching and alias detection.
        Sorts matches by term length descending to favor longer phrases (e.g. 'Scene Contra' over 'Scene').
        """
        text_lower = f" {text.lower()} "
        # Replace punctuation with spaces for clean tokenization while preserving internal hyphens
        cleaned_text = re.sub(r"[^\w\s\-]", " ", text_lower)

        matched: List[Tuple[int, DictionaryTerm]] = []
        seen_terms = set()

        for term in self._terms_cache:
            # Candidate phrases: term itself plus all aliases plus key phrases
            candidates = [term.term] + term.aliases + [kw for kw in term.keywords if len(kw) > 2]
            best_len = 0
            for candidate in candidates:
                cand_clean = candidate.strip().lower()
                if not cand_clean:
                    continue

                # Pattern matching: either word boundary or exact token presence
                pattern = r"(?:\b|_)" + re.escape(cand_clean) + r"(?:\b|_)"
                if re.search(pattern, cleaned_text):
                    best_len = max(best_len, len(cand_clean))

            if best_len > 0 and term.term not in seen_terms:
                seen_terms.add(term.term)
                matched.append((best_len, term))

        # Sort by match length descending so multi-word terms take precedence
        matched.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched]

    def build_grounding_prompt_context(self, matched_terms: List[DictionaryTerm]) -> str:
        """
        Builds a concise, structured markdown grounding block to inject into the Ollama prompt.
        """
        if not matched_terms:
            # Fall back to high-level campus summary context
            return (
                "INFOSYS MYSORE DC CAMPUS CONTEXT:\n"
                "- Campus: 337-acre residential training campus in Mysuru, Karnataka.\n"
                "- GEC 1 & 2: Global Education Centre (academic training, assessments, biometric attendance before 9:15 AM).\n"
                "- JC: Multiplex hub, 3-screen cinema, bowling alley, food court.\n"
                "- ECC: Employee Care Centre (trainee hostel blocks).\n"
                "- FP & FA: Foundation Program and Focus Assessments (65% pass cutoff, Re-FA penalty).\n"
                "- Roommates: Fresh trainees from across India living in twin-sharing rooms.\n"
            )

        lines = [
            "INFOSYS MYSORE GROUNDED DICTIONARY CONTEXT FOR THIS INPUT:",
            "Use the following authentic campus definitions to explain the user's slang:",
        ]
        for t in matched_terms:
            lines.append(
                f"- Term: '{t.term}' (Category: {t.category}, Lang: {', '.join(t.languages)})\n"
                f"  Meaning: {t.meaning}\n"
                f"  Vibe: {t.vibe}\n"
                f"  Campus Context: {t.campus_context}"
            )
        return "\n".join(lines)

    def add_term(self, new_term: AddTermRequest) -> DictionaryTerm:
        """Adds a new term to the in-memory cache and persists to disk."""
        # Check if term already exists
        existing = self.get_term_by_name(new_term.term)
        if existing:
            raise ValueError(f"Term '{new_term.term}' already exists in the campus dictionary.")

        term_obj = DictionaryTerm(
            term=new_term.term.strip(),
            aliases=new_term.aliases or [],
            category=new_term.category.strip(),
            languages=new_term.languages or ["Campus Lingo"],
            meaning=new_term.meaning.strip(),
            vibe=new_term.vibe.strip(),
            campus_context=new_term.campus_context.strip(),
            example_usage=new_term.example_usage.strip(),
            keywords=[new_term.term.strip().lower()],
        )

        self._terms_cache.append(term_obj)
        self._persist_to_disk()
        return term_obj

    def _persist_to_disk(self) -> None:
        """Saves current dictionary state safely."""
        self._data["terms"] = [t.model_dump() for t in self._terms_cache]
        temp_path = self.path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        temp_path.replace(self.path)
        logger.info("Persisted updated dictionary (%d terms) to %s", len(self._terms_cache), self.path)


# Global singleton instance
dictionary_service = DictionaryService()
