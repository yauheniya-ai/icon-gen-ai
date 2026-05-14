"""Tests for AI module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from icon_gen_ai.ai import is_ai_available, get_available_providers


def test_is_ai_available():
    """Test AI availability check."""
    result = is_ai_available()
    assert isinstance(result, bool)


def test_get_available_providers():
    """Test getting available providers."""
    providers = get_available_providers()
    assert isinstance(providers, list)
    # Should be empty if AI not installed, or contain provider names


@pytest.mark.skipif(not is_ai_available(), reason="AI features not installed")
def test_icon_assistant_import():
    """Test IconAssistant can be imported when AI is available."""
    from icon_gen_ai import IconAssistant

    assert IconAssistant is not None


def test_base_llm_provider():
    """Test base LLM provider classes."""
    from icon_gen_ai.ai.base import IconSuggestion, LLMResponse

    suggestion = IconSuggestion(
        icon_name="mdi:test", reason="Test reason", use_case="Testing", confidence=0.9
    )

    assert suggestion.icon_name == "mdi:test"
    assert suggestion.confidence == 0.9

    response = LLMResponse(
        suggestions=[suggestion],
        explanation="Test explanation",
        search_query="test query",
        tokens_used=100,
        provider="test",
    )

    assert len(response.suggestions) == 1
    assert response.tokens_used == 100


# -------------------- IconAssistant coverage tests --------------------

def test_icon_assistant_no_provider(tmp_path):
    """IconAssistant with no env vars has no provider."""
    from icon_gen_ai.ai.assistant import IconAssistant

    with patch.dict(os.environ, {}, clear=True):
        # Remove all known API keys
        for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "HUGGINGFACE_API_TOKEN"):
            os.environ.pop(key, None)
        assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
        assert assistant.provider is None
        assert assistant.is_available() is False


def test_icon_assistant_is_available_false():
    """is_available returns False when provider is None."""
    from icon_gen_ai.ai.assistant import IconAssistant

    assistant = IconAssistant.__new__(IconAssistant)
    assistant.provider = None
    assert assistant.is_available() is False


def test_icon_assistant_discover_icons_no_provider(tmp_path):
    """discover_icons raises RuntimeError when no provider is configured."""
    from icon_gen_ai.ai.assistant import IconAssistant

    # Pass provider=None explicitly; auto-detection doesn't matter here
    assistant = IconAssistant.__new__(IconAssistant)
    assistant.provider = None
    assistant.enable_caching = False
    assistant.cache_dir = tmp_path
    assistant.cache = {}
    with pytest.raises(RuntimeError, match="No LLM provider"):
        assistant.discover_icons("payment icons")


def test_icon_assistant_cache_key_without_context(tmp_path):
    """_get_cache_key returns a hex string for a plain query."""
    from icon_gen_ai.ai.assistant import IconAssistant

    assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
    key = assistant._get_cache_key("payment icons")
    assert isinstance(key, str)
    assert len(key) == 32  # MD5 hex length


def test_icon_assistant_cache_key_with_context(tmp_path):
    """_get_cache_key differs when context is provided."""
    from icon_gen_ai.ai.assistant import IconAssistant

    assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
    key_no_ctx = assistant._get_cache_key("icons")
    key_with_ctx = assistant._get_cache_key("icons", {"style": "modern"})
    assert key_no_ctx != key_with_ctx


def test_icon_assistant_clear_cache(tmp_path):
    """clear_cache empties the in-memory cache."""
    from icon_gen_ai.ai.assistant import IconAssistant
    from icon_gen_ai.ai.base import LLMResponse

    assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
    assistant.cache["dummy"] = MagicMock(spec=LLMResponse)
    assert "dummy" in assistant.cache
    assistant.clear_cache()
    assert len(assistant.cache) == 0


def test_icon_assistant_get_style_advice(tmp_path):
    """get_style_advice returns a dict."""
    from icon_gen_ai.ai.assistant import IconAssistant

    assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
    result = assistant.get_style_advice("modern")
    assert isinstance(result, dict)


def test_icon_assistant_save_and_load_cache(tmp_path):
    """Cache is persisted to disk and loaded back."""
    from icon_gen_ai.ai.assistant import IconAssistant
    from icon_gen_ai.ai.base import LLMResponse, IconSuggestion

    response = LLMResponse(
        suggestions=[
            IconSuggestion(
                icon_name="mdi:test", reason="r", use_case="u", confidence=1.0
            )
        ],
        explanation="e",
        search_query="q",
        tokens_used=10,
        provider="test",
    )

    assistant = IconAssistant(provider=None, cache_dir=str(tmp_path))
    key = assistant._get_cache_key("q")
    assistant._save_to_cache(key, response)

    # Load from a fresh assistant pointing to same dir
    assistant2 = IconAssistant(provider=None, cache_dir=str(tmp_path))
    loaded = assistant2._get_from_cache(key)
    assert loaded is not None
    assert loaded.suggestions[0].icon_name == "mdi:test"


def test_icon_assistant_discover_icons_with_mock_provider(tmp_path):
    """discover_icons calls provider.query and returns suggestions."""
    from icon_gen_ai.ai.assistant import IconAssistant
    from icon_gen_ai.ai.base import LLMResponse, IconSuggestion

    mock_provider = MagicMock()
    mock_provider.is_available.return_value = True
    mock_provider.get_provider_name.return_value = "mock"
    mock_provider.model = "mock-model"
    mock_provider.estimate_cost.return_value = 0.0
    mock_provider.query.return_value = LLMResponse(
        suggestions=[
            IconSuggestion(
                icon_name="mdi:credit-card",
                reason="Payment icon",
                use_case="Checkout",
                confidence=0.95,
            )
        ],
        explanation="Found payment icons",
        search_query="payment icons",
        tokens_used=50,
        provider="mock",
    )

    assistant = IconAssistant(
        provider=mock_provider, cache_dir=str(tmp_path), enable_caching=False
    )
    result = assistant.discover_icons("payment icons", use_cache=False)
    assert len(result.suggestions) == 1
    assert result.suggestions[0].icon_name == "mdi:credit-card"


def test_icon_assistant_uses_cache_on_second_call(tmp_path):
    """Second call with same query uses the cache, not the provider."""
    from icon_gen_ai.ai.assistant import IconAssistant
    from icon_gen_ai.ai.base import LLMResponse, IconSuggestion

    mock_provider = MagicMock()
    mock_provider.is_available.return_value = True
    mock_provider.get_provider_name.return_value = "mock"
    mock_provider.model = "mock-model"
    mock_provider.estimate_cost.return_value = 0.0
    mock_provider.query.return_value = LLMResponse(
        suggestions=[
            IconSuggestion(icon_name="mdi:home", reason="r", use_case="u")
        ],
        explanation="",
        search_query="home",
        tokens_used=5,
        provider="mock",
    )

    assistant = IconAssistant(
        provider=mock_provider, cache_dir=str(tmp_path), enable_caching=True
    )
    assistant.discover_icons("home icons")
    assistant.discover_icons("home icons")  # second call should hit cache
    assert mock_provider.query.call_count == 1  # called only once
