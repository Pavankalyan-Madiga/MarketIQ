
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "churn_features.csv"

MODEL_DIR = PROJECT_ROOT / "models" / "churn"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "best_churn_model.joblib"
RESULTS_PATH = MODEL_DIR / "model_comparison.csv"
METRICS_PATH = MODEL_DIR / "best_model_metrics.json"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():
    print("\nLoading churn dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print(f"Dataset shape: {df.shape}")

    return df


# --------------------------------------------------
# PREPARE FEATURES
# --------------------------------------------------

def prepare_data(df):

    print("\nPreparing features...")

    target = "churn_label"

    if target not in df.columns:
        raise ValueError("Target column churn_label not found")

    # Remove identifier and direct target-generation variable.
    X = df.drop(
        columns=["customer_id", "total_orders", target],
        errors="ignore",
    )

    y = df[target].astype(int)

    categorical_features = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    numerical_features = X.select_dtypes(
        include=["number", "bool"]
    ).columns.tolist()

    print(f"Numerical features: {len(numerical_features)}")
    print(f"Categorical features: {len(categorical_features)}")

    print("\nExcluded columns:")
    print("customer_id: identifier")
    print("total_orders: direct target-generation variable")

    # Numerical preprocessing
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # Categorical preprocessing
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    # Combine preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_pipeline, numerical_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )

    return X, y, preprocessor


# --------------------------------------------------
# MODEL DEFINITIONS
# --------------------------------------------------

def get_models():

    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        ),
    }


# --------------------------------------------------
# TRAIN AND EVALUATE
# --------------------------------------------------

def train_models(X, y, preprocessor):

    print("\nSplitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")

    models = get_models()

    results = []
    trained_models = {}

    for model_name, classifier in models.items():

        print("\n" + "=" * 55)
        print(f"Training: {model_name}")
        print("=" * 55)

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", classifier),
            ]
        )

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)
        probabilities = pipeline.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(
            y_test, predictions, zero_division=0
        )
        recall = recall_score(
            y_test, predictions, zero_division=0
        )
        f1 = f1_score(
            y_test, predictions, zero_division=0
        )
        roc_auc = roc_auc_score(y_test, probabilities)

        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}")

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, predictions))

        print("\nClassification Report:")
        print(
            classification_report(
                y_test,
                predictions,
                zero_division=0,
            )
        )

        results.append({
            "model": model_name,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "roc_auc": roc_auc,
        })

        trained_models[model_name] = pipeline

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by="roc_auc",
        ascending=False,
    )

    print("\n" + "=" * 55)
    print("MODEL COMPARISON")
    print("=" * 55)

    print(results_df.to_string(index=False))

    results_df.to_csv(RESULTS_PATH, index=False)

    # Select the model with the highest ROC-AUC.
    best_model_name = results_df.iloc[0]["model"]
    best_model = trained_models[best_model_name]

    best_metrics = results_df.iloc[0].to_dict()

    print("\nBest model:", best_model_name)

    return best_model, best_model_name, best_metrics


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

def save_model(model, model_name, metrics):

    print("\nSaving best model...")

    joblib.dump(model, MODEL_PATH)

    metrics["best_model"] = model_name
    metrics["model_file"] = str(MODEL_PATH)

    with open(METRICS_PATH, "w") as file:
        json.dump(metrics, file, indent=4)

    print(f"Model saved: {MODEL_PATH}")
    print(f"Metrics saved: {METRICS_PATH}")
    print(f"Comparison saved: {RESULTS_PATH}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nCUSTOMER CHURN PREDICTION")
    print("=" * 55)

    df = load_data()

    X, y, preprocessor = prepare_data(df)

    best_model, best_model_name, best_metrics = train_models(
        X,
        y,
        preprocessor,
    )

    save_model(
        best_model,
        best_model_name,
        best_metrics,
    )

    print("\nTraining pipeline completed successfully!")


if __name__ == "__main__":
    main()
