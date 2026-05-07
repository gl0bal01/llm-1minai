"""Tests for model registration coverage and integrity."""

import llm_1min


def test_register_models_populates_expected_catalog():
    """Model registration should expose the published 1min model IDs."""
    captured = []
    llm_1min.register_models(lambda model: captured.append(model))

    ids = [m.model_id for m in captured]
    assert len(ids) >= 75
    assert "1min/gpt-5" in ids
    assert "1min/claude-4-6-sonnet" in ids
    assert "1min/sonar-deep-research" in ids


def test_register_models_model_objects_have_expected_attributes():
    """Registered models should carry both CLI model IDs and API model IDs."""
    captured = []
    llm_1min.register_models(lambda model: captured.append(model))

    for model in captured:
        assert model.model_id.startswith("1min/")
        assert isinstance(model.api_model_id, str)
        assert len(model.api_model_id) > 0
        assert isinstance(model.display_name, str)
        assert len(model.display_name) > 0
