"""Unit tests for API models."""

import pytest
from pydantic import ValidationError

from src.api.models.api_models import (
    AskRequest,
    SearchResult,
    UniqueTitleRequest,
    UploadAgreementResponse,
    VoiceAskRequest,
)


def test_search_result_model():
    """Test SearchResult model with new field names."""
    result = SearchResult(
        section_title="Section 1: Tenant Rights",
        jurisdiction="Lagos State",
        document_title="Lagos State Tenancy Law 2011",
        document_type=["tenancy_law"],
        document_id="lagos-tenancy-law-2011",
        chunk_text="Tenants have the right to...",
        score=0.95,
    )
    assert result.section_title == "Section 1: Tenant Rights"
    assert result.jurisdiction == "Lagos State"
    assert result.document_title == "Lagos State Tenancy Law 2011"
    assert result.document_type == ["tenancy_law"]
    assert result.document_id == "lagos-tenancy-law-2011"
    assert result.chunk_text == "Tenants have the right to..."
    assert result.score == 0.95


def test_unique_title_request_model():
    """Test UniqueTitleRequest model with new field names."""
    request = UniqueTitleRequest(
        query_text="tenant rights",
        jurisdiction="Lagos State",
        document_title="Lagos State Tenancy Law 2011",
        title_keywords="rights",
        limit=5,
    )
    assert request.query_text == "tenant rights"
    assert request.jurisdiction == "Lagos State"
    assert request.document_title == "Lagos State Tenancy Law 2011"
    assert request.title_keywords == "rights"
    assert request.limit == 5


def test_ask_request_model():
    """Test AskRequest model."""
    request = AskRequest(
        query_text="What are tenant rights?",
        provider="natlas",
        jurisdiction="Lagos State",
        document_title=None,
        title_keywords=None,
        limit=5,
        session_id=None,
        model=None,
    )
    assert request.query_text == "What are tenant rights?"
    assert request.provider == "natlas"
    assert request.jurisdiction == "Lagos State"
    assert request.limit == 5


def test_voice_ask_request_model():
    """Test VoiceAskRequest model."""
    request = VoiceAskRequest(
        session_id="test-session-123",
        language="yo",
        limit=5,
        provider="natlas",
    )
    assert request.session_id == "test-session-123"
    assert request.language == "yo"
    assert request.limit == 5
    assert request.provider == "natlas"


def test_upload_agreement_response_model():
    """Test UploadAgreementResponse model."""
    response = UploadAgreementResponse(
        session_id="test-session-123",
        message="Agreement uploaded successfully",
    )
    assert response.session_id == "test-session-123"
    assert response.message == "Agreement uploaded successfully"


def test_search_result_optional_fields():
    """Test SearchResult with optional fields."""
    result = SearchResult(
        section_title="Section 1",
        jurisdiction=None,
        document_title=None,
        document_type=[],
        document_id=None,
        chunk_text="Some text",
        score=None,
    )
    assert result.section_title == "Section 1"
    assert result.jurisdiction is None
    assert result.document_title is None
    assert result.document_type == []
    assert result.document_id is None
    assert result.chunk_text == "Some text"
    assert result.score is None

