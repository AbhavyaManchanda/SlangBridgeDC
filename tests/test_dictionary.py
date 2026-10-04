"""
Unit tests for DictionaryService.
"""
from backend.dictionary_service import dictionary_service
from backend.models import AddTermRequest


def test_dictionary_loaded():
    terms = dictionary_service.get_all_terms()
    assert len(terms) >= 20, f"Expected at least 20 terms, got {len(terms)}"
    categories = dictionary_service.get_categories()
    assert len(categories) >= 5, f"Expected at least 5 categories, got {len(categories)}"


def test_term_lookup():
    jc = dictionary_service.get_term_by_name("JC")
    assert jc is not None
    assert "multiplex" in jc.meaning.lower() or "multiplex" in jc.campus_context.lower()

    macha = dictionary_service.get_term_by_name("Macha")
    assert macha is not None
    assert "bro" in macha.meaning.lower() or "brother" in macha.meaning.lower()


def test_term_matching_in_sentence():
    sentence = "Macha GEC punch maarke direct JC mein milte hain, scene sorted hai."
    matched = dictionary_service.match_terms_in_text(sentence)
    matched_names = [t.term for t in matched]

    assert "Macha" in matched_names
    assert "JC" in matched_names
    assert "Scene Sorted Hai" in matched_names or "Biometric Punch / 9:15" in matched_names or "GEC 1 & GEC 2" in matched_names


def test_grounding_prompt_builder():
    matched = dictionary_service.match_terms_in_text("Pani paali aliya, re-FA pakka!")
    prompt_context = dictionary_service.build_grounding_prompt_context(matched)
    assert "INFOSYS MYSORE" in prompt_context
    assert len(prompt_context) > 50


def test_search_terms():
    results = dictionary_service.search_terms("dosa")
    assert len(results) >= 1
    assert any("JC" in r.term or "Fiesta" in r.term for r in results)
