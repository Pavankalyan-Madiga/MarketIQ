from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from app.api.sentiment import router as sentiment_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from pathlib import Path
from datetime import datetime
import csv
import io
import re
import uuid
import os
import time
from threading import Lock
from app.database.connection import engine, test_connection
from app.api.churn import router as churn_router


app = FastAPI(
    title="Customer Behavior & Marketing Intelligence",
    description="Customer analytics platform using synthetic datasets",
    version="1.0.0",
)

app.include_router(churn_router)
app.include_router(sentiment_router)

# CORS Configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# SHORT-LIVED API CACHES
# ---------------------------------------------------------------------------
# Each endpoint has its own lock so concurrent cache misses on different
# dashboard endpoints do not block one another.
DASHBOARD_CACHE_TTL = 60
RECOMMENDATION_SCHEMA_CACHE_TTL = 300

_dashboard_stats_cache = {"data": None, "created_at": 0}
_dashboard_revenue_cache = {"data": None, "created_at": 0}
_dashboard_segments_cache = {"data": None, "created_at": 0}

_dashboard_stats_lock = Lock()
_dashboard_revenue_lock = Lock()
_dashboard_segments_lock = Lock()

_recommendation_schema_cache = {"data": None, "created_at": 0}
_recommendation_schema_lock = Lock()


def get_cached_value(cache, cache_lock, ttl, loader):
    """Return a cached value or load and cache it safely."""
    with cache_lock:
        now = time.monotonic()
        if (
            cache["data"] is not None
            and now - cache["created_at"] < ttl
        ):
            return cache["data"]

        value = loader()
        cache["data"] = value
        cache["created_at"] = time.monotonic()
        return value

@app.get("/")
def home():
    return {
        "message": "Customer Marketing Intelligence API",
        "status": "running",
    }


@app.get("/api/v1/health")
def health():
    try:
        test_connection()

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(exc)}",
        )


@app.get("/api/v1/dashboard/stats")
def dashboard_stats():
    def load_stats():
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT
                    (
                        SELECT COALESCE(SUM(oi.total_price::NUMERIC), 0)
                        FROM order_items oi
                        JOIN orders o ON o.order_id = oi.order_id
                        WHERE o.status = 'Delivered'
                    ) AS total_revenue,
                    (SELECT COUNT(*) FROM customers) AS total_customers,
                    (SELECT COUNT(*) FROM orders) AS total_orders,
                    (
                        SELECT COUNT(*)
                        FROM customers
                        WHERE signup_date::DATE >=
                            CURRENT_DATE - INTERVAL '30 days'
                    ) AS new_customers
            """)).mappings().one()

        return {
            "total_revenue": float(result["total_revenue"]),
            "total_customers": result["total_customers"],
            "total_orders": result["total_orders"],
            "new_customers": result["new_customers"],
            "currency": "INR",
        }

    try:
        return get_cached_value(
            _dashboard_stats_cache,
            _dashboard_stats_lock,
            DASHBOARD_CACHE_TTL,
            load_stats,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/dashboard/revenue")
def dashboard_revenue():
    def load_revenue():
        with engine.connect() as connection:
            rows = connection.execute(text("""
                SELECT
                    TO_CHAR(
                        DATE_TRUNC('month', o.order_date::DATE),
                        'Mon YYYY'
                    ) AS month,
                    DATE_TRUNC(
                        'month',
                        o.order_date::DATE
                    ) AS month_date,
                    COALESCE(
                        SUM(oi.total_price::NUMERIC),
                        0
                    ) AS revenue
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.status = 'Delivered'
                  AND o.order_date::DATE >=
                      CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', o.order_date::DATE)
                ORDER BY month_date
            """)).mappings().all()

        return [
            {
                "month": row["month"],
                "revenue": float(row["revenue"]),
            }
            for row in rows
        ]

    try:
        return get_cached_value(
            _dashboard_revenue_cache,
            _dashboard_revenue_lock,
            DASHBOARD_CACHE_TTL,
            load_revenue,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/dashboard/segments")
def dashboard_segments():
    def load_segments():
        with engine.connect() as connection:
            rows = connection.execute(text("""
                SELECT
                    CASE
                        WHEN order_count >= 5 THEN 'Frequent Buyers'
                        WHEN order_count BETWEEN 2 AND 4 THEN 'Returning Buyers'
                        ELSE 'One-time Buyers'
                    END AS name,
                    COUNT(*) AS value
                FROM (
                    SELECT
                        c.customer_id,
                        COUNT(o.order_id) AS order_count
                    FROM customers c
                    LEFT JOIN orders o
                        ON o.customer_id = c.customer_id
                        AND o.status = 'Delivered'
                    GROUP BY c.customer_id
                ) customer_orders
                GROUP BY name
                ORDER BY value DESC
            """)).mappings().all()

        return [
            {
                "name": row["name"],
                "value": row["value"],
            }
            for row in rows
        ]

    try:
        return get_cached_value(
            _dashboard_segments_cache,
            _dashboard_segments_lock,
            DASHBOARD_CACHE_TTL,
            load_segments,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/customers")
def get_customers(
    search: str = Query(default="", max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    """Return a paginated customer list, cached briefly by its filters."""
    try:
        normalized_search = search.strip()
        cache_key = (normalized_search.casefold(), page, page_size)

        def load_customers():
            offset = (page - 1) * page_size
            search_pattern = f"%{normalized_search}%"

            with engine.connect() as connection:
                total = connection.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM customers
                        WHERE
                            name ILIKE :search
                            OR email ILIKE :search
                            OR city ILIKE :search
                    """),
                    {"search": search_pattern},
                ).scalar_one()

                rows = connection.execute(
                    text("""
                        SELECT
                            customer_id,
                            name,
                            age,
                            gender,
                            city,
                            membership,
                            signup_date,
                            email
                        FROM customers
                        WHERE
                            name ILIKE :search
                            OR email ILIKE :search
                            OR city ILIKE :search
                        ORDER BY signup_date DESC, customer_id
                        LIMIT :limit
                        OFFSET :offset
                    """),
                    {
                        "search": search_pattern,
                        "limit": page_size,
                        "offset": offset,
                    },
                ).mappings().all()

            total_pages = (total + page_size - 1) // page_size
            return {
                "customers": [dict(row) for row in rows],
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                },
            }

        return get_cached_key(
            _customers_list_cache,
            _customers_list_cache_lock,
            RECOMMENDATION_CACHE_TTL,
            cache_key,
            load_customers,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.get("/api/v1/customers/{customer_id}")
def get_customer(customer_id: str):
    try:
        with engine.connect() as connection:
            customer = connection.execute(
                text("""
                    SELECT
                        customer_id,
                        name,
                        age,
                        gender,
                        city,
                        membership,
                        signup_date,
                        email
                    FROM customers
                    WHERE customer_id = :customer_id
                """),
                {"customer_id": customer_id},
            ).mappings().first()

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found",
            )

        return dict(customer)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


