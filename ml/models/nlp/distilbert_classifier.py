import json
import os
import random

import joblib
import numpy as np
import pandas as pd
import torch

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

from torch.utils.data import DataLoader, Dataset

from transformers import (
    AutoModel,
    AutoTokenizer,
)


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

MODEL_NAME = "distilbert-base-uncased"

TRAIN_PATH = "data/processed/liar2_features/train.csv"
VAL_PATH = "data/processed/liar2_features/validation.csv"
TEST_PATH = "data/processed/liar2_features/test.csv"

MODEL_DIR = "ml/models/nlp/saved/distilbert_embeddings"
RESULTS_PATH = "ml/evaluation/distilbert_classifier_results.json"

MAX_LENGTH = 96
BATCH_SIZE = 16

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

def set_seed(seed=42):

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================
# DATASET
# ============================================================

class TextDataset(Dataset):

    def __init__(
        self,
        texts,
        tokenizer,
        max_length,
    ):

        self.texts = texts.tolist()
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):

        return len(self.texts)

    def __getitem__(self, index):

        encoding = self.tokenizer(
            self.texts[index],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {
            key: value.squeeze(0)
            for key, value in encoding.items()
        }


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(path):

    df = pd.read_csv(path)

    required_columns = {
        "statement_clean",
        "label",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            f"{path} is missing columns: "
            f"{missing_columns}"
        )

    df = df.dropna(
        subset=[
            "statement_clean",
            "label",
        ]
    )

    texts = df[
        "statement_clean"
    ].astype(str)

    labels = df[
        "label"
    ].astype(int)

    return texts, labels


# ============================================================
# DISTILBERT EMBEDDING EXTRACTION
# ============================================================

def extract_embeddings(
    model,
    dataloader,
):

    model.eval()

    embeddings = []

    total_batches = len(dataloader)

    with torch.no_grad():

        for batch_index, batch in enumerate(
            dataloader,
            start=1,
        ):

            batch = {
                key: value.to(DEVICE)
                for key, value in batch.items()
            }

            outputs = model(
                **batch
            )

            # DistilBERT does not use a CLS token
            # in exactly the same way as BERT.
            #
            # We use the first token representation
            # as a compact sequence representation.

            sequence_embedding = (
                outputs.last_hidden_state[:, 0, :]
            )

            embeddings.append(
                sequence_embedding
                .cpu()
                .numpy()
            )

            if (
                batch_index % 50 == 0
                or batch_index == total_batches
            ):

                progress = (
                    batch_index
                    / total_batches
                    * 100
                )

                print(
                    f"  Processed "
                    f"{batch_index:,}/"
                    f"{total_batches:,} batches "
                    f"({progress:.1f}%)"
                )

    return np.vstack(
        embeddings
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    labels,
    predictions,
):

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="macro",
            zero_division=0,
        )
    )

    weighted_f1 = (
        precision_recall_fscore_support(
            labels,
            predictions,
            average="weighted",
            zero_division=0,
        )[2]
    )

    matrix = confusion_matrix(
        labels,
        predictions,
    )

    report = classification_report(
        labels,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    return {

        "accuracy": float(
            accuracy_score(
                labels,
                predictions,
            )
        ),

        "macro_precision": float(
            precision
        ),

        "macro_recall": float(
            recall
        ),

        "macro_f1": float(
            f1
        ),

        "weighted_f1": float(
            weighted_f1
        ),

        "confusion_matrix": (
            matrix.tolist()
        ),

        "classification_report": report,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    set_seed(SEED)

    print("=" * 70)

    print(
        "VeriLens — DistilBERT Feature-Based NLP Classifier"
    )

    print("=" * 70)

    print()

    print(
        f"PyTorch: {torch.__version__}"
    )

    print(
        f"Transformer: {MODEL_NAME}"
    )

    print(
        f"Device: {DEVICE}"
    )

    print(
        f"CUDA available: "
        f"{torch.cuda.is_available()}"
    )

    print()

    # ========================================================
    # LOAD DATA
    # ========================================================

    print("=" * 70)

    print("Loading LIAR2 datasets")

    print("=" * 70)

    train_texts, train_labels = load_dataset(
        TRAIN_PATH
    )

    val_texts, val_labels = load_dataset(
        VAL_PATH
    )

    test_texts, test_labels = load_dataset(
        TEST_PATH
    )

    print()

    print("Dataset sizes:")

    print(
        f"Train:      {len(train_texts):,}"
    )

    print(
        f"Validation: {len(val_texts):,}"
    )

    print(
        f"Test:       {len(test_texts):,}"
    )

    print()

    # ========================================================
    # TOKENIZER
    # ========================================================

    print("=" * 70)

    print("Loading DistilBERT tokenizer")

    print("=" * 70)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    print(
        "Tokenizer loaded."
    )

    print()

    # ========================================================
    # CREATE DATASETS
    # ========================================================

    train_dataset = TextDataset(
        train_texts,
        tokenizer,
        MAX_LENGTH,
    )

    val_dataset = TextDataset(
        val_texts,
        tokenizer,
        MAX_LENGTH,
    )

    test_dataset = TextDataset(
        test_texts,
        tokenizer,
        MAX_LENGTH,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    print(
        f"Maximum sequence length: "
        f"{MAX_LENGTH}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    print()

    # ========================================================
    # LOAD PRETRAINED DISTILBERT
    # ========================================================

    print("=" * 70)

    print(
        "Loading pretrained DistilBERT"
    )

    print("=" * 70)

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    model.to(DEVICE)

    # ========================================================
    # FREEZE DISTILBERT
    # ========================================================

    for parameter in model.parameters():

        parameter.requires_grad = False

    model.eval()

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print()

    print(
        f"Frozen transformer parameters: "
        f"{parameter_count:,}"
    )

    print(
        "Transformer weights are frozen."
    )

    print(
        "No transformer fine-tuning will be performed."
    )

    print()

    # ========================================================
    # EXTRACT TRAIN EMBEDDINGS
    # ========================================================

    print("=" * 70)

    print(
        "Extracting Transformer Embeddings"
    )

    print("=" * 70)

    print()

    print(
        "Train embeddings..."
    )

    train_embeddings = extract_embeddings(
        model,
        train_loader,
    )

    print()

    print(
        "Train embedding shape:",
        train_embeddings.shape,
    )

    print()

    # ========================================================
    # EXTRACT VALIDATION EMBEDDINGS
    # ========================================================

    print(
        "Validation embeddings..."
    )

    val_embeddings = extract_embeddings(
        model,
        val_loader,
    )

    print()

    print(
        "Validation embedding shape:",
        val_embeddings.shape,
    )

    print()

    # ========================================================
    # EXTRACT TEST EMBEDDINGS
    # ========================================================

    print(
        "Test embeddings..."
    )

    test_embeddings = extract_embeddings(
        model,
        test_loader,
    )

    print()

    print(
        "Test embedding shape:",
        test_embeddings.shape,
    )

    print()

    # ========================================================
    # TRAIN CLASSIFIER
    # ========================================================

    print("=" * 70)

    print(
        "Training Logistic Regression on DistilBERT Embeddings"
    )

    print("=" * 70)

    print()

    classifier = LogisticRegression(
        max_iter=1000,
        C=1.0,
        class_weight="balanced",
        solver="lbfgs",
        random_state=SEED,
    )

    classifier.fit(
        train_embeddings,
        train_labels.to_numpy(),
    )

    print(
        "Classifier training complete."
    )

    print()

    # ========================================================
    # VALIDATION PREDICTIONS
    # ========================================================

    print(
        "Generating validation predictions..."
    )

    val_predictions = classifier.predict(
        val_embeddings
    )

    # ========================================================
    # TEST PREDICTIONS
    # ========================================================

    print(
        "Generating test predictions..."
    )

    test_predictions = classifier.predict(
        test_embeddings
    )

    print()

    # ========================================================
    # CALCULATE METRICS
    # ========================================================

    validation_metrics = calculate_metrics(
        val_labels.to_numpy(),
        val_predictions,
    )

    test_metrics = calculate_metrics(
        test_labels.to_numpy(),
        test_predictions,
    )

    # ========================================================
    # VALIDATION RESULTS
    # ========================================================

    print("=" * 70)

    print(
        "FINAL VALIDATION RESULTS"
    )

    print("=" * 70)

    print()

    print(
        f"Accuracy:        "
        f"{validation_metrics['accuracy']:.4f}"
    )

    print(
        f"Macro Precision: "
        f"{validation_metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall:    "
        f"{validation_metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1:        "
        f"{validation_metrics['macro_f1']:.4f}"
    )

    print(
        f"Weighted F1:     "
        f"{validation_metrics['weighted_f1']:.4f}"
    )

    print()

    # ========================================================
    # TEST RESULTS
    # ========================================================

    print("=" * 70)

    print(
        "FINAL TEST RESULTS"
    )

    print("=" * 70)

    print()

    print(
        f"Accuracy:        "
        f"{test_metrics['accuracy']:.4f}"
    )

    print(
        f"Macro Precision: "
        f"{test_metrics['macro_precision']:.4f}"
    )

    print(
        f"Macro Recall:    "
        f"{test_metrics['macro_recall']:.4f}"
    )

    print(
        f"Macro F1:        "
        f"{test_metrics['macro_f1']:.4f}"
    )

    print(
        f"Weighted F1:     "
        f"{test_metrics['weighted_f1']:.4f}"
    )

    print()

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print("=" * 70)

    print(
        "TEST CONFUSION MATRIX"
    )

    print("=" * 70)

    print()

    for row in test_metrics[
        "confusion_matrix"
    ]:

        print(row)

    print()

    # ========================================================
    # SAVE CLASSIFIER
    # ========================================================

    os.makedirs(
        MODEL_DIR,
        exist_ok=True,
    )

    classifier_path = os.path.join(
        MODEL_DIR,
        "logistic_regression.joblib",
    )

    joblib.dump(
        classifier,
        classifier_path,
    )

    # ========================================================
    # SAVE METADATA
    # ========================================================

    metadata = {

        "model_name": MODEL_NAME,

        "experiment": (
            "Frozen DistilBERT embeddings "
            "with Logistic Regression"
        ),

        "embedding_method": (
            "First-token hidden representation"
        ),

        "task": (
            "6-class text classification"
        ),

        "dataset": (
            "chengxuphd/liar2"
        ),

        "device": str(DEVICE),

        "seed": SEED,

        "max_length": MAX_LENGTH,

        "batch_size": BATCH_SIZE,

        "embedding_dimension": int(
            train_embeddings.shape[1]
        ),

        "transformer_parameters": int(
            parameter_count
        ),

        "train_size": int(
            len(train_texts)
        ),

        "validation_size": int(
            len(val_texts)
        ),

        "test_size": int(
            len(test_texts)
        ),

        "validation": validation_metrics,

        "test": test_metrics,
    }

    os.makedirs(
        os.path.dirname(RESULTS_PATH),
        exist_ok=True,
    )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
        )

    # ========================================================
    # FINAL ARTIFACT SUMMARY
    # ========================================================

    print("=" * 70)

    print(
        "ARTIFACTS"
    )

    print("=" * 70)

    print()

    print(
        f"Classifier:"
    )

    print(
        f"  {classifier_path}"
    )

    print()

    print(
        f"Results:"
    )

    print(
        f"  {RESULTS_PATH}"
    )

    print()

    print("=" * 70)

    print(
        "DistilBERT feature-based experiment complete. 🚀"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
