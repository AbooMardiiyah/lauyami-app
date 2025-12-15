# Lauyami Legal Assistant

![Lauyami App](static/frontend_lauyami_app.png?v=2)

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

<div align="center">

[🌐 Live Demo](https://lauyami-71soez18w-hamzat-tiamiyus-projects.vercel.app/) | [📽️ Demo Video](#demo-video) | [📈 Impact Metrics](#impact-metrics)

</div>

## Table of Contents

- [Lauyami Legal Assistant](#lauyami-legal-assistant)
  - [Table of Contents](#table-of-contents)
  - [About Lauyami](#about-lauyami)
  - [Market Opportunity](#market-opportunity)
    - [Problem Statement](#problem-statement)
    - [Market Size](#market-size)
    - [Competitive Advantage](#competitive-advantage)
  - [Business Model ( In Review)](#business-model--in-review)
    - [Revenue Streams](#revenue-streams)
    - [Growth Strategy](#growth-strategy)
  - [Who Is This For?](#who-is-this-for)
  - [Key Features](#key-features)
  - [Innovation \& Differentiation](#innovation--differentiation)
    - [What Makes Lauyami Unique?](#what-makes-lauyami-unique)
    - [Technical Innovation](#technical-innovation)
  - [Impact Metrics](#impact-metrics)
    - [Target Impact (Year 1)](#target-impact-year-1)
    - [Social Impact Goals](#social-impact-goals)
    - [Measurable Outcomes](#measurable-outcomes)
    - [Long-term Vision (3-5 Years)](#long-term-vision-3-5-years)
  - [Prerequisites](#prerequisites)
  - [Technology Stack](#technology-stack)
  - [Getting Started](#getting-started)
    - [Local Development](#local-development)
    - [Deployment](#deployment)
  - [Live Demo](#live-demo)
  - [Services \& Providers](#services--providers)
  - [Demo Video](#demo-video)
  - [Future Improvements](#future-improvements)
  - [License](#license)
  
## About Lauyami

Lauyami is an AI-powered legal assistant that helps tenants and landlords understand tenancy agreements in the context of Lagos State Tenancy Law 2011. The application provides:

- **Document Analysis**: Upload your tenancy agreement and get instant analysis highlighting rights, warnings, and potentially predatory clauses
- **Multilingual Voice Support**: Ask questions about your agreement in 4 Nigerian languages (English, Yoruba, Hausa, Igbo)
- **Text-to-Speech**: Get analysis read aloud in your preferred language
- **Interactive Chat**: Ask follow-up questions about your agreement or general tenancy law questions
- **PDF Reports**: Download beautifully formatted reports with color-coded warnings and recommendations

## Market Opportunity

### Problem Statement
Nigeria's rental market faces significant challenges:
- **[High illiteracy rates](https://www.worldviewdata.com/countries/nigeria/literacy-rate)** (29.6% in 2024) make legal documents inaccessible
- **Language barriers** prevent understanding of English-only legal documents
- **Predatory clauses** are common in tenancy agreements
- **Limited access to legal counsel** due to cost and availability
- **[Lagos alone](https://lagosstate.gov.ng/)** has over 20 million residents, with millions in rental agreements

### Market Size
- **[Lagos State](https://lekkigardens.com/lagos-rent-surge-2025-why-the-citys-housing-costs-keep-soaring-and-what-smart-homebuyers-are-doing-about-it/)**: ~ million residents, ~70% in rental accommodation = **12 million potential users**
- **[Nigeria-wide](https://www.worldometers.info/world-population/nigeria-population/)**: ~240 million population, growing urban rental market
- **Target segments**: Tenants (70%), Landlords (20%), Legal professionals (10%)

### Competitive Advantage
- **First-mover** in Nigerian-accented legal AI
- **Multilingual support** (Yoruba, Hausa, Igbo, Nigerian English)
- **Voice-first** interface for low-literacy users
- **Free tier** for basic analysis (vs. expensive legal consultations)
- **Real-time analysis** vs. days/weeks for traditional legal review

## Business Model ( In Review)

### Revenue Streams

1. **Freemium Model**
   - Free: Basic document analysis (1 document/month)
   - Premium: Unlimited analysis, priority support, advanced features (₦2,000/month)

2. **B2B Licensing**
   - Property management companies: Bulk analysis for multiple agreements
   - Real estate platforms: API integration (₦30,000-50,000/month)

3. **Legal Professional Tools**
   - Law firms: Advanced analysis, bulk processing (₦10,000-50,000/month)
   - Paralegals: Quick review tool (₦5,000/month)

4. **Government Partnerships**
   - Lagos State Government: Tenant rights education program
   - Consumer protection agencies: Agreement validation service

### Growth Strategy
- **Phase 1** : Lagos State focus, user acquisition
- **Phase 2** : Expand to Abuja, Port Harcourt, Ibadan
- **Phase 3** : Nigeria-wide coverage, additional document types
- **Phase 4** : Expand to other legal domains (tenement rate tax agreements, contracts, house allocation letter etc.)

## Who Is This For?

| Audience              | Why Use Lauyami?                                      |
|-----------------------|-------------------------------------------------------|
| Tenants               | Understand your rights and identify unfair clauses    |
| Landlords             | Ensure your agreements comply with Lagos State law    |
| Legal Professionals   | Quick analysis tool for tenancy agreements            |
| Property Managers     | Validate agreements before signing                    |

## Key Features

- **RAG-Powered Analysis**: Retrieval-Augmented Generation using Lagos State Tenancy Law 2011
- **Multilingual ASR**: Voice input in Nigerian languages (N-ATLaS model)
- **Nigerian-Accented LLM**: N-ATLaS for culturally-aware legal analysis
- **Vector Search**: Semantic search using Qdrant with hybrid embeddings (dense + sparse)
- **Streaming Responses**: Real-time analysis as it's generated
- **PDF Generation**: Beautiful reports with warnings, rights, and recommendations
- **Text-to-Speech**: YarnGPT integration for audio output in 4 languages

## Innovation & Differentiation

### What Makes Lauyami Unique?

| Feature | Traditional Legal Services | Competitors | **Lauyami** |
|---------|---------------------------|-------------|-------------|
| **Language Support** | English only | English + limited | **4 Nigerian languages** (Yoruba, Hausa, Igbo, Nigerian English) |
| **Voice Interface** | None | Limited | **Full voice support** (ASR + TTS) |
| **Accessibility** | High cost, requires literacy | Requires reading | **Voice-first, low-literacy friendly** |
| **Speed** | Days/weeks | Hours | **Real-time analysis** (< 30 seconds) |
| **Cost** | ₦50,000-200,000+ | ₦10,000-50,000 | **Free tier available**, Premium ₦2,000/month |
| **Cultural Context** | Generic | Generic | **Nigerian-accented AI** understands local context |
| **Coverage** | Limited to Lagos | Limited | **Scalable to all Nigerian states** |

### Technical Innovation

1. **Hybrid Vector Search**: Combines dense embeddings (semantic) + sparse BM25 (keyword) for superior retrieval
2. **Nigerian-Accented LLM**: First legal AI using N-ATLaS for culturally-aware analysis
3. **Multilingual RAG**: RAG system that works across 4 languages seamlessly
4. **Streaming Architecture**: Real-time analysis reduces perceived latency
5. **Session-Based Context**: Maintains conversation context for uploaded documents

## Impact Metrics

### Target Impact (Year 1)

| Metric | Target | Status |
|--------|--------|--------|
| **Users Served** | 10,000+ | 🚧 In Progress |
| **Documents Analyzed** | 15,000+ | 🚧 In Progress |
| **Languages Supported** | 4 (Yo, Ha, Ig, En) | ✅ Complete |
| **Average Analysis Time** | < 30 seconds | ✅ Complete |
| **Cost Savings per User** | ₦50,000+ (vs. legal consultation) | 📊 To Measure |
| **Accessibility Improvement** | 60%+ users with low literacy | 📊 To Measure |

### Social Impact Goals

- **Legal Literacy**: Increase understanding of tenant rights among 10,000+ users
- **Accessibility**: Serve 6,000+ low-literacy users through voice interface
- **Cost Reduction**: Save users ₦500M+ in legal consultation fees (Year 1)
- **Predatory Clause Detection**: Identify and flag 1,000+ unfair clauses
- **Geographic Reach**: Expand from Lagos to 3+ Nigerian states

### Measurable Outcomes

- **User Satisfaction**: Target 4.5+ star rating
- **Document Processing Accuracy**: 95%+ accuracy in clause identification
- **Response Time**: < 30 seconds average analysis time
- **Language Coverage**: 100% support for 4 Nigerian languages
- **Uptime**: 99.5%+ service availability

### Long-term Vision (3-5 Years)

- **Scale**: 1M+ users across Nigeria
- **Coverage**: All 36 Nigerian states + FCT
- **Document Types**: Expand beyond tenancy to employment, contracts, etc.
- **Partnerships**: Government agencies, legal aid organizations
- **Policy Impact**: Influence tenant protection policies through data insights

## Prerequisites

- Python 3.12+
- Basic understanding of REST APIs
- Google Cloud account (for deployment)
- Modal account (for AI services)
- Required API keys:
  - Qdrant (vector database)
  - HuggingFace (model downloads)
  - YarnGPT (text-to-speech)

## Technology Stack

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

## Getting Started

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

5. **Test with Sample Agreements**

The repository includes sample tenancy agreement PDFs in the `tenancy_agreements_to_test/` directory for testing purposes. These test files demonstrate various legal scenarios:

- Multiple legal violations
- Upfront payment issues
- Excessive charges
- Structural problems

**Important Note**: These are **simulated test documents** created for demonstration purposes. All names, locations, addresses, and other identifying information are **fictional and not real**. These documents are designed to showcase various types of legal issues that may appear in tenancy agreements and should only be used for testing the application's analysis capabilities.

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

## Live Demo

🌐 **[Try Lauyami Now](#)** - *Live demo link will be added here*

Experience Lauyami's features:
- Upload a tenancy agreement and get instant analysis
- Ask questions in Yoruba, Hausa, Igbo, or Nigerian English
- Use voice input for hands-free interaction
- Download PDF reports with color-coded warnings

**Demo Features:**
- Real-time document analysis
- Multilingual voice interaction
- Streaming responses
- PDF report generation
- Mobile-responsive design

## Services & Providers

This project integrates several best-in-class services:

| Service  | Description                           | Docs/Links                                                                  |
| -------- | ------------------------------------- | --------------------------------------------------------------------------- |
| Supabase | PostgreSQL database for legal docs    | [Supabase](https://supabase.com/docs)                                       |
| Qdrant   | Vector DB for semantic search         | [Qdrant](https://qdrant.tech/documentation/)                                |
| Modal    | N-ATLaS LLM & ASR hosting             | [Modal](https://modal.com/docs)                                             |
| YarnGPT  | Nigerian language TTS                 | [YarnGPT](https://yarngpt.ai/)                                              |
| Docker   | Containerization                      | [Docker](https://docs.docker.com/)                                          |
| FastAPI  | API framework                         | [FastAPI](https://fastapi.tiangolo.com/)                                    |
| Google Cloud Run | Backend deployment               | [Cloud Run](https://cloud.google.com/run/docs)                              |
| Vercel   | Frontend deployment                   | [Vercel](https://vercel.com/docs)                                           |

## Demo Video

📽️ **[Watch Demo Video](#)** - *Demo video link will be added here*

**Demo Highlights:**
- Document upload and analysis workflow
- Multilingual voice interaction
- Real-time streaming responses
- PDF report generation
- Mobile-responsive design

**Key Features Showcased:**
- **Market Potential**: 12M+ potential users in Lagos alone
- **Technical Innovation**: First Nigerian-accented legal AI with multilingual RAG
- **Social Impact**: Democratizing legal access for low-literacy populations
- **Scalability**: Architecture designed for Nigeria-wide expansion
- **Business Model**: Multiple revenue streams with freemium approach

## Future Improvements

1. **Fine-tune N-ATLaS LLM** on tenancy agreements and property legal documents
2. **Expand Jurisdiction** - Add Abuja, Ibadan, and other Nigerian states tenancy laws
3. **Optimize Latency** - Improve document analysis speed and response times
4. **Tenement Rate Features** - Add explanations for tenement rate agreements
5. **Enhanced Voice Experience** - Improve language selection and audio latency
6. **Advanced Reports** - Enhanced PDF generation with more insights and visualizations
7. **Microservices Architecture** - Migrate from monolith to distributed services
8. **Pricing & Personalization** - Add subscription tiers and user accounts

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built** by Hamzat Tiamiyu (Adeiza) @[portfolio](https://aboomardiiyah.github.io/) | Empowering Nigerian tenants with AI