RFM_QUERY = """
WITH order_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS frequency,
        MAX(order_date::DATE) AS last_order_date
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
),
spend_metrics AS (
    SELECT
        o.customer_id,
        COALESCE(SUM(oi.total_price::NUMERIC), 0) AS monetary
    FROM orders o
    JOIN order_items oi
        ON oi.order_id = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY o.customer_id
),
base AS (
    SELECT
        c.customer_id,
        c.name,
        c.email,
        c.city,
        COALESCE(om.frequency, 0) AS frequency,
        COALESCE(sm.monetary, 0) AS monetary,
        om.last_order_date,
        CASE
            WHEN om.last_order_date IS NOT NULL
                THEN CURRENT_DATE - om.last_order_date
            ELSE NULL
        END AS recency_days
    FROM customers c
    LEFT JOIN order_metrics om
        ON om.customer_id = c.customer_id
    LEFT JOIN spend_metrics sm
        ON sm.customer_id = c.customer_id
),
active_scores AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM base
    WHERE frequency > 0
),
scored AS (
    SELECT
        b.*,
        COALESCE(s.r_score, 1) AS recency_score,
        COALESCE(s.f_score, 1) AS frequency_score,
        COALESCE(s.m_score, 1) AS monetary_score
    FROM base b
    LEFT JOIN active_scores s
        ON b.customer_id = s.customer_id
)
SELECT
    *,
    recency_score + frequency_score + monetary_score AS rfm_score,
    CASE
        WHEN frequency = 0 THEN 'No Delivered Orders'
        WHEN recency_score >= 4
            AND frequency_score >= 4
            AND monetary_score >= 4
            THEN 'Champions'
        WHEN frequency_score >= 4
            AND recency_score >= 3
            THEN 'Loyal Customers'
        WHEN recency_score >= 4
            AND frequency_score >= 2
            THEN 'Potential Loyalists'
        WHEN recency_score >= 4
            AND frequency_score = 1
            THEN 'Recent Customers'
        WHEN recency_score <= 2
            AND frequency_score >= 3
            THEN 'At Risk'
        WHEN recency_score <= 2
            AND frequency_score <= 2
            THEN 'Hibernating'
        ELSE 'Needs Attention'
    END AS segment
FROM scored
"""


