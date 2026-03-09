from multi_agent_research_assistant.tools.text import extract_numeric_facts, top_relevant_sentences


def test_extract_numeric_facts_returns_numbered_sentences():
    text = (
        "European AI startup funding reached EUR 2.4 billion in 2025. "
        "Growth was 35% year over year according to market trackers. "
        "Founders highlighted talent shortages across major hubs."
    )
    facts = extract_numeric_facts(text, limit=3)
    assert len(facts) == 2
    assert "2.4 billion" in facts[0].lower()
    assert "35%" in facts[1]


def test_top_relevant_sentences_prioritizes_keywords():
    text = (
        "Retail adoption is increasing in Europe. "
        "Startup funding accelerated after policy updates. "
        "New venture capital firms entered the AI market."
    )
    selected = top_relevant_sentences(text, keywords=["startup", "funding", "venture"], limit=2)
    assert len(selected) == 2
    assert "funding" in selected[0].lower() or "venture" in selected[0].lower()

