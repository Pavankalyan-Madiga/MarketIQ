# MarketIQ — Customer Behavior & Marketing Intelligence

MarketIQ is a data-driven customer behavior and marketing intelligence platform designed to help businesses understand customer behavior, identify valuable customer segments, predict customer churn, analyze customer sentiment, and generate product recommendations.

The platform combines data analytics, machine learning, and an interactive dashboard to turn customer data into actionable business insights.

## Features

### 1. Interactive Dashboard
- Customer and business performance overview
- Key performance indicators
- Customer behavior insights
- Data-driven visualizations

### 2. Customer Management
- View customer records
- Explore customer information
- Search and analyze customer data

### 3. RFM Customer Segmentation
- Recency analysis
- Frequency analysis
- Monetary analysis
- Customer segmentation based on purchasing behavior

### 4. Customer Churn Prediction
- Machine learning-based churn prediction
- Customer-level churn probability
- Low, medium, and high-risk classification
- Churn prediction summary and analytics

### 5. Product Recommendations
- Rule-based product recommendations
- Customer-oriented product suggestions

### 6. Sentiment Analysis
- Analyze customer review text using VADER
- Positive, negative, and neutral classification
- Sentiment distribution
- Sentiment trends
- Review search and filtering

### 7. Dataset Management
- Upload datasets
- Preview dataset records
- Manage uploaded datasets

### 8. Data Quality
- Dataset quality monitoring
- Data validation and quality insights

### 9. Settings
- Profile preferences
- Light and dark appearance preferences
- Notification preferences
- Browser-based preference storage

### 10. AI Assistant
- Reserved for future development

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| UI & Styling | CSS |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Machine Learning | Scikit-learn |
| Sentiment Analysis | VADER |
| API Communication | REST APIs, Axios |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

## System Architecture

```text
                 ┌──────────────────────┐
                 │       User           │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   React + Vite       │
                 │    Frontend          │
                 └──────────┬───────────┘
                            │
                       REST API
                            │
                            ▼
                 ┌──────────────────────┐
                 │     FastAPI          │
                 │      Backend         │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │ PostgreSQL │ │ ML Models  │ │ Sentiment  │
       │ Database   │ │ Churn      │ │ Analysis   │
       └────────────┘ └────────────┘ └────────────┘
```

## Project Structure

```text
customer-marketing-intelligence/
│
├── ai/
│
├── backend/
│   └── app/
│       └── api/
│           ├── churn.py
│           └── sentiment.py
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── frontend/
│   └── src/
│       ├── assets/
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
│
├── ml/
│
├── models/
│   └── churn/
│       ├── best_churn_model.joblib
│       ├── best_model_metrics.json
│       └── model_comparison.csv
│
├── notebooks/
│
├── scripts/
│
├── tests/
│
├── docker-compose.yml
└── README.md
```

## Dataset Information

The project uses synthetic customer and marketing data for development and demonstration.

| Dataset | Records |
|---|---:|
| Customers | 5,000 |
| Products | 500 |
| Orders | 15,000 |
| Order Items | 25,000 |
| Reviews | 8,000 |
| Campaigns | 1,000 |
| Interactions | 20,000 |
| Churn Labels | 5,000 |
| **Total** | **79,500** |

## Machine Learning — Churn Prediction

The churn prediction module uses customer behavioral features to estimate the likelihood of customer churn.

The project includes:
- Feature engineering
- Model training and comparison
- Random Forest classification
- Customer-level churn probability
- Risk classification

The current best model is stored at:

`models/churn/best_churn_model.joblib`

Current evaluation results:

| Metric | Score |
|---|---:|
| Accuracy | 69.10% |
| Precision | 35.87% |
| Recall | 51.36% |
| F1 Score | 42.24% |
| ROC-AUC | 68.22% |

**Note:** Churn labels are synthetically generated. These metrics demonstrate model behavior on the project's synthetic dataset and should not be interpreted as real-world business performance.

## Sentiment Analysis

MarketIQ uses VADER to classify customer review text.

Classification thresholds:
- Positive: Compound score ≥ 0.05
- Negative: Compound score ≤ -0.05
- Neutral: Compound score between -0.05 and 0.05

Current dataset sentiment summary:

| Sentiment | Reviews |
|---|---:|
| Positive | 5,429 |
| Negative | 1,525 |
| Neutral | 1,046 |
| **Total** | **8,000** |

## Backend API Endpoints

### Churn Prediction

Base path: `/api/v1/churn`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check churn service |
| GET | `/model-info` | Model information |
| GET | `/customers` | Customer predictions |
| GET | `/customers/{customer_id}` | Individual prediction |
| GET | `/summary` | Churn summary |

### Sentiment Analysis

Base path: `/api/v1/sentiment`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check sentiment service |
| GET | `/summary` | Sentiment summary |
| GET | `/distribution` | Sentiment distribution |
| GET | `/trends` | Sentiment trends |
| GET | `/reviews` | Search and filter reviews |

## Local Installation and Setup

### Prerequisites

- Python 3.10+
- Node.js and npm
- PostgreSQL
- Git
- Docker and Docker Compose (if using the containerized setup)

### 1. Clone the repository

```bash
git clone https://github.com/Pavankalyan-Madiga/MarketIQ.git

cd MarketIQ
```

### 2. Backend setup

```bash
cd backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

Configure your backend environment variables in `backend/.env` according to your database configuration.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

### 3. Frontend setup

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

`http://localhost:5173`

### 4. Database setup

Configure PostgreSQL credentials and database settings in your backend environment file.

Run the project's database initialization and data-loading scripts according to the available scripts in the `scripts/` directory.

### 5. Docker setup

The project includes a Docker Compose configuration.

Start the configured services:

```bash
sudo docker compose up --build -d
```

Check running containers:

```bash
sudo docker compose ps
```

Stop the services:

```bash
sudo docker compose down
```

## Environment Variables

Keep credentials and secrets in local environment files. Never commit actual passwords, API keys, or database connection strings.

Use `.env.example` files to document the required variable names without including secret values.

## Future Enhancements

- AI-powered marketing assistant
- Advanced customer segmentation
- Improved churn prediction models
- Campaign performance analytics
- Real-time customer behavior insights
- Production deployment and monitoring

## Project Status

Active development.

## Author

**Pavankalyan Madiga**

GitHub: [Pavankalyan-Madiga](https://github.com/Pavankalyan-Madiga)

Project Repository: [MarketIQ](https://github.com/Pavankalyan-Madiga/MarketIQ)

---

*MarketIQ — Turning Customer Data into Business Intelligence.*
