# Lauyami Legal Assistant

![Diagram](static/app_diagram.png)

<div align="center">

<!-- Project Status -->

![Status](https://img.shields.io/badge/status-active-success.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python version](https://img.shields.io/badge/python-3.12.8-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

<!-- Providers -->

[![Supabase](https://img.shields.io/badge/Supabase-2.18.1-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.15.1-5A31F4?logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Modal](https://img.shields.io/badge/Modal-1.2.4-000000?logo=modal&logoColor=white)](https://modal.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

</div>

<p align="center">
  <em>An AI-powered legal assistant for analyzing tenancy agreements using Lagos State Tenancy Law 2011</em>
</p>

## 📚 Table of Contents

- [Lauyami Legal Assistant](#lauyami-legal-assistant)
  - [📚 Table of Contents](#-table-of-contents)
  - [🎯 About Lauyami](#-about-lauyami)
  - [👥 Who Is This For?](#-who-is-this-for)
  - [🧑‍🎓 Key Features](#-key-features)
  - [🎓 Prerequisites](#-prerequisites)
  - [📚 Technology Stack](#-technology-stack)
  - [🚀 Getting Started](#-getting-started)
    - [Local Development](#local-development)
    - [Deployment](#deployment)
  - [🔌 Services \& Providers](#-services--providers)
  - [🪪 License](#-license)
  
## 🎯 About Lauyami

Lauyami is an AI-powered legal assistant that helps tenants and landlords understand tenancy agreements in the context of Lagos State Tenancy Law 2011. The application provides:

- **Document Analysis**: Upload your tenancy agreement and get instant analysis highlighting rights, warnings, and potentially predatory clauses
- **Multilingual Voice Support**: Ask questions about your agreement in 4 Nigerian languages (English, Yoruba, Hausa, Igbo)
- **Text-to-Speech**: Get analysis read aloud in your preferred language
- **Interactive Chat**: Ask follow-up questions about your agreement or general tenancy law questions
- **PDF Reports**: Download beautifully formatted reports with color-coded warnings and recommendations

## 👥 Who Is This For?

| Audience              | Why Use Lauyami?                                      |
|-----------------------|-------------------------------------------------------|
| Tenants               | Understand your rights and identify unfair clauses    |
| Landlords             | Ensure your agreements comply with Lagos State law    |
| Legal Professionals   | Quick analysis tool for tenancy agreements            |
| Property Managers     | Validate agreements before signing                    |

## 🧑‍🎓 Key Features

- **RAG-Powered Analysis**: Retrieval-Augmented Generation using Lagos State Tenancy Law 2011
- **Multilingual ASR**: Voice input in Nigerian languages (N-ATLaS model)
- **Multi-Provider LLM**: N-ATLaS (primary) with OpenAI (fallback)
- **Vector Search**: Semantic search using Qdrant with hybrid embeddings
- **Streaming Responses**: Real-time analysis as it's generated
- **PDF Generation**: Beautiful reports with warnings, rights, and recommendations
- **Text-to-Speech**: YarnGPT integration for audio output in 4 languages

![Lauyami UI](static/gradio_app.png)

## 🎓 Prerequisites

- Python 3.12+
- Basic understanding of REST APIs
- Google Cloud account (for deployment)
- Modal account (for AI services)
- Required API keys:
  - Qdrant (vector database)
  - HuggingFace (model downloads)
  - YarnGPT (text-to-speech)

## 📚 Technology Stack

**Backend:**
- FastAPI (REST API)
- Modal (N-ATLaS LLM & ASR hosting)
- Qdrant (vector database)
- Supabase (PostgreSQL for documents)
- Prefect (orchestration - optional)

**Frontend:**
- React + Vite
- TypeScript
- Tailwind CSS + Shadcn UI
- Vercel (deployment)

**AI/ML:**
- N-ATLaS (Nigerian-accented LLM)
- N-ATLaS ASR (multilingual speech recognition)
- YarnGPT (text-to-speech in Nigerian languages)
- FastEmbed (embeddings)

## 🚀 Getting Started

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lauyami-app.git
cd lauyami-app
```

2. **Backend Setup**
```bash
cd backend
uv sync
cp .env.example .env
# Fill in your API keys in .env
make run-dev
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Deploy Modal Services**
```bash
cd backend/modal_services
modal deploy natlas_serve.py
modal deploy natlas_asr.py
```

### Deployment

See [CLOUD_RUN_DEPLOYMENT_GUIDE.md](../CLOUD_RUN_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

**Quick Deploy:**
```bash
# Backend (Google Cloud Run)
cd backend
./deploy_fastapi.sh

# Frontend (Vercel)
cd frontend
vercel
```

## 🔌 Services & Providers

This project integrates several best-in-class services:

| Service  | Description                           | Docs/Links                                                                  |
| -------- | ------------------------------------- | --------------------------------------------------------------------------- |
| Supabase | PostgreSQL database for legal docs    | [Supabase](https://supabase.com/docs)                                       |
| Qdrant   | Vector DB for semantic search         | [Qdrant](https://qdrant.tech/documentation/)                                |
| Modal    | N-ATLaS LLM & ASR hosting             | [Modal](https://modal.com/docs)                                             |
                             |
| YarnGPT  | Nigerian language TTS                 | [YarnGPT](https://yarngpt.ai/)                                              |
| Docker   | Containerization                      | [Docker](https://docs.docker.com/)                                          |
| FastAPI  | API framework                         | [FastAPI](https://fastapi.tiangolo.com/)                                    |
| Google Cloud Run | Backend deployment               | [Cloud Run](https://cloud.google.com/run/docs)                              |
| Vercel   | Frontend deployment                   | [Vercel](https://vercel.com/docs)                                           |

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for the hackathon** by Hamzat Tiamiyu (Adeiza) @[portfolio](https://aboomardiiyah.github.io/) | Empowering Nigerian tenants with AI
