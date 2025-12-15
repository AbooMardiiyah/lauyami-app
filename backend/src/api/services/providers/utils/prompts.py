try:
    import opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False

from src.api.models.api_models import SearchResult
from src.api.models.provider_models import ModelConfig

config = ModelConfig()

PROMPT = """
You are a skilled legal research assistant specialized in analyzing tenancy agreements and Lagos State Tenancy Law.
Respond to the user's query using the provided context from legal documents,
that is retrieved from a vector database without relying on outside knowledge or assumptions.

**IMPORTANT: You MUST respond in {language_name}. All your output must be in {language_name}.**

### Output Rules:
- Write a detailed, structured answer using **Markdown** (headings, bullet points,
  short or long paragraphs as appropriate).
- Use up to **{tokens} tokens** without exceeding this limit.
- Only include facts from the provided context from the legal documents.
- Attribute each fact to the correct source document and include **clickable links** where available.
- There is no need to mention that you based your answer on the provided context.
- But if no relevant information exists, clearly state this and provide a fallback suggestion.
- At the very end, include a **funny quote** and wish the user a great day.
- **CRITICAL: Respond entirely in {language_name}. Do not mix languages.**

### Query:
{query}

### Context Documents:
{context_texts}

### Final Answer (in {language_name}):
"""


# Create a new prompt (only if opik is available and configured)
prompt = None
if OPIK_AVAILABLE:
    try:
        prompt = opik.Prompt(
            name="lauyami_legal_assistant", prompt=PROMPT, metadata={"environment": "development"}
        )
    except Exception:
        # opik is installed but not configured (no API key), continue without it
        prompt = None


def build_research_prompt(
    contexts: list[SearchResult],
    query: str = "",
    tokens: int = config.max_completion_tokens,
    language: str = "en",
) -> str:
    """Construct a research-focused LLM prompt using the given query
    and supporting context documents.

    The prompt enforces Markdown formatting, citations, and strict length guidance.

    Args:
        contexts (list[SearchResult]): List of context documents with metadata.
        query (str): The user's research query.
        tokens (int): Maximum number of tokens for the LLM response.

    Returns:
        str: The formatted prompt ready for LLM consumption.

    """
    # Join all retrieved contexts into a readable format
    context_texts = "\n\n".join(
        (
            f"- Document Title: {r.document_title or 'N/A'}\n"
            f"  Section Title: {r.section_title}\n"
            f"  Document Type: {', '.join(r.document_type) if r.document_type else 'N/A'}\n"
            f"  Jurisdiction: {r.jurisdiction or 'N/A'}\n"
            f"  Document ID: {r.document_id or 'N/A'}\n"
            f"  Snippet: {r.chunk_text}"
        )
        for r in contexts
    )

    # Map language codes to language names
    language_names = {
        "en": "English",
        "yo": "Yoruba",
        "ha": "Hausa",
        "ig": "Igbo",
    }
    language_name = language_names.get(language, "English")
    
    return PROMPT.format(
        query=query,
        context_texts=context_texts,
        tokens=tokens,
        language_name=language_name,
    )
