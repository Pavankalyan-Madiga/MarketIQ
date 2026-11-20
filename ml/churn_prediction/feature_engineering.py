
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found. Check backend/.env"
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ==================================================
# 2. FEATURE ENGINEERING QUERY
# ==================================================

FEATURE_QUERY = """
WITH order_features AS (

    SELECT
        customer_id,

        COUNT(*) AS total_orders,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(status)) = 'cancelled'
        ) AS cancelled_orders,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(status)) = 'returned'
        ) AS returned_orders,

        COUNT(*) FILTER (
            WHERE LOWER(TRIM(status)) = 'delivered'
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
        SUM(oi.total_price) AS order_amount,
        SUM(oi.quantity) AS order_quantity

    FROM orders o

    LEFT JOIN order_items oi
        ON o.order_id = oi.order_id

    GROUP BY
        o.customer_id,
        o.order_id
),

purchase_features AS (

    SELECT
        customer_id,

        SUM(order_quantity) AS total_quantity,

        SUM(order_amount) AS total_spending,

        AVG(order_amount) AS avg_order_value

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

        AVG(rating) AS avg_rating

    FROM reviews
    GROUP BY customer_id
)

SELECT

    c.customer_id,

    -- Customer information
    c.age,
    c.gender,
    c.membership,
    c.city,

    -- Order information
    COALESCE(ordf.total_orders, 0) AS total_orders,

    COALESCE(ordf.cancelled_orders, 0)
        AS cancelled_orders,

    COALESCE(ordf.returned_orders, 0)
        AS returned_orders,

    COALESCE(ordf.delivered_orders, 0)
        AS delivered_orders,

    COALESCE(ordf.payment_method_count, 0)
        AS payment_method_count,

    COALESCE(
        CURRENT_DATE - ordf.last_order_date,
        -1
    ) AS days_since_last_order,

    -- Purchase information
    COALESCE(pf.total_quantity, 0)
        AS total_quantity,

    COALESCE(pf.total_spending, 0)
        AS total_spending,

    COALESCE(pf.avg_order_value, 0)
        AS avg_order_value,

    -- Interaction information
    COALESCE(inf.total_interactions, 0)
        AS total_interactions,

    COALESCE(inf.email_click_count, 0)
        AS email_click_count,

    COALESCE(inf.email_open_count, 0)
        AS email_open_count,

    COALESCE(inf.product_view_count, 0)
        AS product_view_count,

    COALESCE(inf.website_visit_count, 0)
        AS website_visit_count,

    COALESCE(inf.add_to_cart_count, 0)
        AS add_to_cart_count,

    COALESCE(inf.interaction_purchase_count, 0)
        AS interaction_purchase_count,

    -- Review information
    COALESCE(rf.review_count, 0)
        AS review_count,

    COALESCE(rf.avg_rating, 0)
        AS avg_rating,

    -- Target
    cl.churn_label

FROM customers c

JOIN churn_labels cl
    ON c.customer_id = cl.customer_id

LEFT JOIN order_features ordf
    ON c.customer_id = ordf.customer_id

LEFT JOIN purchase_features pf
    ON c.customer_id = pf.customer_id

LEFT JOIN interaction_features inf
    ON c.customer_id = inf.customer_id

LEFT JOIN review_features rf
    ON c.customer_id = rf.customer_id

ORDER BY c.customer_id;
"""


# ==================================================
# 3. GENERATE FEATURE DATASET
# ==================================================

def generate_features():

    print("\nConnecting to PostgreSQL...")

    with engine.connect() as connection:

        df = pd.read_sql(
            text(FEATURE_QUERY),
            connection
        )

    print("\nFeature engineering completed.")

    return df


# ==================================================
# 4. VALIDATE FEATURE DATASET
# ==================================================

def validate_features(df):

    print("\n========== DATASET VALIDATION ==========")

    print("Dataset shape:", df.shape)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nDuplicate customer IDs:")
    print(df["customer_id"].duplicated().sum())

    print("\nTarget distribution:")
    print(df["churn_label"].value_counts())

    interaction_columns = [
        "email_click_count",
        "email_open_count",
        "product_view_count",
        "website_visit_count",
        "add_to_cart_count",
        "interaction_purchase_count"
    ]

    print("\nInteraction feature totals:")

    print(
        df[interaction_columns]
        .sum()
        .to_string()
    )

    if len(df) != 5000:
        raise ValueError(
            f"Expected 5000 customers, found {len(df)}"
        )

    if df["customer_id"].duplicated().any():
        raise ValueError(
            "Duplicate customer IDs detected."
        )

    if df["churn_label"].isnull().any():
        raise ValueError(
            "Missing churn labels detected."
        )

    if not df["churn_label"].isin([0, 1]).all():
        raise ValueError(
            "Invalid churn labels. Expected only 0 and 1."
        )

    if df.isnull().any().any():
        raise ValueError(
            "Missing values detected in feature dataset."
        )

    print("\nAll validation checks passed.")


# ==================================================
# 5. SAVE FEATURE DATASET
# ==================================================

def save_features(df):

    output_dir = (
        PROJECT_ROOT
        / "datasets"
        / "processed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "churn_features.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nFeature dataset saved successfully.")

    print("File:", output_file)


# ==================================================
# 6. MAIN
# ==================================================

def main():

    try:

        df = generate_features()

        validate_features(df)

        save_features(df)

        print("\nFeature engineering pipeline finished.")

    except Exception as error:

        print("\nFeature engineering failed:")
        print(error)

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":
    main()
