from pathlib import Path
import json

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# CONFIG
# ============================================================

ROOT = Path("ml/datasets/multimodal/fakeddit/processed/valid_subset")

TRAIN_FILE = ROOT / "train.csv"
VAL_FILE = ROOT / "validation.csv"
TEST_FILE = ROOT / "test.csv"

OUTPUT_DIR = Path("ml/models/multimodal/saved")
RESULTS_DIR = Path("ml/evaluation/multimodal")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "distilbert-base-uncased"

MAX_LENGTH = 64
BATCH_SIZE = 16
RANDOM_STATE = 42


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ============================================================
# LOAD DATA
# ============================================================

def load_split(path: Path):
    df = pd.read_csv(path)

    texts = df["clean_title"].fillna("").astype(str).tolist()
    labels = df["2_way_label"].astype(int).to_numpy()

    return texts, labels


# ============================================================
# LOAD DISTILBERT
# ============================================================

def load_encoder():
    print("=" * 80)
    print("LOADING DISTILBERT TEXT ENCODER")
    print("=" * 80)

    print(f"Model: {MODEL_NAME}")
    print(f"Device: {DEVICE}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)

    model.to(DEVICE)
    model.eval()

    for parameter in model.parameters():
        parameter.requires_grad = False

    return tokenizer, model


# ============================================================
# EXTRACT EMBEDDINGS
# ============================================================

def extract_embeddings(texts, tokenizer, model):
    embeddings = []

    total = len(texts)

    print(f"Extracting embeddings for {total:,} texts...")

    with torch.no_grad():

        for start in range(0, total, BATCH_SIZE):

            batch_texts = texts[start:start + BATCH_SIZE]

            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )

            encoded = {
                key: value.to(DEVICE)
                for key, value in encoded.items()
            }

            outputs = model(**encoded)

            # CLS token representation
            batch_embeddings = outputs.last_hidden_state[:, 0, :]

            embeddings.append(
                batch_embeddings.cpu().numpy()
            )

            processed = min(start + BATCH_SIZE, total)

            if processed % 500 < BATCH_SIZE or processed == total:
                print(
                    f"  Processed {processed:,}/{total:,}"
                )

    return np.vstack(embeddings)


# ============================================================
# TRAIN CLASSIFIER
# ============================================================

def train_classifier(X_train, y_train):

    print()
    print("=" * 80)
    print("TRAINING TEXT-ONLY CLASSIFIER")
    print("=" * 80)

    classifier = LogisticRegression(
        max_iter=1000,
        C=1.0,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    classifier.fit(X_train, y_train)

    return classifier


# ============================================================
# EVALUATION
# ============================================================

def evaluate(classifier, X, y, split_name):

    predictions = classifier.predict(X)
    probabilities = classifier.predict_proba(X)[:, 1]

    accuracy = accuracy_score(y, predictions)

    precision = precision_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    recall = recall_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        average="weighted",
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y,
        probabilities,
    )

    cm = confusion_matrix(y, predictions)

    print()
    print("=" * 80)
    print(f"{split_name.upper()} RESULTS")
    print("=" * 80)

    print(f"Accuracy       : {accuracy:.4f}")
    print(f"Macro Precision: {precision:.4f}")
    print(f"Macro Recall   : {recall:.4f}")
    print(f"Macro F1       : {macro_f1:.4f}")
    print(f"Weighted F1    : {weighted_f1:.4f}")
    print(f"ROC-AUC        : {roc_auc:.4f}")

    print()
    print("Confusion Matrix:")
    print(cm)

    return {
        "accuracy": float(accuracy),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm.tolist(),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("VERILENS PHASE 5 — TEXT-ONLY MULTIMODAL BASELINE")
    print("=" * 80)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print()
    print("Loading Fakeddit dataset...")

    train_texts, y_train = load_split(TRAIN_FILE)
    val_texts, y_val = load_split(VAL_FILE)
    test_texts, y_test = load_split(TEST_FILE)

    print(f"Train      : {len(train_texts):,}")
    print(f"Validation : {len(val_texts):,}")
    print(f"Test       : {len(test_texts):,}")

    # --------------------------------------------------------
    # Load encoder
    # --------------------------------------------------------

    tokenizer, model = load_encoder()

    # --------------------------------------------------------
    # Extract embeddings
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("EXTRACTING TEXT EMBEDDINGS")
    print("=" * 80)

    X_train = extract_embeddings(
        train_texts,
        tokenizer,
        model,
    )

    X_val = extract_embeddings(
        val_texts,
        tokenizer,
        model,
    )

    X_test = extract_embeddings(
        test_texts,
        tokenizer,
        model,
    )

    print()
    print("Embedding shapes:")
    print(f"Train      : {X_train.shape}")
    print(f"Validation : {X_val.shape}")
    print(f"Test       : {X_test.shape}")

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    classifier = train_classifier(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    val_results = evaluate(
        classifier,
        X_val,
        y_val,
        "validation",
    )

    test_results = evaluate(
        classifier,
        X_test,
        y_test,
        "test",
    )

    # --------------------------------------------------------
    # Save classifier
    # --------------------------------------------------------

    import joblib

    model_path = (
        OUTPUT_DIR /
        "fakeddit_text_distilbert_logistic_regression.joblib"
    )

    joblib.dump(
        classifier,
        model_path,
    )

    # --------------------------------------------------------
    # Save embeddings
    # --------------------------------------------------------

    np.save(
        OUTPUT_DIR / "fakeddit_text_train_embeddings.npy",
        X_train,
    )

    np.save(
        OUTPUT_DIR / "fakeddit_text_validation_embeddings.npy",
        X_val,
    )

    np.save(
        OUTPUT_DIR / "fakeddit_text_test_embeddings.npy",
        X_test,
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {
        "phase": "Phase 5 — Multimodal Intelligence",
        "experiment": "Text-only baseline",
        "dataset": "Fakeddit",
        "dataset_size": {
            "train": len(train_texts),
            "validation": len(val_texts),
            "test": len(test_texts),
        },
        "model": {
            "encoder": MODEL_NAME,
            "classifier": "LogisticRegression",
            "max_length": MAX_LENGTH,
            "batch_size": BATCH_SIZE,
            "embedding_dimension": int(X_train.shape[1]),
            "frozen_encoder": True,
            "random_state": RANDOM_STATE,
        },
        "validation": val_results,
        "test": test_results,
    }

    results_path = (
        RESULTS_DIR /
        "fakeddit_text_baseline_results.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("TEXT-ONLY BASELINE COMPLETE")
    print("=" * 80)

    print(f"Saved classifier : {model_path}")
    print(f"Saved results    : {results_path}")

    print()
    print("NEXT:")
    print("Image-only baseline → Multimodal fusion")


if __name__ == "__main__":
    main()