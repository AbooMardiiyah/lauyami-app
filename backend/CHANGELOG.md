# Changelog

## 1.0.0

Released on December 2024.

### Added

- Initial release of Lauyami Legal Assistant
- AI-powered tenancy agreement analysis using Lagos State Tenancy Law 2011
- Multilingual voice input support (English, Yoruba, Hausa, Igbo) via N-ATLaS ASR
- N-ATLaS LLM integration via Modal for Nigerian-context legal analysis
- RAG (Retrieval-Augmented Generation) system using Qdrant vector database
- Real-time streaming analysis with progressive status updates
- Text-to-Speech support in 4 Nigerian languages via YarnGPT
- PDF report generation with color-coded warnings, rights, and recommendations
- Interactive chat interface for follow-up questions
- General tenancy law Q&A without document upload
- Document analysis with highlighting of:
  - ✅ Tenant rights under Lagos law
  - ⚠️ Warnings about potentially problematic clauses
  - 🚨 Predatory clauses that violate the law
- FastAPI backend with streaming endpoints
- React + Vite frontend with modern UI (Shadcn)
- Google Cloud Run deployment support
- Vercel frontend deployment
- Modal deployment for AI services (LLM + ASR)
- Caching for improved performance
- Audio caching for TTS
- Session management with localStorage
- Hybrid search with dense and sparse embeddings
- Environment-based configuration with Pydantic
- Comprehensive error handling and logging
