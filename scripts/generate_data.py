
import os
import random
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "datasets", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuration
N_CUSTOMERS = 5000
N_PRODUCTS = 500
N_ORDERS = 15000
N_ORDER_ITEMS = 25000
N_REVIEWS = 8000
N_CAMPAIGNS = 1000
N_INTERACTIONS = 20000

CITIES = [
    "Hyderabad", "Bengaluru", "Chennai", "Mumbai",
    "Delhi", "Pune", "Kurnool", "Vijayawada",
    "Visakhapatnam", "Kolkata", "Jaipur", "Kochi"
]

CATEGORIES = [
    "Electronics", "Fashion", "Home & Kitchen",
    "Beauty", "Sports", "Books", "Accessories"
]

BRANDS = [
    "TechPro", "UrbanStyle", "HomeEase",
    "GlowCare", "FitZone", "ReadMore"
]

def save(df, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Generated: {filename} ({len(df):,} records)")


# 1. CUSTOMERS
print("\nGenerating customers...")

customer_ids = [
    f"CUST{i:05d}" for i in range(1, N_CUSTOMERS + 1)
]

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "name": [fake.name() for _ in range(N_CUSTOMERS)],
    "age": np.random.randint(18, 65, N_CUSTOMERS),
    "gender": np.random.choice(
        ["Male", "Female", "Other"],
        N_CUSTOMERS,
        p=[0.49, 0.49, 0.02]
    ),
    "city": np.random.choice(CITIES, N_CUSTOMERS),
    "membership": np.random.choice(
        ["Standard", "Silver", "Gold", "Platinum"],
        N_CUSTOMERS,
        p=[0.45, 0.25, 0.20, 0.10]
    ),
    "signup_date": fake.date_between(
        start_date="-3y", end_date="-30d"
    ).isoformat(),
    "email": [
        f"customer{i}@example.com"
        for i in range(1, N_CUSTOMERS + 1)
    ]
})

save(customers, "customers.csv")


# 2. PRODUCTS
print("\nGenerating products...")

products = pd.DataFrame({
    "product_id": [
        f"PROD{i:04d}" for i in range(1, N_PRODUCTS + 1)
    ],
    "product_name": [
        f"{random.choice(BRANDS)} {fake.word().title()} {random.choice(CATEGORIES)}"
        for _ in range(N_PRODUCTS)
    ],
    "category": np.random.choice(CATEGORIES, N_PRODUCTS),
    "brand": np.random.choice(BRANDS, N_PRODUCTS),
    "price": np.round(
        np.random.uniform(199, 25000, N_PRODUCTS), 2
    ),
    "stock": np.random.randint(0, 500, N_PRODUCTS)
})

product_ids = products["product_id"].tolist()
product_prices = products.set_index("product_id")["price"].to_dict()

save(products, "products.csv")


# 3. ORDERS
print("\nGenerating orders...")

order_ids = [
    f"ORD{i:06d}" for i in range(1, N_ORDERS + 1)
]

order_customers = np.random.choice(customer_ids, N_ORDERS)

orders = pd.DataFrame({
    "order_id": order_ids,
    "customer_id": order_customers,
    "order_date": [
        fake.date_between(
            start_date="-2y", end_date="today"
        ).isoformat()
        for _ in range(N_ORDERS)
    ],
    "payment_method": np.random.choice(
        ["UPI", "Credit Card", "Debit Card", "COD", "Net Banking"],
        N_ORDERS
    ),
    "status": np.random.choice(
        ["Delivered", "Processing", "Cancelled", "Returned"],
        N_ORDERS,
        p=[0.75, 0.12, 0.08, 0.05]
    )
})

save(orders, "orders.csv")


# 4. ORDER ITEMS
print("\nGenerating order items...")

item_order_ids = np.random.choice(order_ids, N_ORDER_ITEMS)
item_product_ids = np.random.choice(product_ids, N_ORDER_ITEMS)

order_items = pd.DataFrame({
    "item_id": [
        f"ITEM{i:06d}" for i in range(1, N_ORDER_ITEMS + 1)
    ],
    "order_id": item_order_ids,
    "product_id": item_product_ids,
    "quantity": np.random.randint(1, 5, N_ORDER_ITEMS),
    "unit_price": [
        product_prices[p] for p in item_product_ids
    ]
})

order_items["total_price"] = (
    order_items["quantity"] * order_items["unit_price"]
).round(2)

save(order_items, "order_items.csv")


# 5. REVIEWS
print("\nGenerating reviews...")

review_orders = np.random.choice(
    order_ids, N_REVIEWS, replace=True
)

order_customer_map = orders.set_index("order_id")["customer_id"]

positive_reviews = [
    "Excellent product and great quality.",
    "Very happy with this purchase.",
    "Amazing experience. Highly recommended.",
    "Good value for money.",
    "Fast delivery and excellent packaging."
]

