# AI Recommendation System

A production-ready, full-stack AI recommendation engine built with modern ML techniques and a commercial-quality web interface.

![RecSys](/Frontend.png)


## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  React + TypeScript + TailwindCSS + Shadcn UI + Framer Motion  │
├────────────────────────────────────────────────────────────────┤
│                     REST API (FastAPI)                          │
│  JWT Auth │ Rate Limiting │ Caching │ Repository Pattern        │
├────────────────────────────────────────────────────────────────┤
│                    ML Pipeline (Python)                         │
│  Popularity │ Content-Based │ Collaborative │ MF │ Hybrid      │
├────────────────────────────────────────────────────────────────┤
│               PostgreSQL + Redis Cache Layer                    │
└────────────────────────────────────────────────────────────────┘
```

## Features

### Recommendation Algorithms
- **Popularity-Based**: Trending items based on interaction count and ratings
- **Content-Based Filtering**: TF-IDF vectorization + cosine similarity
- **Collaborative Filtering**: KNN-based user-user similarity
- **Matrix Factorization**: SVD-style latent factor model with SGD
- **Hybrid System**: Weighted ensemble of all algorithms with confidence scoring

### ML Pipeline
- Data loading from PostgreSQL
- Feature engineering and text vectorization
- Model training with evaluation metrics (Precision@K, Recall@K, NDCG, MAP)
- Model versioning and persistence
- Real-time prediction API

### Application Features
- JWT authentication with refresh tokens
- Dashboard with personalized recommendations
- Algorithm comparison view
- Search with category filters
- Admin panel with model training controls
- Data visualizations (charts, metrics)
- Dark mode, responsive design, loading skeletons
- Toast notifications, infinite scroll, pagination

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript, TailwindCSS, Framer Motion |
| Backend | FastAPI, Python 3.11, Pydantic, SQLAlchemy |
| ML | scikit-learn, NumPy, Pandas, SciPy |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | JWT (python-jose, passlib) |
| Deployment | Docker, Docker Compose |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+

### Using Docker (Recommended)

```bash
cd docker
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set up PostgreSQL database
# Copy .env.example to .env and configure

# Seed the database
python -m seed_data

# Run the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Default Credentials

- **Admin**: admin@recommendation.ai / admin123
- **User**: alice@example.com / password123

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login |
| GET | /api/v1/auth/me | Get current user |
| GET | /api/v1/recommendations/me | Get recommendations |
| GET | /api/v1/recommendations/all | Get all algorithm results |
| POST | /api/v1/recommendations/compare | Compare algorithms |
| POST | /api/v1/recommendations/rate | Rate an item |
| POST | /api/v1/recommendations/interaction | Record interaction |
| GET | /api/v1/recommendations/similar/:id | Get similar items |
| GET | /api/v1/search/ | Search items |
| GET | /api/v1/items/trending | Trending items |
| GET | /api/v1/items/top-rated | Top rated items |
| POST | /api/v1/admin/train | Train model |
| GET | /api/v1/admin/stats | Dashboard stats |
| GET | /api/v1/admin/models | List trained models |

## Project Structure

```
recommendation-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Config, DB, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── repositories/  # Data access layer
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── ml/
│   │   ├── pipelines/     # ML algorithms
│   │   ├── models/        # Saved models
│   │   └── utils/         # Helper functions
│   ├── seed_data.py       # Database seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json
├── docker/
│   └── docker-compose.yml
└── README.md
```

## ML Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Precision@K | Fraction of recommended items that are relevant |
| Recall@K | Fraction of relevant items that are recommended |
| NDCG@K | Normalized Discounted Cumulative Gain |
| MAP@K | Mean Average Precision |
| RMSE | Root Mean Square Error (for rating prediction) |

## License

MIT
