
from pathlib import Path

import pandas as pd


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "churn_features.csv"
)


# ==================================================
# 2. LOAD DATASET
# ==================================================

def load_dataset():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Run feature_engineering.py first."
        )

    return pd.read_csv(DATA_FILE)


# ==================================================
# 3. DATASET OVERVIEW
# ==================================================

def inspect_overview(df):

    print("\n========== DATASET OVERVIEW ==========")

    print("Shape:", df.shape)

    print("\nColumns:")

    print(df.columns.tolist())

    print("\nData types:")

    print(df.dtypes)

    print("\nFirst 10 records:")

    print(
        df.head(10).to_string(index=False)
    )


# ==================================================
# 4. DATA QUALITY
# ==================================================

def inspect_quality(df):

    print("\n========== DATA QUALITY ==========")

    print("\nMissing values:")

    print(df.isnull().sum())

    print("\nDuplicate rows:")

    print(df.duplicated().sum())

    print("\nDuplicate customer IDs:")

    print(df["customer_id"].duplicated().sum())


# ==================================================
# 5. TARGET DISTRIBUTION
# ==================================================

def inspect_target(df):

    print("\n========== CHURN DISTRIBUTION ==========")

    counts = df["churn_label"].value_counts()

    percentages = (
        df["churn_label"]
        .value_counts(normalize=True)
        .mul(100)
    )

    result = pd.DataFrame({
        "Customer Count": counts,
        "Percentage": percentages
    })

    print(result)


# ==================================================
# 6. NUMERICAL STATISTICS
# ==================================================

def inspect_statistics(df):

    print("\n========== NUMERICAL STATISTICS ==========")

    print(
        df.describe(
            include="all"
        ).to_string()
    )


# ==================================================
# 7. CHURN GROUP COMPARISON
# ==================================================

def inspect_churn_groups(df):

    print("\n========== CHURN GROUP COMPARISON ==========")

    numeric_columns = (
        df.select_dtypes(include="number")
        .columns
        .drop("churn_label")
    )

    comparison = (
        df.groupby("churn_label")[numeric_columns]
        .mean()
        .T
    )

    comparison.columns = [
        "Not Churned (0)",
        "Churned (1)"
    ]

    print(comparison.to_string())


# ==================================================
# 8. CORRELATION ANALYSIS
# ==================================================

def inspect_correlations(df):

    print("\n========== CORRELATION WITH CHURN ==========")

    numeric_df = df.select_dtypes(
        include="number"
    )

    correlations = (
        numeric_df.corr()["churn_label"]
        .drop("churn_label")
        .sort_values(ascending=False)
    )

    print(correlations.to_string())


# ==================================================
# 9. INTERACTION ANALYSIS
# ==================================================

def inspect_interactions(df):

    interaction_columns = [
        "email_click_count",
        "email_open_count",
        "product_view_count",
        "website_visit_count",
        "add_to_cart_count",
        "interaction_purchase_count"
    ]

    available_columns = [
        column
        for column in interaction_columns
        if column in df.columns
    ]

    print("\n========== INTERACTION ANALYSIS ==========")

    print("\nTotal interaction counts:")

    print(
        df[available_columns]
        .sum()
        .to_string()
    )

    print("\nAverage interactions by churn label:")

    print(
        df.groupby("churn_label")[available_columns]
        .mean()
        .T
        .to_string()
    )


# ==================================================
# 10. CUSTOMER FEATURE ANALYSIS
# ==================================================

def inspect_categorical_features(df):

    categorical_columns = [
        "gender",
        "membership",
        "city"
    ]

    print("\n========== CATEGORICAL FEATURES ==========")

    for column in categorical_columns:

        if column not in df.columns:
            continue

        print(f"\n{column}:")

        print(
            df[column]
            .value_counts()
            .to_string()
        )


# ==================================================
# 11. MAIN
# ==================================================

def main():

    print("Loading churn feature dataset...")

    df = load_dataset()

    inspect_overview(df)

    inspect_quality(df)

    inspect_target(df)

    inspect_statistics(df)

    inspect_churn_groups(df)

    inspect_correlations(df)

    inspect_interactions(df)

    inspect_categorical_features(df)

    print("\nFeature inspection completed.")


if __name__ == "__main__":
    main()
