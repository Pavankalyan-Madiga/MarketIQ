
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load backend environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

load_dotenv(os.path.join(BACKEND_DIR, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in backend/.env")

DATA_DIR = os.path.join(BASE_DIR, "datasets", "raw")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Import order: parent tables before child tables
tables = [
    ("customers", "customers.csv"),
    ("products", "products.csv"),
    ("campaigns", "campaigns.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("reviews", "reviews.csv"),
    ("interactions", "interactions.csv"),
    ("churn_labels", "churn_labels.csv"),
]

primary_keys = {
    "customers": "customer_id",
    "products": "product_id",
    "campaigns": "campaign_id",
    "orders": "order_id",
    "order_items": "item_id",
    "reviews": "review_id",
    "interactions": "interaction_id",
    "churn_labels": "customer_id",
}

foreign_keys = [
    ("orders", "customer_id", "customers", "customer_id"),
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("reviews", "order_id", "orders", "order_id"),
    ("reviews", "customer_id", "customers", "customer_id"),
    ("interactions", "customer_id", "customers", "customer_id"),
    ("interactions", "campaign_id", "campaigns", "campaign_id"),
    ("churn_labels", "customer_id", "customers", "customer_id"),
]


def main():
    print("\nConnecting to PostgreSQL...")

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("Database connection successful.")

    # Load CSV files
    for table_name, filename in tables:
        file_path = os.path.join(DATA_DIR, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing dataset: {file_path}")

        df = pd.read_csv(file_path)

        print(f"\nLoading {filename}: {len(df)} rows")

        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

        print(f"Imported {table_name} successfully.")

    # Add primary keys
    print("\nCreating primary keys...")

    with engine.begin() as connection:
        for table_name, column_name in primary_keys.items():
            constraint_name = f"pk_{table_name}"

            connection.execute(text(
                f'ALTER TABLE "{table_name}" '
                f'ADD CONSTRAINT "{constraint_name}" '
                f'PRIMARY KEY ("{column_name}")'
            ))

            print(f"Primary key added: {table_name}.{column_name}")

    # Add foreign keys
    print("\nCreating foreign keys...")

    with engine.begin() as connection:
        for child, child_col, parent, parent_col in foreign_keys:
            constraint_name = f"fk_{child}_{child_col}"

            connection.execute(text(
                f'ALTER TABLE "{child}" '
                f'ADD CONSTRAINT "{constraint_name}" '
                f'FOREIGN KEY ("{child_col}") '
                f'REFERENCES "{parent}" ("{parent_col}")'
            ))

            print(f"Foreign key added: {child}.{child_col}")

    # Verify imported record counts
    print("\n" + "=" * 55)
    print("DATABASE IMPORT SUMMARY")
    print("=" * 55)

    with engine.connect() as connection:
        for table_name, _ in tables:
            count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar_one()

            print(f"{table_name:20} {count:>8} rows")

    print("\nALL DATASETS IMPORTED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