# Cache RFM records so summary, distribution, and customer endpoints
# can reuse the same calculation for five minutes.
_rfm_cache = {
    "data": None,
    "created_at": 0,
}
_rfm_cache_lock = Lock()
RFM_CACHE_TTL = 300  # 5 minutes


def get_rfm_records():
    with _rfm_cache_lock:
        current_time = time.monotonic()

        if (
            _rfm_cache["data"] is not None
            and current_time - _rfm_cache["created_at"] < RFM_CACHE_TTL
        ):
            return _rfm_cache["data"]

        with engine.connect() as connection:
            rows = connection.execute(
                text(RFM_QUERY)
            ).mappings().all()

        records = [dict(row) for row in rows]
        _rfm_cache["data"] = records
        _rfm_cache["created_at"] = time.monotonic()

        return records


@app.get("/api/v1/segmentation/summary")
def segmentation_summary():
    try:
        records = get_rfm_records()

        active_customers = [
            row for row in records if row["frequency"] > 0
        ]

        total_revenue = sum(
            float(row["monetary"]) for row in records
        )

        average_recency = (
            sum(row["recency_days"] for row in active_customers)
            / len(active_customers)
            if active_customers else 0
        )

        return {
            "total_customers": len(records),
            "active_customers": len(active_customers),
            "inactive_customers": len(records) - len(active_customers),
            "total_revenue": round(total_revenue, 2),
            "average_recency_days": round(average_recency, 2),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/segmentation/distribution")
def segmentation_distribution():
    try:
        records = get_rfm_records()
        distribution = {}

        for row in records:
            segment = row["segment"]

            if segment not in distribution:
                distribution[segment] = {
                    "name": segment,
                    "customer_count": 0,
                    "revenue": 0,
                }

            distribution[segment]["customer_count"] += 1
            distribution[segment]["revenue"] += float(row["monetary"])

        result = list(distribution.values())

        for item in result:
            item["revenue"] = round(item["revenue"], 2)
            item["percentage"] = round(
                item["customer_count"] / len(records) * 100, 2
            ) if records else 0

        return sorted(
            result,
            key=lambda item: item["customer_count"],
            reverse=True,
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/segmentation/customers")
def segmentation_customers(
    segment: str = Query(default=""),
    search: str = Query(default="", max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    try:
        records = get_rfm_records()

        if segment:
            records = [
                row for row in records
                if row["segment"].lower() == segment.strip().lower()
            ]

        if search.strip():
            keyword = search.strip().lower()

            records = [
                row for row in records
                if keyword in row["name"].lower()
                or keyword in row["email"].lower()
                or keyword in row["city"].lower()
                or keyword in row["customer_id"].lower()
            ]

        total = len(records)
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        paginated_records = records[offset:offset + page_size]

        return {
            "customers": [
                {
                    **row,
                    "monetary": round(float(row["monetary"]), 2),
                    "last_order_date": (
                        row["last_order_date"].isoformat()
                        if row["last_order_date"] else None
                    ),
                }
                for row in paginated_records
            ],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            },
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))



# ---------------------------------------------------------------------------
# RULE-BASED PRODUCT RECOMMENDATIONS (NO ML / AI)
# ---------------------------------------------------------------------------

def _table_columns(connection, table_name: str):
    rows = connection.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = :table_name
    """), {"table_name": table_name}).scalars().all()
    return set(rows)


def _first_column(columns, candidates, table_name):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise HTTPException(
        status_code=500,
        detail=f"Could not find a supported column in {table_name}. Tried: {', '.join(candidates)}",
    )


def _recommendation_schema(connection):
    def load_schema():
        products = _table_columns(connection, "products")
        items = _table_columns(connection, "order_items")
        orders = _table_columns(connection, "orders")
        product_name = _first_column(
            products, ("product_name", "name", "title"), "products"
        )
        category = next(
            (c for c in ("category", "product_category") if c in products),
            None,
        )
        brand = next(
            (c for c in ("brand", "manufacturer") if c in products),
            None,
        )
        quantity = next(
            (c for c in ("quantity", "qty") if c in items),
            None,
        )
        unit_price = next(
            (c for c in ("unit_price", "price") if c in items),
            None,
        )
        total_price = "total_price" if "total_price" in items else None

        return {
            "product_name": product_name,
            "category": category,
            "brand": brand,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "has_status": "status" in orders,
        }

    return get_cached_value(
        _recommendation_schema_cache,
        _recommendation_schema_lock,
        RECOMMENDATION_SCHEMA_CACHE_TTL,
        load_schema,
    )


# Cache computed recommendation results as well as schema metadata.
# Results are short-lived because order/product data may change.
RECOMMENDATION_CACHE_TTL = 60
_recommendation_summary_cache = {}
_popular_products_cache = {}
_customer_recommendations_cache = {}
_frequently_bought_cache = {}
_customers_list_cache = {}
_recommendation_summary_lock = Lock()
_popular_products_lock = Lock()
_customer_recommendations_lock = Lock()
_frequently_bought_lock = Lock()
_customers_list_cache_lock = Lock()


def get_cached_key(cache, cache_lock, ttl, key, loader):
    """Cache a result by request key, with a small bounded cache."""
    with cache_lock:
        now = time.monotonic()
        entry = cache.get(key)
        if entry is not None and now - entry["created_at"] < ttl:
            return entry["data"]

        value = loader()
        # Remove expired entries and cap memory use for customer-specific keys.
        expired = [
            cache_key for cache_key, cached in cache.items()
            if now - cached["created_at"] >= ttl
        ]
        for cache_key in expired:
            cache.pop(cache_key, None)
        if len(cache) >= 200:
            oldest_key = min(cache, key=lambda item: cache[item]["created_at"])
            cache.pop(oldest_key, None)
        cache[key] = {"data": value, "created_at": time.monotonic()}
        return value


def _load_recommendation_summary():
    with engine.connect() as connection:
        schema = _recommendation_schema(connection)
        status_filter = "WHERE o.status = 'Delivered'" if schema["has_status"] else ""
        row = connection.execute(text(f"""
            SELECT
                COUNT(DISTINCT p.product_id) AS total_products,
                COUNT(DISTINCT oi.order_id) AS orders_with_products,
                COALESCE(SUM({f"NULLIF(oi.{schema['quantity']}::TEXT, '')::NUMERIC" if schema['quantity'] else '1'}), 0) AS units_sold
            FROM products p
            JOIN order_items oi ON oi.product_id = p.product_id
            JOIN orders o ON o.order_id = oi.order_id
            {status_filter}
        """)).mappings().one()
    return {key: int(value or 0) for key, value in row.items()}


@app.get("/api/v1/recommendations/summary")
def recommendation_summary():
    try:
        return get_cached_key(
            _recommendation_summary_cache,
            _recommendation_summary_lock,
            RECOMMENDATION_CACHE_TTL,
            "summary",
            _load_recommendation_summary,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _load_popular_products(limit: int):
    with engine.connect() as connection:
        schema = _recommendation_schema(connection)
        category_select = f"p.{schema['category']}" if schema["category"] else "NULL"
        brand_select = f"p.{schema['brand']}" if schema["brand"] else "NULL"
        quantity_expr = f"SUM(NULLIF(oi.{schema['quantity']}::TEXT, '')::NUMERIC)" if schema["quantity"] else "COUNT(*)"
        if schema["total_price"]:
            revenue_expr = f"SUM(NULLIF(oi.{schema['total_price']}::TEXT, '')::NUMERIC)"
        elif schema["unit_price"] and schema["quantity"]:
            revenue_expr = f"SUM(NULLIF(oi.{schema['unit_price']}::TEXT, '')::NUMERIC * NULLIF(oi.{schema['quantity']}::TEXT, '')::NUMERIC)"
        else:
            revenue_expr = "0"
        status_filter = "WHERE o.status = 'Delivered'" if schema["has_status"] else ""
        rows = connection.execute(text(f"""
            SELECT p.product_id, p.{schema['product_name']} AS product_name,
                   {category_select} AS category, {brand_select} AS brand,
                   COUNT(DISTINCT o.order_id) AS order_count,
                   {quantity_expr} AS units_sold,
                   {revenue_expr} AS revenue
            FROM products p
            JOIN order_items oi ON oi.product_id = p.product_id
            JOIN orders o ON o.order_id = oi.order_id
            {status_filter}
            GROUP BY p.product_id, p.{schema['product_name']}
                     {f", p.{schema['category']}" if schema['category'] else ""}
                     {f", p.{schema['brand']}" if schema['brand'] else ""}
            ORDER BY units_sold DESC, order_count DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()
    return [
        {**dict(row), "units_sold": int(row["units_sold"] or 0),
         "order_count": int(row["order_count"] or 0),
         "revenue": float(row["revenue"] or 0)}
        for row in rows
    ]


@app.get("/api/v1/recommendations/popular")
def popular_products(limit: int = Query(default=10, ge=1, le=50)):
    try:
        return get_cached_key(
            _popular_products_cache, _popular_products_lock,
            RECOMMENDATION_CACHE_TTL, limit,
            lambda: _load_popular_products(limit),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _load_customer_product_recommendations(customer_id: str, limit: int):
    with engine.connect() as connection:
        schema = _recommendation_schema(connection)
        customer = connection.execute(text(
            "SELECT customer_id, name FROM customers WHERE customer_id = :customer_id"
        ), {"customer_id": customer_id}).mappings().first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")
        if not schema["category"]:
            raise HTTPException(status_code=400, detail="Product category column is required for customer-based recommendations.")
        quantity_expr = f"SUM(NULLIF(oi.{schema['quantity']}::TEXT, '')::NUMERIC)" if schema["quantity"] else "COUNT(*)"
        status_filter = "AND o.status = 'Delivered'" if schema["has_status"] else ""
        popularity_filter = "WHERE o.status = 'Delivered'" if schema["has_status"] else ""
        rows = connection.execute(text(f"""
            WITH customer_categories AS (
                SELECT p.{schema['category']} AS category, COUNT(*) AS preference
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.order_id
                JOIN products p ON p.product_id = oi.product_id
                WHERE o.customer_id = :customer_id {status_filter}
                GROUP BY p.{schema['category']}
                ORDER BY preference DESC
                LIMIT 3
            ), purchased AS (
                SELECT DISTINCT oi.product_id
                FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.customer_id = :customer_id
            ), popularity AS (
                SELECT oi.product_id, {quantity_expr} AS units_sold,
                       COUNT(DISTINCT o.order_id) AS order_count
                FROM order_items oi JOIN orders o ON o.order_id = oi.order_id
                {popularity_filter}
                GROUP BY oi.product_id
            )
            SELECT p.product_id, p.{schema['product_name']} AS product_name,
                   p.{schema['category']} AS category,
                   pop.units_sold, pop.order_count
            FROM products p
            JOIN customer_categories cc ON cc.category = p.{schema['category']}
            JOIN popularity pop ON pop.product_id = p.product_id
            WHERE p.product_id NOT IN (SELECT product_id FROM purchased)
            ORDER BY cc.preference DESC, pop.units_sold DESC
            LIMIT :limit
        """), {"customer_id": customer_id, "limit": limit}).mappings().all()
    return {
        "customer": dict(customer),
        "recommendations": [
            {**dict(row), "units_sold": int(row["units_sold"] or 0),
             "order_count": int(row["order_count"] or 0)}
            for row in rows
        ],
        "method": "Purchase-category preference + product popularity (rule-based)",
    }


@app.get("/api/v1/recommendations/customer/{customer_id}")
def customer_product_recommendations(
    customer_id: str,
    limit: int = Query(default=10, ge=1, le=50),
):
    """Recommend popular products in the customer's preferred categories,
    excluding products already purchased by that customer."""
    try:
        return get_cached_key(
            _customer_recommendations_cache, _customer_recommendations_lock,
            RECOMMENDATION_CACHE_TTL, (customer_id, limit),
            lambda: _load_customer_product_recommendations(customer_id, limit),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _load_frequently_bought_together(limit: int):
    with engine.connect() as connection:
        schema = _recommendation_schema(connection)
        status_filter = "AND o.status = 'Delivered'" if schema["has_status"] else ""
        rows = connection.execute(text(f"""
            SELECT
                p1.product_id AS product_id_1,
                p1.{schema['product_name']} AS product_name_1,
                p2.product_id AS product_id_2,
                p2.{schema['product_name']} AS product_name_2,
                COUNT(DISTINCT oi1.order_id) AS together_count
            FROM order_items oi1
            JOIN order_items oi2
              ON oi1.order_id = oi2.order_id
             AND oi1.product_id < oi2.product_id
            JOIN orders o ON o.order_id = oi1.order_id
            JOIN products p1 ON p1.product_id = oi1.product_id
            JOIN products p2 ON p2.product_id = oi2.product_id
            WHERE 1=1 {status_filter}
            GROUP BY p1.product_id, p1.{schema['product_name']},
                     p2.product_id, p2.{schema['product_name']}
            ORDER BY together_count DESC
            LIMIT :limit
        """), {"limit": limit}).mappings().all()
    return [
        {**dict(row), "together_count": int(row["together_count"] or 0)}
        for row in rows
    ]


@app.get("/api/v1/recommendations/frequently-bought-together")
def frequently_bought_together(limit: int = Query(default=10, ge=1, le=50)):
    try:
        return get_cached_key(
            _frequently_bought_cache, _frequently_bought_lock,
            RECOMMENDATION_CACHE_TTL, limit,
            lambda: _load_frequently_bought_together(limit),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# DATASET MANAGEMENT
# CSV files are stored locally; metadata is stored in PostgreSQL.
# ---------------------------------------------------------------------------

MAX_DATASET_SIZE = 20 * 1024 * 1024  # 20 MB
DATASET_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Cache the aggregate quality report briefly so CSV files are not revalidated
# on every dashboard request. Upload/delete operations invalidate this cache.
_dataset_quality_cache = {"data": None, "created_at": 0}
_dataset_quality_cache_lock = Lock()
DATASET_QUALITY_CACHE_TTL = 60


def invalidate_dataset_quality_cache():
    with _dataset_quality_cache_lock:
        _dataset_quality_cache["data"] = None
        _dataset_quality_cache["created_at"] = 0


def ensure_dataset_registry():
    """Create the metadata table if it does not already exist."""
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS dataset_registry (
                dataset_id VARCHAR(36) PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_filename VARCHAR(100) NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                columns_json TEXT NOT NULL,
                file_size BIGINT NOT NULL,
                uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))


def get_dataset_record(dataset_id: str):
    ensure_dataset_registry()
    with engine.connect() as connection:
        row = connection.execute(
            text("""
                SELECT dataset_id, original_filename, stored_filename,
                       file_path, row_count, column_count, columns_json,
                       file_size, uploaded_at
                FROM dataset_registry
                WHERE dataset_id = :dataset_id
            """),
            {"dataset_id": dataset_id},
        ).mappings().first()
    return dict(row) if row else None


@app.get("/api/v1/datasets")
def list_datasets():
    """List uploaded CSV datasets and their metadata."""
    try:
        ensure_dataset_registry()
        with engine.connect() as connection:
            rows = connection.execute(text("""
                SELECT dataset_id, original_filename, row_count,
                       column_count, file_size, uploaded_at
                FROM dataset_registry
                ORDER BY uploaded_at DESC
            """)).mappings().all()

        return {
            "datasets": [
                {
                    **dict(row),
                    "uploaded_at": row["uploaded_at"].isoformat()
                    if row["uploaded_at"] else None,
                }
                for row in rows
            ],
            "total": len(rows),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Validate and save a CSV, then register its metadata."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    if Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_DATASET_SIZE:
        raise HTTPException(
            status_code=413,
            detail="CSV file exceeds the 20 MB upload limit.",
        )

    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV must use UTF-8 encoding.",
        )

    try:
        reader = csv.reader(io.StringIO(decoded))
        headers = next(reader, None)

        if not headers:
            raise HTTPException(status_code=400, detail="CSV has no header row.")

        headers = [header.strip() for header in headers]
        if any(not header for header in headers):
            raise HTTPException(
                status_code=400,
                detail="CSV contains an empty column name.",
            )

        normalized_headers = [header.casefold() for header in headers]
        if len(normalized_headers) != len(set(normalized_headers)):
            raise HTTPException(
                status_code=400,
                detail="CSV contains duplicate column names.",
            )

        row_count = 0
        for line_number, row in enumerate(reader, start=2):
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) != len(headers):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Invalid CSV structure on line {line_number}: "
                        f"expected {len(headers)} fields, found {len(row)}."
                    ),
                )
            row_count += 1

        if row_count == 0:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain at least one data row.",
            )

    except csv.Error as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse CSV: {str(exc)}",
        )

    dataset_id = str(uuid.uuid4())
    stored_filename = f"{dataset_id}.csv"
    DATASET_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = DATASET_UPLOAD_DIR / stored_filename

    try:
        stored_path.write_bytes(content)
        ensure_dataset_registry()

        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO dataset_registry (
                        dataset_id, original_filename, stored_filename,
                        file_path, row_count, column_count, columns_json,
                        file_size
                    )
                    VALUES (
                        :dataset_id, :original_filename, :stored_filename,
                        :file_path, :row_count, :column_count, :columns_json,
                        :file_size
                    )
                """),
                {
                    "dataset_id": dataset_id,
                    "original_filename": Path(file.filename).name,
                    "stored_filename": stored_filename,
                    "file_path": str(stored_path),
                    "row_count": row_count,
                    "column_count": len(headers),
                    "columns_json": "\n".join(headers),
                    "file_size": len(content),
                },
            )

        invalidate_dataset_quality_cache()
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Dataset could not be saved: {str(exc)}",
        )
    finally:
        await file.close()

    return {
        "message": "Dataset uploaded and validated successfully.",
        "dataset": {
            "dataset_id": dataset_id,
            "original_filename": Path(file.filename).name,
            "row_count": row_count,
            "column_count": len(headers),
            "columns": headers,
            "file_size": len(content),
        },
    }


@app.get("/api/v1/datasets/{dataset_id}/preview")
def preview_dataset(
    dataset_id: str,
    limit: int = Query(default=10, ge=1, le=100),
):
    """Return column names and up to 100 CSV rows for preview."""
    try:
        dataset = get_dataset_record(dataset_id)
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        file_path = Path(dataset["file_path"]).resolve()
        upload_root = DATASET_UPLOAD_DIR.resolve()

        # Ensure the stored path remains inside the uploads directory.
        if upload_root not in file_path.parents or not file_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Dataset file is missing from storage.",
            )

        with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = []
            for row in reader:
                rows.append(row)
                if len(rows) >= limit:
                    break

        columns = dataset["columns_json"].split("\n") if dataset["columns_json"] else []

        return {
            "dataset_id": dataset_id,
            "filename": dataset["original_filename"],
            "columns": columns,
            "preview": rows,
            "preview_count": len(rows),
            "total_rows": dataset["row_count"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/v1/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):
    """Remove dataset metadata and its stored CSV file."""
    try:
        dataset = get_dataset_record(dataset_id)
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        file_path = Path(dataset["file_path"]).resolve()
        upload_root = DATASET_UPLOAD_DIR.resolve()

        if upload_root in file_path.parents:
            file_path.unlink(missing_ok=True)

        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM dataset_registry WHERE dataset_id = :dataset_id"),
                {"dataset_id": dataset_id},
            )

        invalidate_dataset_quality_cache()

        return {
            "message": "Dataset deleted successfully.",
            "dataset_id": dataset_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# DATASET QUALITY VALIDATION AND OVERVIEW
# ---------------------------------------------------------------------------

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NUMERIC_COLUMN_HINTS = (
    "age", "quantity", "price", "amount", "total",
    "spent", "revenue", "count",
)
DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d")


def analyze_dataset_quality(dataset: dict):
    """Read one stored CSV and calculate its data-quality metrics."""
    file_path = Path(dataset["file_path"]).resolve()
    upload_root = DATASET_UPLOAD_DIR.resolve()

    if upload_root not in file_path.parents or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset file is missing from storage.",
        )

    missing_by_column = {}
    invalid_numeric_by_column = {}
    invalid_date_by_column = {}
    invalid_emails = 0
    duplicate_rows = 0
    empty_rows = 0
    total_rows = 0
    seen_rows = set()

    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = reader.fieldnames or []

            if not columns:
                raise HTTPException(
                    status_code=400,
                    detail="Dataset has no header row.",
                )

            for row in reader:
                total_rows += 1
                values = [row.get(column) or "" for column in columns]

                if not any(value.strip() for value in values):
                    empty_rows += 1

                row_key = tuple(value.strip() for value in values)
                if row_key in seen_rows:
                    duplicate_rows += 1
                else:
                    seen_rows.add(row_key)

                for column in columns:
                    value = (row.get(column) or "").strip()
                    column_lower = column.lower()

                    if not value:
                        missing_by_column[column] = (
                            missing_by_column.get(column, 0) + 1
                        )
                        continue

                    if "email" in column_lower:
                        if not EMAIL_PATTERN.match(value):
                            invalid_emails += 1

                    if any(hint in column_lower for hint in NUMERIC_COLUMN_HINTS):
                        try:
                            float(value.replace(",", "").replace("₹", "").replace("$", "").strip())
                        except ValueError:
                            invalid_numeric_by_column[column] = (
                                invalid_numeric_by_column.get(column, 0) + 1
                            )

                    if "date" in column_lower or "timestamp" in column_lower:
                        valid_date = False
                        for date_format in DATE_FORMATS:
                            try:
                                datetime.strptime(value, date_format)
                                valid_date = True
                                break
                            except ValueError:
                                continue
                        if not valid_date:
                            invalid_date_by_column[column] = (
                                invalid_date_by_column.get(column, 0) + 1
                            )

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Dataset is not valid UTF-8 CSV.",
        )
    except csv.Error as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read dataset CSV: {str(exc)}",
        )

    total_columns = len(columns)
    total_cells = total_rows * total_columns
    missing_total = sum(missing_by_column.values())
    invalid_numeric_total = sum(invalid_numeric_by_column.values())
    invalid_date_total = sum(invalid_date_by_column.values())

    invalid_cells = (
        missing_total
        + invalid_emails
        + invalid_numeric_total
        + invalid_date_total
    )
    quality_score = (
        max(0, 100 * (1 - invalid_cells / total_cells))
        if total_cells else 0
    )

    if quality_score >= 90:
        status = "Good"
    elif quality_score >= 70:
        status = "Needs Improvement"
    else:
        status = "Poor"

    return {
        "dataset_id": dataset["dataset_id"],
        "filename": dataset["original_filename"],
        "total_rows": total_rows,
        "total_columns": total_columns,
        "total_cells": total_cells,
        "quality_score": round(quality_score, 2),
        "missing_values": {
            "total": missing_total,
            "by_column": missing_by_column,
        },
        "duplicate_rows": duplicate_rows,
        "empty_rows": empty_rows,
        "invalid_emails": invalid_emails,
        "invalid_numeric_values": invalid_numeric_by_column,
        "invalid_date_values": invalid_date_by_column,
        "status": status,
    }


@app.get("/api/v1/datasets/{dataset_id}/validation")
def validate_dataset(dataset_id: str):
    """Validate one uploaded dataset and return its quality report."""
    try:
        dataset = get_dataset_record(dataset_id)
        if dataset is None:
            raise HTTPException(status_code=404, detail="Dataset not found.")
        return analyze_dataset_quality(dataset)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def build_dataset_quality_overview():
    """
    Return aggregate quality metrics for all uploaded datasets.
    Each dataset is revalidated from its stored CSV when this endpoint runs.
    """
    try:
        ensure_dataset_registry()
        with engine.connect() as connection:
            datasets = connection.execute(text("""
                SELECT dataset_id, original_filename, file_path,
                       row_count, column_count, file_size, uploaded_at
                FROM dataset_registry
                ORDER BY uploaded_at DESC
            """)).mappings().all()

        reports = []
        unavailable = []

        for dataset_row in datasets:
            dataset = dict(dataset_row)
            try:
                report = analyze_dataset_quality(dataset)
                report["uploaded_at"] = (
                    dataset["uploaded_at"].isoformat()
                    if dataset.get("uploaded_at") else None
                )
                reports.append(report)
            except HTTPException as exc:
                unavailable.append({
                    "dataset_id": dataset["dataset_id"],
                    "filename": dataset["original_filename"],
                    "detail": exc.detail,
                })

        total_datasets = len(datasets)
        scored_reports = reports
        average_quality = (
            sum(report["quality_score"] for report in scored_reports)
            / len(scored_reports)
            if scored_reports else 0
        )

        status_distribution = {"Good": 0, "Needs Improvement": 0, "Poor": 0}
        missing_by_dataset = []
        total_issues = 0
        needs_attention = 0

        for report in scored_reports:
            status_distribution[report["status"]] += 1

            missing_count = report["missing_values"]["total"]
            invalid_email_count = report["invalid_emails"]
            invalid_numeric_count = sum(
                report["invalid_numeric_values"].values()
            )
            invalid_date_count = sum(
                report["invalid_date_values"].values()
            )
            duplicate_count = report["duplicate_rows"]
            empty_count = report["empty_rows"]

            dataset_issue_count = (
                missing_count
                + invalid_email_count
                + invalid_numeric_count
                + invalid_date_count
                + duplicate_count
                + empty_count
            )
            total_issues += dataset_issue_count

            if report["status"] != "Good":
                needs_attention += 1

            missing_by_dataset.append({
                "dataset_id": report["dataset_id"],
                "filename": report["filename"],
                "missing_values": missing_count,
                "quality_score": report["quality_score"],
            })

        return {
            "total_datasets": total_datasets,
            "validated_datasets": len(scored_reports),
            "unavailable_datasets": len(unavailable),
            "average_quality_score": round(average_quality, 2),
            "datasets_needing_attention": needs_attention,
            "total_issues": total_issues,
            "status_distribution": [
                {"name": name, "value": count}
                for name, count in status_distribution.items()
            ],
            "dataset_quality": [
                {
                    "dataset_id": report["dataset_id"],
                    "filename": report["filename"],
                    "quality_score": report["quality_score"],
                    "status": report["status"],
                }
                for report in scored_reports
            ],
            "missing_values_by_dataset": sorted(
                missing_by_dataset,
                key=lambda item: item["missing_values"],
                reverse=True,
            ),
            "recent_validations": scored_reports[:10],
            "unavailable": unavailable,
        }

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/v1/datasets/quality/overview")
def dataset_quality_overview():
    """Return the aggregate dataset-quality report, cached for 60 seconds."""
    with _dataset_quality_cache_lock:
        current_time = time.monotonic()

        if (
            _dataset_quality_cache["data"] is not None
            and current_time - _dataset_quality_cache["created_at"]
            < DATASET_QUALITY_CACHE_TTL
        ):
            return _dataset_quality_cache["data"]

        result = build_dataset_quality_overview()
        _dataset_quality_cache["data"] = result
        _dataset_quality_cache["created_at"] = time.monotonic()
        return result
