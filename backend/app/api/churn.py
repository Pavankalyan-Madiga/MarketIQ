
from pathlib import Path
import json

import joblib
import pandas as pd

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from app.database.connection import engine


router = APIRouter(
    prefix="/api/v1/churn",
    tags=["Churn Prediction"],
)


# --------------------------------------------------
# MODEL PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = PROJECT_ROOT / "models" / "churn" / "best_churn_model.joblib"
METRICS_PATH = PROJECT_ROOT / "models" / "churn" / "best_model_metrics.json"

_model = None


def get_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail="Trained churn model not found.",
            )

        _model = joblib.load(MODEL_PATH)

    return _model


# --------------------------------------------------
# FEATURE QUERY
# Must match the training feature engineering logic.
# --------------------------------------------------

FEATURE_QUERY = text("""
WITH order_features AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,

        COUNT(*) FILTER (
            WHERE LOWER(status) = 'cancelled'
        ) AS cancelled_orders,

        COUNT(*) FILTER (
            WHERE LOWER(status) = 'returned'
        ) AS returned_orders,

        COUNT(*) FILTER (
            WHERE LOWER(status) = 'delivered'
        ) AS delivered_orders,

        COUNT(DISTINCT payment_method) AS payment_method_count,

        MAX(order_date::DATE) AS last_order_date

    FROM orders
    GROUP BY customer_id
),

order_amounts AS (
    SELECT
        o.customer_id,
        o.order_id,
        SUM(oi.total_price::NUMERIC) AS order_amount,
        SUM(oi.quantity::NUMERIC) AS order_quantity

    FROM orders o
    JOIN order_items oi
        ON oi.order_id = o.order_id

    GROUP BY o.customer_id, o.order_id
),

purchase_features AS (
    SELECT
        customer_id,
        COALESCE(SUM(order_quantity), 0) AS total_quantity,
        COALESCE(SUM(order_amount), 0) AS total_spending,
        COALESCE(AVG(order_amount), 0) AS avg_order_value

    FROM order_amounts
    GROUP BY customer_id
),

interaction_features AS (
    SELECT
        customer_id,

        COUNT(*) AS total_interactions,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'email click'
        ) AS email_click_count,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'email open'
        ) AS email_open_count,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'product view'
        ) AS product_view_count,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'website visit'
        ) AS website_visit_count,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'add to cart'
        ) AS add_to_cart_count,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(interaction_type)) = 'purchase'
        ) AS interaction_purchase_count

    FROM interactions
    GROUP BY customer_id
),

review_features AS (
    SELECT
        customer_id,
        COUNT(*) AS review_count,
        AVG(rating::NUMERIC) AS avg_rating

    FROM reviews
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.age::NUMERIC AS age,
    c.gender,
    c.membership,
    c.city,

    COALESCE(o.cancelled_orders, 0) AS cancelled_orders,
    COALESCE(o.returned_orders, 0) AS returned_orders,
    COALESCE(o.delivered_orders, 0) AS delivered_orders,
    COALESCE(o.payment_method_count, 0) AS payment_method_count,

    COALESCE(
        CURRENT_DATE - o.last_order_date,
        -1
    ) AS days_since_last_order,

    COALESCE(p.total_quantity, 0) AS total_quantity,
    COALESCE(p.total_spending, 0) AS total_spending,
    COALESCE(p.avg_order_value, 0) AS avg_order_value,

    COALESCE(i.total_interactions, 0) AS total_interactions,
    COALESCE(i.email_click_count, 0) AS email_click_count,
    COALESCE(i.email_open_count, 0) AS email_open_count,
    COALESCE(i.product_view_count, 0) AS product_view_count,
    COALESCE(i.website_visit_count, 0) AS website_visit_count,
    COALESCE(i.add_to_cart_count, 0) AS add_to_cart_count,
    COALESCE(i.interaction_purchase_count, 0) AS interaction_purchase_count,

    COALESCE(r.review_count, 0) AS review_count,
    COALESCE(r.avg_rating, 0) AS avg_rating

FROM customers c

LEFT JOIN order_features o
    ON c.customer_id = o.customer_id

LEFT JOIN purchase_features p
    ON c.customer_id = p.customer_id

LEFT JOIN interaction_features i
    ON c.customer_id = i.customer_id

LEFT JOIN review_features r
    ON c.customer_id = r.customer_id
""")


# --------------------------------------------------
# FETCH CUSTOMER FEATURES
# --------------------------------------------------

