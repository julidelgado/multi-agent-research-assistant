from multi_agent_research_assistant.tools.search import normalize_search_url


def test_normalize_search_url_unwraps_duckduckgo_redirect():
    wrapped = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Finsight"
    assert normalize_search_url(wrapped) == "https://example.com/insight"


def test_normalize_search_url_unwraps_bing_redirect():
    wrapped = "https://www.bing.com/aclick?u=https%3A%2F%2Fexample.com%2Farticle"
    assert normalize_search_url(wrapped) == "https://example.com/article"


def test_normalize_search_url_rejects_non_http():
    assert normalize_search_url("mailto:test@example.com") == ""

