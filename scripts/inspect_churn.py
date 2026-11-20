import pandas as pd
from pathlib import Path

DATA_DIR = Path("datasets/raw")

churn_file = DATA_DIR / "churn_labels.csv"

if not churn_file.exists():
    print(f"File not found: {churn_file}")
    exit()

df = pd.read_csv(churn_file)

print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)

print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

print("\n========== FIRST 10 ROWS ==========")
print(df.head(10).to_string(index=False))

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print(df.duplicated().sum())

print("\n========== UNIQUE VALUES ==========")
for column in df.columns:
    print(f"\n{column}:")
    print(df[column].value_counts(dropna=False).head(15))

print("\n========== POSSIBLE CHURN TARGET ==========")
for column in df.columns:
    if "churn" in column.lower():
        print(f"\nTarget column: {column}")
        print(df[column].value_counts(dropna=False))