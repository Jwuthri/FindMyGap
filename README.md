# FindMyGap

> 🚀 **AI-Powered Product Gap Analysis Platform** built with **FastAPI** + **Next.js** + **Agno** + **OpenRouter**

Find My Gaps uses advanced LLM analysis to identify product gaps across entire markets by aggregating and analyzing customer feedback from app stores, e-commerce reviews, Reddit discussions, support tickets, and more. Discover actionable insights on what customers desperately need but can't find anywhere.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=flat&logo=next.js)](https://nextjs.org)
[![Agno](https://img.shields.io/badge/Agno-2.0+-blue?style=flat)](https://docs.agno.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-500%2B%20models-green?style=flat)](https://openrouter.ai)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178c6?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed?style=flat&logo=docker)](https://www.docker.com)

---

## ✨ **Key Features**

### 🔍 **Multi-Source Gap Analysis**
- **📱 App Store Reviews**: Google Play & Apple App Store scraping and analysis
- **🛍️ E-commerce Reviews**: Amazon and other marketplace feedback aggregation
- **💬 Reddit Analysis**: Discussion mining via Apify for real user pain points
- **🎫 Support Tickets**: Import and analyze support data
- **🌐 Forum Discussions**: Cross-platform feedback collection
- **📊 Custom Data Upload**: CSV/JSON upload for proprietary feedback

### 🧠 **AI-Powered Intelligence**
- **500+ Models** via [OpenRouter](https://openrouter.ai) (GPT-5, Claude 3.7, Gemini 2.5 Pro, etc.)
- **Smart Gap Detection**: LLM identifies patterns and unmet needs across thousands of data points
- **Smart Clustering**: Groups similar complaints into actionable product opportunities
- **Competitor Gap Analysis**: See what features competitors are missing
- **Trend Detection**: Track how gaps evolve over time
- **Semantic Search**: Find specific pain points across all feedback sources

### 📈 **Actionable Insights**
- **Gap Scoring**: Priority ranking based on frequency and sentiment
- **Evidence-Based Reports**: PDF/Markdown reports with source citations
- **Opportunity Sizing**: Market demand estimation for each gap
- **Export & Share**: Multiple format support for team collaboration
- **Real-Time Processing**: Upload data and get insights in minutes

### 🚀 **Production-Ready Architecture**
- **FastAPI Backend** with async/await support
- **Next.js Frontend** with modern UI and data visualization
- **Vector Database** (Pinecone/Qdrant) for semantic analysis
- **Background Task Processing** with Celery workers
- **Docker Compose** setup for easy deployment
- **Scalable Infrastructure** with Redis, PostgreSQL, and microservices support

---

## 🏗️ **Architecture**
...

---

## 🚀 **Quick Start**

### 1. **Prerequisites**
```bash
# Install uv (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Node.js 18+
# https://nodejs.org/

# Install Docker & Docker Compose
# https://docs.docker.com/get-docker/
```

### 2. **Environment Setup**
```bash
# Copy environment files
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env

# Set your API keys in backend/.env
OPENROUTER_API_KEY=your_openrouter_key_here

PINECONE_API_KEY=your_pinecone_key_here

```

### 3. **Start with Docker Compose** ⚡
```bash
# Start all services (recommended for first run)
docker-compose up -d

# Or use the development setup
docker-compose -f docker-compose.dev.yml up -d
```

### 4. **Manual Development Setup** 🛠️
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e .
uv pip list
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 5. **Access Your AI Agent App** 🎉
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤖 **AI Agent Configuration**

### **Model Selection**
Choose from 500+ models available through OpenRouter:

```python
# Latest and greatest models
"openai/gpt-5"                   # OpenAI's latest
"anthropic/claude-4.5-sonnet"    # Anthropic's most capable
"google/gemini-2.5-pro"          # Google's flagship
"x-ai/grok-4"                    # Latest xai

# Fast and efficient
"openai/gpt-5-mini"             # Quick responses
"openai/gpt-5-nano"             # Ultra Fast responses
"anthropic/claude-3.5-haiku"    # Speed optimized responses
"google/gemini-2.5-flash"       # Very quick responses
"x-ai/grok-4-fast"              # Fast resposnse 
```

### **Agent Types**


- **Single Agent**: One AI agent handling all conversations
- **Multi-Agent**: Multiple specialized agents working together
- **Workflow**: Step-by-step agent workflows for complex tasks

### **Memory Configuration**

**Current Setup**: vector with pinecone


- **Vector Memory**: Semantic search across conversation history
- **Redis**: Fast session-based memory
- **Hybrid**: Best of both vector search and Redis speed
- **In-Memory**: Development and testing

---

## 📚 **API Endpoints**
```python
```

---

## 🔧 **Configuration**

### **Backend Settings** (`backend/.env`)
```bash
```

### **Frontend Settings** (`frontend/.env`)
```bash
```

---

## 🚢 **Deployment**

### **Using Docker** (Recommended)
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment script
./backend/scripts/deploy.sh
```

### **Manual Deployment**
```bash
# Backend
cd backend
uv pip install -e .
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd frontend
npm run build
npm start
```

### **Environment Variables for Production**
- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY`
- Configure proper `CORS_ORIGINS`
- Set up SSL/TLS certificates
- Use managed database services
- Configure pinecone production instance

---

## 📁 **Project Structure**

```
findmygap/
├── 📁 backend/                 # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 api/v1/         # API routes
│   │   ├── 📁 core/           # Core business logic
│   │   │   ├── 📁 llm/        # Agno + OpenRouter integration
│   │   │   ├── 📁 memory/     # Vector & Redis memory
│   │   │   └── 📁 security/   # Auth & rate limiting
│   │   ├── 📁 models/         # Pydantic models
│   │   ├── 📁 services/       # Business services
│   │   ├── 📁 tasks/          # Celery background tasks
│   │   └── 📁 utils/          # Utilities
│   ├── 📁 docker/             # Docker configurations
│   ├── 📁 scripts/            # Deployment scripts
│   └── 📄 pyproject.toml      # Python dependencies (uv)
│
├── 📁 frontend/               # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/            # Next.js App Router
│   │   ├── 📁 components/     # React components
│   │   │   ├── 📁 ui/         # Base UI components
│   │   │   └── 📁 chat/       # Chat interface
│   │   ├── 📁 hooks/          # Custom React hooks
│   │   ├── 📁 lib/            # Utilities & API client
│   │   └── 📁 types/          # TypeScript definitions
│   └── 📄 package.json       # Node.js dependencies
│
├── 📄 docker-compose.yml     # Development services
├── 📄 docker-compose.prod.yml # Production setup
└── 📄 README.md              # This file
```

---

## 🧪 **Development**

### **Running Tests**
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

### **Code Quality**
```bash
# Backend linting & formatting
cd backend
uv run black .
uv run isort .
uv run ruff check .
uv run mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### **Database Migrations**

```bash
cd backend
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

---

## 🤝 **Contributing**

### 🔧 **Setup Pre-commit Hooks**

We use pre-commit hooks to ensure code quality. Set them up before making changes:

```bash
# Install and setup pre-commit hooks
./scripts/setup-pre-commit.sh

# Or manually:
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

The hooks will automatically check:
- **Python**: Black formatting, autoflake unused import removal, isort import sorting, flake8 linting, mypy type checking
- **Frontend**: Prettier formatting, ESLint linting
- **Security**: Secret detection, private key scanning
- **General**: Trailing whitespace, file endings, YAML/JSON validation

### 🚀 **Contribution Steps**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. **Setup pre-commit hooks**: `./scripts/setup-pre-commit.sh`
4. Make your changes
5. Run tests: `uv run pytest && npm test`
6. Commit: `git commit -m 'Add amazing feature'` (pre-commit hooks will run automatically)
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **[Agno](https://docs.agno.com)** - Powerful AI agent framework
- **[OpenRouter](https://openrouter.ai)** - Unified access to 500+ AI models
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Next.js](https://nextjs.org)** - React framework for production
- **[uv](https://github.com/astral-sh/uv)** - Ultra-fast Python package manager

- **[Pinecone](https://pinecone.io)** - Vector database for AI memory


---

## 📞 **Support**

- 📧 **Email**: julien.wut@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Julien Wuthrich/findmygap/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/Julien Wuthrich/findmygap/wiki)

---

<div align="center">

**Built with ❤️ using the latest AI technologies**

[🤖 Agno](https://docs.agno.com) • [🔀 OpenRouter](https://openrouter.ai) • [⚡ FastAPI](https://fastapi.tiangolo.com) • [⚛️ Next.js](https://nextjs.org)

</div>
