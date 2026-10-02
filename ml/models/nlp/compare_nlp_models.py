import json
import os

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_DIR = "ml/evaluation"

OUTPUT_CSV = (
    "ml/evaluation/nlp_model_comparison.csv"
)

OUTPUT_JSON = (
    "ml/evaluation/nlp_model_comparison.json"
)

SUMMARY_JSON = (
    "ml/evaluation/nlp_experiment_summary.json"
)


# ============================================================
# RESULT FILES
# ============================================================

RESULT_FILES = {
    "Logistic Regression v2":
        "logistic_regression_v2_results.json",

    "Linear SVM":
        "linear_svm_results.json",

    "Random Forest":
        "random_forest_results.json",

    "XGBoost":
        "xgboost_results.json",

    "BiLSTM":
        "bilstm_baseline_results.json",

    "DistilBERT Embeddings + LR":
        "distilbert_classifier_results.json",
}


# ============================================================
# LOAD CLASSICAL / BILSTM RESULTS
# ============================================================

def load_standard_result(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# EXTRACT METRICS
# ============================================================

def extract_standard_metrics(
    model_name,
    result,
):

    # Classical ML and BiLSTM results use
    # slightly different structures, so we
    # handle both formats.

    test = result.get(
        "test",
        {}
    )

    validation = result.get(
        "validation",
        {}
    )

    return {

        "model": model_name,

        "family": (
            "Transformer"
            if "DistilBERT" in model_name
            else (
                "Deep Learning"
                if model_name == "BiLSTM"
                else "Classical ML"
            )
        ),

        "validation_accuracy": (
            validation.get(
                "accuracy",
                validation.get(
                    "val_accuracy",
                    None,
                ),
            )
        ),

        "validation_macro_precision": (
            validation.get(
                "macro_precision",
                None,
            )
        ),

        "validation_macro_recall": (
            validation.get(
                "macro_recall",
                None,
            )
        ),

        "validation_macro_f1": (
            validation.get(
                "macro_f1",
                validation.get(
                    "val_macro_f1",
                    None,
                ),
            )
        ),

        "validation_weighted_f1": (
            validation.get(
                "weighted_f1",
                None,
            )
        ),

        "test_accuracy": (
            test.get(
                "accuracy",
                None,
            )
        ),

        "test_macro_precision": (
            test.get(
                "macro_precision",
                None,
            )
        ),

        "test_macro_recall": (
            test.get(
                "macro_recall",
                None,
            )
        ),

        "test_macro_f1": (
            test.get(
                "macro_f1",
                None,
            )
        ),

        "test_weighted_f1": (
            test.get(
                "weighted_f1",
                None,
            )
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "VeriLens — NLP Model Comparison"
    )

    print("=" * 70)

    rows = []

    loaded_models = []

    # --------------------------------------------------------
    # Load every experiment
    # --------------------------------------------------------

    for model_name, filename in RESULT_FILES.items():

        path = os.path.join(
            RESULTS_DIR,
            filename,
        )

        print(
            f"Loading: {filename}"
        )

        if not os.path.exists(path):

            print(
                f"  WARNING: File not found."
            )

            continue

        result = load_standard_result(
            path
        )

        row = extract_standard_metrics(
            model_name,
            result,
        )

        rows.append(row)

        loaded_models.append(
            model_name
        )

    if not rows:

        raise RuntimeError(
            "No NLP result files were found."
        )

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    comparison = pd.DataFrame(
        rows
    )

    comparison = comparison.sort_values(
        by="test_macro_f1",
        ascending=False,
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Add ranking
    # --------------------------------------------------------

    comparison.insert(
        0,
        "rank_by_test_macro_f1",
        range(
            1,
            len(comparison) + 1,
        ),
    )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    comparison.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    # --------------------------------------------------------
    # Identify metric leaders
    # --------------------------------------------------------

    best_macro_f1 = comparison.loc[
        comparison[
            "test_macro_f1"
        ].idxmax()
    ]

    best_accuracy = comparison.loc[
        comparison[
            "test_accuracy"
        ].idxmax()
    ]

    best_macro_precision = comparison.loc[
        comparison[
            "test_macro_precision"
        ].idxmax()
    ]

    best_macro_recall = comparison.loc[
        comparison[
            "test_macro_recall"
        ].idxmax()
    ]

    best_weighted_f1 = comparison.loc[
        comparison[
            "test_weighted_f1"
        ].idxmax()
    ]

    # --------------------------------------------------------
    # JSON comparison
    # --------------------------------------------------------

    comparison_records = (
        comparison.where(
            pd.notnull(comparison),
            None,
        ).to_dict(
            orient="records"
        )
    )

    comparison_json = {

        "experiment": (
            "VeriLens NLP model comparison"
        ),

        "dataset": (
            "chengxuphd/liar2"
        ),

        "models_evaluated": loaded_models,

        "metric_used_for_primary_comparison": (
            "test_macro_f1"
        ),

        "models": comparison_records,

        "metric_leaders": {

            "test_macro_f1": {
                "model": best_macro_f1["model"],
                "score": float(
                    best_macro_f1[
                        "test_macro_f1"
                    ]
                ),
            },

            "test_accuracy": {
                "model": best_accuracy["model"],
                "score": float(
                    best_accuracy[
                        "test_accuracy"
                    ]
                ),
            },

            "test_macro_precision": {
                "model": best_macro_precision["model"],
                "score": float(
                    best_macro_precision[
                        "test_macro_precision"
                    ]
                ),
            },

            "test_macro_recall": {
                "model": best_macro_recall["model"],
                "score": float(
                    best_macro_recall[
                        "test_macro_recall"
                    ]
                ),
            },

            "test_weighted_f1": {
                "model": best_weighted_f1["model"],
                "score": float(
                    best_weighted_f1[
                        "test_weighted_f1"
                    ]
                ),
            },
        },
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            comparison_json,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Experiment summary
    # --------------------------------------------------------

    summary = {

        "phase": (
            "Phase 3 — NLP Deep Learning"
        ),

        "status": "completed",

        "dataset": (
            "chengxuphd/liar2"
        ),

        "task": (
            "6-class text classification"
        ),

        "experiments": {

            "classical_ml": [
                "Logistic Regression v2",
                "Linear SVM",
                "Random Forest",
                "XGBoost",
            ],

            "deep_learning": [
                "BiLSTM",
            ],

            "transformer": [
                "DistilBERT Embeddings + LR",
            ],
        },

        "primary_metric": (
            "Test Macro F1"
        ),

        "best_test_macro_f1_model": (
            best_macro_f1["model"]
        ),

        "best_test_macro_f1": float(
            best_macro_f1[
                "test_macro_f1"
            ]
        ),

        "best_test_accuracy_model": (
            best_accuracy["model"]
        ),

        "best_test_accuracy": float(
            best_accuracy[
                "test_accuracy"
            ]
        ),

        "key_observation": (
            "Transformer embeddings provided "
            "the strongest test Macro F1 among "
            "the evaluated NLP models, while "
            "classical TF-IDF models remained "
            "competitive on accuracy."
        ),

        "engineering_notes": [

            (
                "The BiLSTM experiment showed "
                "substantial train-validation "
                "divergence, indicating overfitting."
            ),

            (
                "DistilBERT was evaluated using "
                "frozen pretrained embeddings "
                "because the available environment "
                "was CPU-only."
            ),

            (
                "Model selection should consider "
                "Macro F1 because the six classes "
                "are not perfectly balanced."
            ),

            (
                "LIAR2 is a benchmark dataset and "
                "should not be treated as a universal "
                "truth detector."
            ),
        ],

        "artifacts": [

            OUTPUT_CSV,

            OUTPUT_JSON,

            SUMMARY_JSON,
        ],
    }

    with open(
        SUMMARY_JSON,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Terminal report
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "NLP MODEL COMPARISON"
    )

    print("=" * 70)

    print()

    display_columns = [
        "model",
        "family",
        "test_accuracy",
        "test_macro_f1",
        "test_weighted_f1",
    ]

    print(
        comparison[
            display_columns
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print()

    print("=" * 70)

    print(
        "METRIC LEADERS"
    )

    print("=" * 70)

    print()

    print(
        f"Test Macro F1: "
        f"{best_macro_f1['model']} "
        f"({best_macro_f1['test_macro_f1']:.4f})"
    )

    print(
        f"Test Accuracy: "
        f"{best_accuracy['model']} "
        f"({best_accuracy['test_accuracy']:.4f})"
    )

    print(
        f"Test Macro Precision: "
        f"{best_macro_precision['model']} "
        f"({best_macro_precision['test_macro_precision']:.4f})"
    )

    print(
        f"Test Macro Recall: "
        f"{best_macro_recall['model']} "
        f"({best_macro_recall['test_macro_recall']:.4f})"
    )

    print(
        f"Test Weighted F1: "
        f"{best_weighted_f1['model']} "
        f"({best_weighted_f1['test_weighted_f1']:.4f})"
    )

    print()

    print("=" * 70)

    print(
        "ARTIFACTS"
    )

    print("=" * 70)

    print()

    print(
        OUTPUT_CSV
    )

    print(
        OUTPUT_JSON
    )

    print(
        SUMMARY_JSON
    )

    print()

    print("=" * 70)

    print(
        "PHASE 3 — NLP DEEP LEARNING COMPLETE ✅"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()