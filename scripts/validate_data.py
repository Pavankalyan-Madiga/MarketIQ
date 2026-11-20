
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "datasets", "raw")

files = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "reviews": "reviews.csv",
    "campaigns": "campaigns.csv",
    "interactions": "interactions.csv",
    "churn_labels": "churn_labels.csv",
}

data = {}

print("\n" + "=" * 60)
print("CUSTOMER MARKETING INTELLIGENCE - DATA VALIDATION")
print("=" * 60)

# Load datasets
for name, filename in files.items():
    path = os.path.join(DATA_DIR, filename)

    df = pd.read_csv(path)
    data[name] = df

    print(f"\n{name.upper()}")
    print("-" * 40)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Duplicates:", df.duplicated().sum())
    print("Missing values:", df.isnull().sum().sum())

# Primary key validation
print("\n" + "=" * 60)
print("PRIMARY KEY VALIDATION")
print("=" * 60)

primary_keys = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "item_id",
    "reviews": "review_id",
    "campaigns": "campaign_id",
    "interactions": "interaction_id",
    "churn_labels": "customer_id",
}

for name, key in primary_keys.items():
    df = data[name]
    duplicate_keys = df[key].duplicated().sum()

    print(
        f"{name}: "
        f"{'PASS' if duplicate_keys == 0 else 'FAIL'} "
        f"({duplicate_keys} duplicate keys)"
    )

# Foreign key validation
print("\n" + "=" * 60)
print("FOREIGN KEY VALIDATION")
print("=" * 60)

checks = [
    ("orders", "customer_id", "customers", "customer_id"),
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("reviews", "order_id", "orders", "order_id"),
    ("reviews", "customer_id", "customers", "customer_id"),
    ("interactions", "customer_id", "customers", "customer_id"),
    ("interactions", "campaign_id", "campaigns", "campaign_id"),
    ("churn_labels", "customer_id", "customers", "customer_id"),
]

for child, child_col, parent, parent_col in checks:
    invalid = ~data[child][child_col].isin(data[parent][parent_col])
    count = invalid.sum()

    print(
        f"{child}.{child_col}: "
        f"{'PASS' if count == 0 else 'FAIL'} "
        f"({count} invalid references)"
    )

# Data range validation
print("\n" + "=" * 60)
print("VALUE VALIDATION")
print("=" * 60)

customers = data["customers"]
products = data["products"]
orders = data["orders"]
reviews = data["reviews"]

print("Customer ages valid:",
      customers["age"].between(18, 100).all())

print("Product prices positive:",
      (products["price"] > 0).all())

print("Review ratings valid:",
      reviews["rating"].between(1, 5).all())

print("Order statuses valid:",
      orders["status"].isin(
          ["Delivered", "Processing", "Cancelled", "Returned"]
      ).all())

print("All order item quantities positive:",
      (data["order_items"]["quantity"] > 0).all())

print("\n" + "=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)