negative_reviews = [
    "Very poor quality.",
    "Not worth the money.",
    "Product stopped working.",
    "Disappointed with the purchase.",
    "Delivery was extremely late."
]

neutral_reviews = [
    "Product is okay.",
    "Average experience.",
    "It works as expected.",
    "Nothing special.",
    "Decent product for the price."
]

review_texts = []
ratings = []

for _ in range(N_REVIEWS):
    sentiment = np.random.choice(
        ["Positive", "Negative", "Neutral"],
        p=[0.65, 0.20, 0.15]
    )

    if sentiment == "Positive":
        review_texts.append(random.choice(positive_reviews))
        ratings.append(random.randint(4, 5))
    elif sentiment == "Negative":
        review_texts.append(random.choice(negative_reviews))
        ratings.append(random.randint(1, 2))
    else:
        review_texts.append(random.choice(neutral_reviews))
        ratings.append(3)

reviews = pd.DataFrame({
    "review_id": [
        f"REV{i:06d}" for i in range(1, N_REVIEWS + 1)
    ],
    "order_id": review_orders,
    "customer_id": [order_customer_map[o] for o in review_orders],
    "rating": ratings,
    "review_text": review_texts,
    "review_date": [
        fake.date_between(
            start_date="-2y", end_date="today"
        ).isoformat()
        for _ in range(N_REVIEWS)
    ]
})

save(reviews, "reviews.csv")


# 6. CAMPAIGNS
print("\nGenerating campaigns...")

campaigns = pd.DataFrame({
    "campaign_id": [
        f"CAMP{i:04d}" for i in range(1, N_CAMPAIGNS + 1)
    ],
    "campaign_name": [
        f"{random.choice(['Summer', 'Festive', 'Flash', 'New Year', 'Mega'])} "
        f"{random.choice(['Sale', 'Offer', 'Promotion', 'Rewards'])} {i}"
        for i in range(1, N_CAMPAIGNS + 1)
    ],
    "campaign_type": np.random.choice(
        ["Email", "SMS", "Push Notification", "Social Media"],
        N_CAMPAIGNS
    ),
    "discount_percentage": np.random.choice(
        [5, 10, 15, 20, 25, 30, 40],
        N_CAMPAIGNS
    ),
    "budget": np.random.randint(
        5000, 100000, N_CAMPAIGNS
    ),
    "status": np.random.choice(
        ["Active", "Completed", "Scheduled"],
        N_CAMPAIGNS
    )
})

campaign_ids = campaigns["campaign_id"].tolist()

save(campaigns, "campaigns.csv")


# 7. INTERACTIONS
print("\nGenerating customer interactions...")

interactions = pd.DataFrame({
    "interaction_id": [
        f"INT{i:06d}" for i in range(1, N_INTERACTIONS + 1)
    ],
    "customer_id": np.random.choice(
        customer_ids, N_INTERACTIONS
    ),
    "campaign_id": np.random.choice(
        campaign_ids, N_INTERACTIONS
    ),
    "interaction_type": np.random.choice(
        ["Email Open", "Email Click", "Website Visit",
         "Product View", "Add to Cart", "Purchase"],
        N_INTERACTIONS
    ),
    "interaction_date": [
        fake.date_between(
            start_date="-2y", end_date="today"
        ).isoformat()
        for _ in range(N_INTERACTIONS)
    ],
    "device": np.random.choice(
        ["Mobile", "Desktop", "Tablet"],
        N_INTERACTIONS
    )
})

save(interactions, "interactions.csv")


# 8. CHURN LABELS
print("\nGenerating churn labels...")

customer_order_counts = (
    orders.groupby("customer_id")
    .size()
    .to_dict()
)

customer_labels = []

for customer_id in customer_ids:
    order_count = customer_order_counts.get(customer_id, 0)

    churn_probability = 0.65 if order_count == 0 else (
        0.35 if order_count <= 2 else 0.12
    )

    churn_probability += random.uniform(-0.05, 0.05)
    churn_probability = max(0.02, min(0.95, churn_probability))

    customer_labels.append({
        "customer_id": customer_id,
        "order_count": order_count,
        "churn_label": int(
            np.random.random() < churn_probability
        )
    })

churn_labels = pd.DataFrame(customer_labels)

save(churn_labels, "churn_labels.csv")


# SUMMARY
print("\n" + "=" * 45)
print("ALL SYNTHETIC DATASETS GENERATED SUCCESSFULLY")
print("=" * 45)

for filename in sorted(os.listdir(OUTPUT_DIR)):
    if filename.endswith(".csv"):
        df = pd.read_csv(os.path.join(OUTPUT_DIR, filename))
        print(f"{filename:<25} {len(df):>8,} rows")

print("\nOutput directory:", OUTPUT_DIR)
