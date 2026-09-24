<div align="center">

# 🚀 MomentumAI

### *Your goals deserve more than a to-do list.*

**AI-powered goal tracking that plans your path, tracks your climb, and keeps you moving.**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Python](https://img.shields.io/badge/Python_3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

*Tell the AI your goal. It builds the roadmap. You climb the mountain.*

</div>

---

## ⛰️ What is MomentumAI?

MomentumAI isn't just another habit tracker. It's an **AI-powered goal achievement engine** that turns vague ambitions into structured, trackable plans — and keeps you accountable every step of the way.

Imagine telling an AI *"I want to learn machine learning in 3 months"* and getting back:
- 📅 A **week-by-week schedule** tailored to your available hours
- 🏔️ **Milestones** that break the impossible into the achievable
- 📚 **Curated resources** (courses, books, tools) filtered by your budget
- 📊 A **visual dashboard** where a hiker climbs a mountain as you progress
- 🔔 **Daily check-ins** that keep your streak alive

---

## ✨ Key Features

### 🤖 AI-Powered Onboarding
No blank-page anxiety. An AI chatbot asks the right questions — *What's your goal? What's your timeline? How many hours can you commit?* — and builds a plan from your answers.

### 🗺️ Smart Plan Generation
Using **Google Gemini**, MomentumAI deep-searches and generates:
- Structured weekly schedules
- Progressive milestones with target dates
- The best available resources (courses, books, videos)

### 🎛️ Full Customization
Don't like the AI's plan? Modify your schedule, swap resources, adjust milestones. It's *your* journey.

### 📈 Visual Progress Dashboard
Watch a **hiker climb a mountain** as you progress toward your goal. Real-time charts, streak counters, ETA predictions, and milestone tracking — all in one view.

### 🔔 Smart Notifications
Daily reminders. Weekly summaries. Milestone celebrations. Deadline warnings. Streak alerts. MomentumAI keeps you moving without being annoying.

### 📊 Analytics & Insights
- Progress history with trend lines
- Weekly hours tracked
- On-track / off-track detection
- AI-generated feedback on your performance

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI App                        │
├──────────┬──────────┬───────────┬───────────────────┤
│  Auth    │  Goals   │ Progress  │   Notifications    │
│  Router  │  Router  │  Router   │   Router           │
├──────────┴──────────┴───────────┴───────────────────┤
│                  Service Layer                        │
│  auth · goal · onboarding · ai · plan · progress     │
├─────────────────────────────────────────────────────┤
│              MongoDB (PyMongo Async)                  │
│  users · goals · plans · progress_logs · notifications│
├─────────────────────────────────────────────────────┤
│           Gemini AI  ·  APScheduler                   │
└─────────────────────────────────────────────────────┘
```

**Clean layered architecture:**
- **Routers** → Thin HTTP controllers (status codes, validation)
- **Services** → Business logic (HTTP-agnostic, testable)
- **Models** → Pydantic schemas (request/response validation)
- **Global Exception Handlers** → Consistent error responses everywhere

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI (async, high-performance) |
| **Database** | MongoDB with PyMongo Async API |
| **AI** | Google Gemini (structured output) · LlamaIndex (retrieval, indexing) |
| **Auth** | JWT (access + refresh tokens) + bcrypt |
| **Scheduling** | APScheduler (daily reminders, weekly evaluations) |
| **Validation** | Pydantic v2 with strict schemas |
| **Package Manager** | uv (blazing fast) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MongoDB (local or Atlas)
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repo
git clone https://github.com/srimanchaudhuri/Momentum-AI.git
cd Momentum-AI

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI, JWT secret, and Gemini API key

# Run the development server
uv run fastapi dev main.py
```

### Environment Variables

```env
DB_URL=mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME=momentum_db
JWT_SECRET_KEY=your-super-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

The API docs are available at **http://localhost:8000/docs** 🎉

---

## 📡 API Overview

| Endpoint | Description |
|---|---|
| `POST /api/auth/signup` | Create an account |
| `POST /api/auth/login` | Get access token |
| `POST /api/onboarding/start` | Start AI goal conversation |
| `POST /api/onboarding/{id}/answer` | Answer AI's questions |
| `GET /api/goals` | List your goals |
| `GET /api/goals/{id}/plan` | View your AI-generated plan |
| `POST /api/goals/{id}/progress` | Log daily check-in |
| `GET /api/dashboard` | Full progress dashboard |
| `GET /api/notifications` | Your notifications |

> 📖 Full interactive API docs at `/docs` (Swagger UI) or `/redoc`

---

## 📂 Project Structure

```
Momentum-AI/
├── main.py                 # App entry point
├── app/                    # Core wiring (config, DB, auth, logging)
├── ai/                     # LlamaIndex layer (embeddings, llm, index, ingestion, chat)
├── models/                 # Pydantic request/response schemas
├── services/               # Business logic (HTTP-agnostic)
├── routers/                # Thin API controllers
├── middleware/              # Auth middleware
└── tasks/                  # Background jobs (reminders, evaluations)
```

---

## 🗺️ Roadmap

- [x] Core FastAPI setup with MongoDB
- [x] User CRUD with service layer
- [x] Global exception handlers & logger
- [ ] 🔐 Authentication (JWT + bcrypt)
- [ ] 🤖 AI onboarding conversation flow
- [ ] 🗺️ AI plan generation (Gemini)
- [ ] 📈 Progress tracking & analytics
- [ ] 📊 Dashboard API
- [ ] 🔔 Notifications & scheduling
- [ ] 🌐 Frontend (coming soon)

---

## 🤝 Contributing

This project is in active development. Stay tuned!

---

<div align="center">

**Built with 🔥 by [Sriman Chaudhuri](https://github.com/srimanchaudhuri)**

*Every mountain is climbable. You just need the right plan.*

</div>