def get_customer_features(customer_id=None):

    query = FEATURE_QUERY

    params = {}

    if customer_id:
        query = text(
            FEATURE_QUERY.text
            + "\nWHERE c.customer_id = :customer_id"
        )
        params["customer_id"] = customer_id

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            params,
        ).mappings().all()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame([dict(row) for row in rows])

    # Keep the same feature names and numeric types
    # used during model training.
    numeric_columns = [
        "age",
        "cancelled_orders",
        "returned_orders",
        "delivered_orders",
        "payment_method_count",
        "days_since_last_order",
        "total_quantity",
        "total_spending",
        "avg_order_value",
        "total_interactions",
        "email_click_count",
        "email_open_count",
        "product_view_count",
        "website_visit_count",
        "add_to_cart_count",
        "interaction_purchase_count",
        "review_count",
        "avg_rating",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df[numeric_columns] = df[numeric_columns].fillna(0)

    return df


# --------------------------------------------------
# PREDICTION LOGIC
# --------------------------------------------------

def make_predictions(df):

    if df.empty:
        return []

    customer_ids = df["customer_id"].tolist()

    # The model was trained without these columns.
    X = df.drop(columns=["customer_id"])

    trained_model = get_model()

    predictions = trained_model.predict(X)
    probabilities = trained_model.predict_proba(X)[:, 1]

    results = []

    for customer_id, prediction, probability in zip(
        customer_ids,
        predictions,
        probabilities,
    ):

        probability = float(probability)
        risk_percentage = round(probability * 100, 2)

        if risk_percentage >= 70:
            risk_level = "High"
        elif risk_percentage >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        results.append({
            "customer_id": customer_id,
            "churn_prediction": int(prediction),
            "churn_status": (
                "Likely to Churn"
                if int(prediction) == 1
                else "Not Likely to Churn"
            ),
            "churn_probability": risk_percentage,
            "risk_level": risk_level,
        })

    return results


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@router.get("/health")
def churn_health():

    return {
        "status": "healthy",
        "model_exists": MODEL_PATH.exists(),
        "model_loaded": _model is not None,
    }


# --------------------------------------------------
# MODEL INFORMATION
# --------------------------------------------------

@router.get("/model-info")
def model_info():

    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found.",
        )

    with open(METRICS_PATH, "r") as file:
        metrics = json.load(file)

    return metrics


# --------------------------------------------------
# CUSTOMER PREDICTION
# --------------------------------------------------

@router.get("/customers/{customer_id}")
def predict_customer_churn(customer_id: str):

    try:
        df = get_customer_features(customer_id)

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="Customer not found.",
            )

        predictions = make_predictions(df)

        return {
            "success": True,
            "prediction": predictions[0],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# --------------------------------------------------
# ALL CUSTOMER PREDICTIONS
# --------------------------------------------------

@router.get("/customers")
def predict_all_customers(
    risk_level: str = Query(
        default="",
        description="Filter by High, Medium or Low",
    ),
    limit: int = Query(default=5000, ge=1, le=5000),
):

    try:
        df = get_customer_features()

        predictions = make_predictions(df)

        if risk_level:
            allowed = {"high", "medium", "low"}

            if risk_level.lower() not in allowed:
                raise HTTPException(
                    status_code=400,
                    detail="Risk level must be High, Medium or Low.",
                )

            predictions = [
                item for item in predictions
                if item["risk_level"].lower() == risk_level.lower()
            ]

        total = len(predictions)

        return {
            "success": True,
            "total_customers": total,
            "predictions": predictions[:limit],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# --------------------------------------------------
# CHURN SUMMARY
# --------------------------------------------------

@router.get("/summary")
def churn_summary():

    try:
        df = get_customer_features()

        predictions = make_predictions(df)

        high = sum(
            item["risk_level"] == "High"
            for item in predictions
        )

        medium = sum(
            item["risk_level"] == "Medium"
            for item in predictions
        )

        low = sum(
            item["risk_level"] == "Low"
            for item in predictions
        )

        predicted_churn = sum(
            item["churn_prediction"] == 1
            for item in predictions
        )

        total = len(predictions)

        return {
            "total_customers": total,
            "predicted_churn_customers": predicted_churn,
            "high_risk_customers": high,
            "medium_risk_customers": medium,
            "low_risk_customers": low,
            "predicted_churn_percentage": round(
                predicted_churn / total * 100,
                2,
            ) if total else 0,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
