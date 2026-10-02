from pathlib import Path
import json

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[3]

EVALUATION_DIR = ROOT / "ml" / "evaluation"
OUTPUT_DIR = EVALUATION_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MODEL FILES
# ============================================================

MODEL_FILES = {
    "Logistic Regression v2": "logistic_regression_v2_results.json",
    "Linear SVM": "linear_svm_results.json",
    "Random Forest": "random_forest_results.json",
    "XGBoost": "xgboost_results.json",
}


# ============================================================
# LOAD RESULTS
# ============================================================

print("=" * 80)
print("📊 VERILENS — CLASSICAL ML MODEL COMPARISON")
print("=" * 80)

results = {}

for model_name, filename in MODEL_FILES.items():

    path = EVALUATION_DIR / filename

    if not path.exists():
        print(f"\n⚠️ Missing: {filename}")
        continue

    with open(path, "r", encoding="utf-8") as file:
        results[model_name] = json.load(file)

    print(f"✅ Loaded: {filename}")


if not results:
    raise FileNotFoundError(
        "No model result files were found."
    )


# ============================================================
# BUILD COMPARISON TABLE
# ============================================================

rows = []

for model_name, result in results.items():

    validation = result.get("validation", {})
    test = result.get("test", {})

    rows.append(
        {
            "Model": model_name,

            "Validation Accuracy":
                validation.get("accuracy"),

            "Validation Macro Precision":
                validation.get("macro_precision"),

            "Validation Macro Recall":
                validation.get("macro_recall"),

            "Validation Macro F1":
                validation.get("macro_f1"),

            "Validation Weighted F1":
                validation.get("weighted_f1"),

            "Test Accuracy":
                test.get("accuracy"),

            "Test Macro Precision":
                test.get("macro_precision"),

            "Test Macro Recall":
                test.get("macro_recall"),

            "Test Macro F1":
                test.get("macro_f1"),

            "Test Weighted F1":
                test.get("weighted_f1"),

            "Training Time (seconds)":
                result.get("training_time_seconds"),
        }
    )


df = pd.DataFrame(rows)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 80)
print("📈 MODEL PERFORMANCE")
print("=" * 80)

display_columns = [
    "Model",
    "Validation Accuracy",
    "Validation Macro F1",
    "Test Accuracy",
    "Test Macro F1",
    "Test Weighted F1",
    "Training Time (seconds)",
]

print(
    df[display_columns]
    .to_string(index=False)
)


# ============================================================
# FIND BEST MODELS BY METRIC
# ============================================================

print("\n" + "=" * 80)
print("🏆 METRIC LEADERS")
print("=" * 80)


def print_leader(metric, label):

    valid = df.dropna(subset=[metric])

    if valid.empty:
        print(f"{label}: No data")
        return

    best_index = valid[metric].idxmax()
    best_model = valid.loc[best_index, "Model"]
    best_value = valid.loc[best_index, metric]

    print(
        f"{label}: "
        f"{best_model} "
        f"({best_value:.4f})"
    )


print_leader(
    "Validation Accuracy",
    "Validation Accuracy"
)

print_leader(
    "Validation Macro F1",
    "Validation Macro F1"
)

print_leader(
    "Test Accuracy",
    "Test Accuracy"
)

print_leader(
    "Test Macro F1",
    "Test Macro F1"
)

print_leader(
    "Test Weighted F1",
    "Test Weighted F1"
)


# ============================================================
# SAVE CSV
# ============================================================

csv_path = OUTPUT_DIR / "classical_ml_model_comparison.csv"

df.to_csv(
    csv_path,
    index=False,
)

print(f"\n💾 CSV saved:")
print(f"   {csv_path}")


# ============================================================
# SAVE JSON
# ============================================================

json_path = OUTPUT_DIR / "classical_ml_model_comparison.json"

comparison_json = {
    "experiment": "Classical ML baseline comparison",
    "dataset": "LIAR2",
    "models": df.to_dict(orient="records"),
}

with open(
    json_path,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        comparison_json,
        file,
        indent=2,
    )


print("\n💾 JSON saved:")
print(f"   {json_path}")


# ============================================================
# SAVE BEST MODEL SUMMARY
# ============================================================

valid_macro_f1 = df.dropna(
    subset=["Test Macro F1"]
)

best_model = None
best_macro_f1 = None

if not valid_macro_f1.empty:

    best_index = valid_macro_f1[
        "Test Macro F1"
    ].idxmax()

    best_model = valid_macro_f1.loc[
        best_index,
        "Model",
    ]

    best_macro_f1 = float(
        valid_macro_f1.loc[
            best_index,
            "Test Macro F1",
        ]
    )


summary = {
    "selection_metric": "Test Macro F1",
    "reason": (
        "Macro F1 gives equal importance to each "
        "class and is therefore useful for evaluating "
        "the imbalanced six-class LIAR2 classification task."
    ),
    "best_model_by_test_macro_f1": best_model,
    "best_test_macro_f1": best_macro_f1,
}


summary_path = (
    OUTPUT_DIR /
    "classical_ml_best_model.json"
)

with open(
    summary_path,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        summary,
        file,
        indent=2,
    )


print("\n💾 Best-model summary saved:")
print(f"   {summary_path}")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 80)
print("✅ CLASSICAL ML COMPARISON COMPLETE")
print("=" * 80)

print("\nCreated:")

print(
    "   • ml/evaluation/"
    "classical_ml_model_comparison.csv"
)

print(
    "   • ml/evaluation/"
    "classical_ml_model_comparison.json"
)

print(
    "   • ml/evaluation/"
    "classical_ml_best_model.json"
)

print("\n🚀 Next: Review the comparison and move into NLP Deep Learning.")