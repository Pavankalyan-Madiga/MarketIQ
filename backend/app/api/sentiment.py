
from collections import Counter, defaultdict
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.database.connection import engine


router = APIRouter(
    prefix="/api/v1/sentiment",
    tags=["Sentiment Analysis"]
)

analyzer = SentimentIntensityAnalyzer()


# ==========================================
# SENTIMENT CLASSIFICATION
# ==========================================

def classify_sentiment(review_text: Optional[str]):
    if not review_text or not review_text.strip():
        return {
            "sentiment": "Neutral",
            "compound_score": 0.0
        }

    scores = analyzer.polarity_scores(review_text)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "compound_score": round(compound, 4)
    }


def classify_rating(rating):
    if rating is None:
        return None

    if rating >= 4:
        return "Positive"
    elif rating <= 2:
        return "Negative"

    return "Neutral"


# ==========================================
# DATABASE
# ==========================================

def fetch_reviews():
    query = text("""
        SELECT
            review_id,
            order_id,
            customer_id,
            rating,
            review_text,
            review_date
        FROM reviews
        ORDER BY review_date DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        return [dict(row._mapping) for row in result]


def analyze_review(review):
    text_value = review.get("review_text") or ""

    result = classify_sentiment(text_value)
    rating_sentiment = classify_rating(review.get("rating"))

    return {
        "review_id": review["review_id"],
        "order_id": review["order_id"],
        "customer_id": review["customer_id"],
        "rating": review["rating"],
        "review_text": text_value,
        "review_date": review["review_date"],
        "sentiment": result["sentiment"],
        "compound_score": result["compound_score"],
        "rating_sentiment": rating_sentiment,
        "sentiment_agreement": (
            result["sentiment"] == rating_sentiment
            if rating_sentiment is not None
            else None
        )
    }


def get_analyzed_reviews():
    reviews = fetch_reviews()
    return [analyze_review(review) for review in reviews]


# ==========================================
# HEALTH CHECK
# ==========================================

@router.get("/health")
def sentiment_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database_connected": True,
            "sentiment_engine": "VADER"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# SENTIMENT SUMMARY
# ==========================================

@router.get("/summary")
def sentiment_summary():
    try:
        reviews = get_analyzed_reviews()

        total = len(reviews)

        counts = Counter(
            review["sentiment"] for review in reviews
        )

        positive = counts.get("Positive", 0)
        negative = counts.get("Negative", 0)
        neutral = counts.get("Neutral", 0)

        ratings = [
            review["rating"]
            for review in reviews
            if review["rating"] is not None
        ]

        average_rating = (
            round(sum(ratings) / len(ratings), 2)
            if ratings else 0
        )

        agreement_values = [
            review["sentiment_agreement"]
            for review in reviews
            if review["sentiment_agreement"] is not None
        ]

        agreement_percentage = (
            round(
                sum(agreement_values) / len(agreement_values) * 100,
                2
            )
            if agreement_values else 0
        )

        def percentage(value):
            return round(value / total * 100, 2) if total else 0

        return {
            "total_reviews": total,
            "positive_reviews": positive,
            "negative_reviews": negative,
            "neutral_reviews": neutral,
            "positive_percentage": percentage(positive),
            "negative_percentage": percentage(negative),
            "neutral_percentage": percentage(neutral),
            "average_rating": average_rating,
            "rating_sentiment_agreement": agreement_percentage
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# SENTIMENT DISTRIBUTION
# ==========================================

@router.get("/distribution")
def sentiment_distribution():
    try:
        reviews = get_analyzed_reviews()

        counts = Counter(
            review["sentiment"] for review in reviews
        )

        total = len(reviews)

        return {
            "total_reviews": total,
            "distribution": [
                {
                    "sentiment": sentiment,
                    "count": counts.get(sentiment, 0),
                    "percentage": round(
                        counts.get(sentiment, 0) / total * 100,
                        2
                    ) if total else 0
                }
                for sentiment in ["Positive", "Negative", "Neutral"]
            ]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# SENTIMENT TRENDS
# ==========================================

@router.get("/trends")
def sentiment_trends():
    try:
        reviews = get_analyzed_reviews()

        monthly_data = defaultdict(
            lambda: {
                "Positive": 0,
                "Negative": 0,
                "Neutral": 0
            }
        )

        for review in reviews:
            review_date = review.get("review_date")

            try:
                parsed_date = date.fromisoformat(str(review_date))
                month = parsed_date.strftime("%Y-%m")
            except (ValueError, TypeError):
                continue

            monthly_data[month][review["sentiment"]] += 1

        trends = [
            {
                "month": month,
                "positive": values["Positive"],
                "negative": values["Negative"],
                "neutral": values["Neutral"],
                "total": sum(values.values())
            }
            for month, values in sorted(monthly_data.items())
        ]

        return {
            "trends": trends
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================
# REVIEW-LEVEL SENTIMENT RESULTS
# ==========================================

@router.get("/reviews")
def sentiment_reviews(
    search: str = "",
    sentiment: str = "",
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    try:
        reviews = get_analyzed_reviews()

        if sentiment:
            normalized_sentiment = sentiment.strip().capitalize()

            if normalized_sentiment not in [
                "Positive", "Negative", "Neutral"
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid sentiment. Use Positive, Negative or Neutral."
                )

            reviews = [
                review for review in reviews
                if review["sentiment"] == normalized_sentiment
            ]

        if search:
            search_value = search.lower()

            reviews = [
                review for review in reviews
                if search_value in str(review["customer_id"]).lower()
                or search_value in str(review["review_text"]).lower()
                or search_value in str(review["review_id"]).lower()
            ]

        total = len(reviews)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "reviews": reviews[offset:offset + limit]
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
