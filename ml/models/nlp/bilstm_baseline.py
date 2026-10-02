from __future__ import annotations

import json
import random
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence
from torch.utils.data import DataLoader, Dataset


# ============================================================
# Configuration
# ============================================================

SEED = 42

# IMPORTANT:
# statement_clean was created during Phase 1 preprocessing.
DATA_DIR = Path("data/processed/liar2_features")

MODEL_DIR = Path("ml/models/nlp/saved")
EVALUATION_DIR = Path("ml/evaluation")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = DATA_DIR / "train.csv"
VALIDATION_FILE = DATA_DIR / "validation.csv"
TEST_FILE = DATA_DIR / "test.csv"

MODEL_FILE = MODEL_DIR / "bilstm_baseline.pt"
VOCABULARY_FILE = MODEL_DIR / "bilstm_vocabulary.json"
RESULTS_FILE = EVALUATION_DIR / "bilstm_baseline_results.json"

TEXT_COLUMN = "statement_clean"
LABEL_COLUMN = "label"

NUM_CLASSES = 6

MAX_VOCAB_SIZE = 20_000
MIN_TOKEN_FREQUENCY = 2
MAX_SEQUENCE_LENGTH = 80

EMBEDDING_DIM = 128
HIDDEN_DIM = 128
NUM_LAYERS = 1
DROPOUT = 0.30

BATCH_SIZE = 64
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4

EPOCHS = 8
PATIENCE = 2

PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


# ============================================================
# Reproducibility
# ============================================================

def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ============================================================
# Tokenization
# ============================================================

def tokenize(text: str) -> list[str]:
    return str(text).split()


def build_vocabulary(
    texts: pd.Series,
    max_vocab_size: int,
    min_frequency: int,
) -> dict[str, int]:

    counter = Counter()

    for text in texts:
        counter.update(tokenize(text))

    vocabulary = {
        PAD_TOKEN: 0,
        UNK_TOKEN: 1,
    }

    sorted_tokens = sorted(
        (
            (token, frequency)
            for token, frequency in counter.items()
            if frequency >= min_frequency
        ),
        key=lambda item: (-item[1], item[0]),
    )

    available_slots = max_vocab_size - len(vocabulary)

    for token, _ in sorted_tokens[:available_slots]:
        vocabulary[token] = len(vocabulary)

    return vocabulary


def encode_text(
    text: str,
    vocabulary: dict[str, int],
    max_length: int,
) -> list[int]:

    tokens = tokenize(text)

    if not tokens:
        tokens = [UNK_TOKEN]

    tokens = tokens[:max_length]

    return [
        vocabulary.get(token, vocabulary[UNK_TOKEN])
        for token in tokens
    ]


# ============================================================
# Dataset
# ============================================================

class TextDataset(Dataset):

    def __init__(
        self,
        dataframe: pd.DataFrame,
        vocabulary: dict[str, int],
        max_length: int,
    ) -> None:

        self.texts = dataframe[TEXT_COLUMN].astype(str).tolist()

        self.labels = (
            dataframe[LABEL_COLUMN]
            .astype(int)
            .tolist()
        )

        self.encoded_texts = [
            encode_text(
                text,
                vocabulary,
                max_length,
            )
            for text in self.texts
        ]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int):

        sequence = torch.tensor(
            self.encoded_texts[index],
            dtype=torch.long,
        )

        label = torch.tensor(
            self.labels[index],
            dtype=torch.long,
        )

        return sequence, label


def collate_batch(batch):

    sequences, labels = zip(*batch)

    lengths = torch.tensor(
        [len(sequence) for sequence in sequences],
        dtype=torch.long,
    )

    padded_sequences = pad_sequence(
        sequences,
        batch_first=True,
        padding_value=0,
    )

    labels = torch.stack(labels)

    return (
        padded_sequences,
        lengths,
        labels,
    )


# ============================================================
# BiLSTM Model
# ============================================================

class BiLSTMClassifier(nn.Module):

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_classes: int,
        num_layers: int = 1,
        dropout: float = 0.3,
    ) -> None:

        super().__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=0,
        )

        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        self.dropout = nn.Dropout(dropout)

        self.classifier = nn.Linear(
            hidden_dim * 2,
            num_classes,
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        lengths: torch.Tensor,
    ) -> torch.Tensor:

        embedded = self.embedding(input_ids)

        packed = pack_padded_sequence(
            embedded,
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False,
        )

        _, (hidden, _) = self.lstm(packed)

        forward_hidden = hidden[-2]
        backward_hidden = hidden[-1]

        combined_hidden = torch.cat(
            (
                forward_hidden,
                backward_hidden,
            ),
            dim=1,
        )

        combined_hidden = self.dropout(
            combined_hidden
        )

        logits = self.classifier(
            combined_hidden
        )

        return logits


# ============================================================
# Data Loading
# ============================================================

def load_data():

    train_df = pd.read_csv(
        TRAIN_FILE
    )

    validation_df = pd.read_csv(
        VALIDATION_FILE
    )

    test_df = pd.read_csv(
        TEST_FILE
    )

    required_columns = {
        TEXT_COLUMN,
        LABEL_COLUMN,
    }

    for name, dataframe in [
        ("train", train_df),
        ("validation", validation_df),
        ("test", test_df),
    ]:

        missing = (
            required_columns
            - set(dataframe.columns)
        )

        if missing:
            raise ValueError(
                f"{name} dataset is missing columns: "
                f"{missing}"
            )

    return (
        train_df,
        validation_df,
        test_df,
    )


# ============================================================
# Evaluation
# ============================================================

def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
):

    model.eval()

    total_loss = 0.0

    all_predictions = []
    all_labels = []

    with torch.no_grad():

        for (
            input_ids,
            lengths,
            labels,
        ) in loader:

            input_ids = input_ids.to(device)
            lengths = lengths.to(device)
            labels = labels.to(device)

            logits = model(
                input_ids,
                lengths,
            )

            loss = criterion(
                logits,
                labels,
            )

            total_loss += (
                loss.item()
                * labels.size(0)
            )

            predictions = torch.argmax(
                logits,
                dim=1,
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

            all_labels.extend(
                labels.cpu().numpy()
            )

    average_loss = (
        total_loss
        / len(loader.dataset)
    )

    accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    macro_precision = precision_score(
        all_labels,
        all_predictions,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        all_labels,
        all_predictions,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        all_labels,
        all_predictions,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        all_labels,
        all_predictions,
        average="weighted",
        zero_division=0,
    )

    return {
        "loss": average_loss,
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "predictions": all_predictions,
        "labels": all_labels,
    }


# ============================================================
# Training
# ============================================================

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    validation_loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    vocabulary: dict[str, int],
):

    best_validation_f1 = -1.0

    epochs_without_improvement = 0

    history = []

    for epoch in range(
        1,
        EPOCHS + 1,
    ):

        model.train()

        start_time = time.time()

        total_train_loss = 0.0

        train_predictions = []
        train_labels = []

        for (
            input_ids,
            lengths,
            labels,
        ) in train_loader:

            input_ids = input_ids.to(device)
            lengths = lengths.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            logits = model(
                input_ids,
                lengths,
            )

            loss = criterion(
                logits,
                labels,
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                max_norm=1.0,
            )

            optimizer.step()

            total_train_loss += (
                loss.item()
                * labels.size(0)
            )

            predictions = torch.argmax(
                logits,
                dim=1,
            )

            train_predictions.extend(
                predictions.detach()
                .cpu()
                .numpy()
            )

            train_labels.extend(
                labels.detach()
                .cpu()
                .numpy()
            )

        train_loss = (
            total_train_loss
            / len(train_loader.dataset)
        )

        train_f1 = f1_score(
            train_labels,
            train_predictions,
            average="macro",
            zero_division=0,
        )

        validation_metrics = evaluate(
            model,
            validation_loader,
            criterion,
            device,
        )

        epoch_time = (
            time.time()
            - start_time
        )

        epoch_record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_macro_f1": train_f1,
            "validation_loss": validation_metrics[
                "loss"
            ],
            "validation_accuracy": validation_metrics[
                "accuracy"
            ],
            "validation_macro_f1": validation_metrics[
                "macro_f1"
            ],
            "epoch_time_seconds": epoch_time,
        }

        history.append(epoch_record)

        print(
            f"Epoch {epoch}/{EPOCHS} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Macro F1: {train_f1:.4f} | "
            f"Val Loss: "
            f"{validation_metrics['loss']:.4f} | "
            f"Val Accuracy: "
            f"{validation_metrics['accuracy']:.4f} | "
            f"Val Macro F1: "
            f"{validation_metrics['macro_f1']:.4f} | "
            f"Time: {epoch_time:.1f}s"
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if (
            validation_metrics["macro_f1"]
            > best_validation_f1
        ):

            best_validation_f1 = (
                validation_metrics["macro_f1"]
            )

            torch.save(
                {
                    "model_state_dict":
                        model.state_dict(),

                    "vocabulary":
                        vocabulary,

                    "config": {
                        "embedding_dim":
                            EMBEDDING_DIM,

                        "hidden_dim":
                            HIDDEN_DIM,

                        "num_classes":
                            NUM_CLASSES,

                        "num_layers":
                            NUM_LAYERS,

                        "dropout":
                            DROPOUT,

                        "max_sequence_length":
                            MAX_SEQUENCE_LENGTH,
                    },
                },
                MODEL_FILE,
            )

            epochs_without_improvement = 0

            print(
                "  ✓ Saved best model "
                f"(Val Macro F1: "
                f"{best_validation_f1:.4f})"
            )

        else:

            epochs_without_improvement += 1

            if (
                epochs_without_improvement
                >= PATIENCE
            ):

                print(
                    "  Early stopping triggered."
                )

                break

    return history


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    set_seed()

    device = torch.device("cpu")

    print("=" * 70)
    print("VeriLens — BiLSTM Neural NLP Baseline")
    print("=" * 70)

    print(f"Device: {device}")
    print(
        f"Training file: {TRAIN_FILE}"
    )

    print()

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        train_df,
        validation_df,
        test_df,
    ) = load_data()

    print("Dataset sizes:")

    print(
        f"  Train:      {len(train_df):,}"
    )

    print(
        f"  Validation: {len(validation_df):,}"
    )

    print(
        f"  Test:       {len(test_df):,}"
    )

    print()

    # --------------------------------------------------------
    # Build vocabulary ONLY from training data
    # --------------------------------------------------------

    print(
        "Building vocabulary from "
        "training data..."
    )

    vocabulary = build_vocabulary(
        train_df[TEXT_COLUMN],
        max_vocab_size=MAX_VOCAB_SIZE,
        min_frequency=MIN_TOKEN_FREQUENCY,
    )

    print(
        f"Vocabulary size: "
        f"{len(vocabulary):,}"
    )

    print()

    # --------------------------------------------------------
    # Create datasets
    # --------------------------------------------------------

    train_dataset = TextDataset(
        train_df,
        vocabulary,
        MAX_SEQUENCE_LENGTH,
    )

    validation_dataset = TextDataset(
        validation_df,
        vocabulary,
        MAX_SEQUENCE_LENGTH,
    )

    test_dataset = TextDataset(
        test_df,
        vocabulary,
        MAX_SEQUENCE_LENGTH,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_batch,
        num_workers=0,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_batch,
        num_workers=0,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_batch,
        num_workers=0,
    )

    # --------------------------------------------------------
    # Class weights
    # --------------------------------------------------------

    label_counts = np.bincount(
        train_df[LABEL_COLUMN]
        .astype(int),
        minlength=NUM_CLASSES,
    )

    class_weights = (
        len(train_df)
        / (
            NUM_CLASSES
            * label_counts
        )
    )

    class_weights = torch.tensor(
        class_weights,
        dtype=torch.float32,
    )

    print("Class counts:")

    for label, count in enumerate(
        label_counts
    ):

        print(
            f"  Class {label}: "
            f"{count:,}"
        )

    print()

    print("Class weights:")

    print(
        class_weights.numpy()
    )

    print()

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = BiLSTMClassifier(
        vocab_size=len(vocabulary),
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        num_classes=NUM_CLASSES,
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights.to(device)
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    print("=" * 70)
    print("Model")
    print("=" * 70)

    print(model)

    print()

    print(
        f"Trainable parameters: "
        f"{parameter_count:,}"
    )

    print()

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    training_start = time.time()

    history = train_model(
        model=model,
        train_loader=train_loader,
        validation_loader=validation_loader,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        vocabulary=vocabulary,
    )

    training_time = (
        time.time()
        - training_start
    )

    # --------------------------------------------------------
    # Load best model
    # --------------------------------------------------------

    checkpoint = torch.load(
        MODEL_FILE,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    # --------------------------------------------------------
    # Final validation evaluation
    # --------------------------------------------------------

    validation_metrics = evaluate(
        model,
        validation_loader,
        criterion,
        device,
    )

    # --------------------------------------------------------
    # Final test evaluation
    # --------------------------------------------------------

    test_metrics = evaluate(
        model,
        test_loader,
        criterion,
        device,
    )

    print()

    print("=" * 70)
    print("Final Validation Results")
    print("=" * 70)

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

    print("=" * 70)
    print("Final Test Results")
    print("=" * 70)

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

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    report = classification_report(
        test_metrics["labels"],
        test_metrics["predictions"],
        labels=list(range(NUM_CLASSES)),
        output_dict=True,
        zero_division=0,
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    confusion = confusion_matrix(
        test_metrics["labels"],
        test_metrics["predictions"],
        labels=list(range(NUM_CLASSES)),
    )

    print()

    print(
        "Test Confusion Matrix:"
    )

    print(confusion)

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    results = {
        "model": "BiLSTM",
        "task": (
            "LIAR2 six-class "
            "text classification"
        ),
        "device": str(device),

        "dataset": {
            "train_samples":
                len(train_df),

            "validation_samples":
                len(validation_df),

            "test_samples":
                len(test_df),
        },

        "configuration": {
            "vocabulary_size":
                len(vocabulary),

            "max_sequence_length":
                MAX_SEQUENCE_LENGTH,

            "embedding_dim":
                EMBEDDING_DIM,

            "hidden_dim":
                HIDDEN_DIM,

            "num_layers":
                NUM_LAYERS,

            "dropout":
                DROPOUT,

            "batch_size":
                BATCH_SIZE,

            "learning_rate":
                LEARNING_RATE,

            "weight_decay":
                WEIGHT_DECAY,

            "epochs_requested":
                EPOCHS,

            "epochs_completed":
                len(history),
        },

        "training_time_seconds":
            training_time,

        "validation": {
            "loss":
                validation_metrics["loss"],

            "accuracy":
                validation_metrics["accuracy"],

            "macro_precision":
                validation_metrics[
                    "macro_precision"
                ],

            "macro_recall":
                validation_metrics[
                    "macro_recall"
                ],

            "macro_f1":
                validation_metrics[
                    "macro_f1"
                ],

            "weighted_f1":
                validation_metrics[
                    "weighted_f1"
                ],
        },

        "test": {
            "loss":
                test_metrics["loss"],

            "accuracy":
                test_metrics["accuracy"],

            "macro_precision":
                test_metrics[
                    "macro_precision"
                ],

            "macro_recall":
                test_metrics[
                    "macro_recall"
                ],

            "macro_f1":
                test_metrics[
                    "macro_f1"
                ],

            "weighted_f1":
                test_metrics[
                    "weighted_f1"
                ],
        },

        "classification_report":
            report,

        "confusion_matrix":
            confusion.tolist(),

        "training_history":
            history,
    }

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )

    # --------------------------------------------------------
    # Save vocabulary
    # --------------------------------------------------------

    with open(
        VOCABULARY_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            vocabulary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Final artifact summary
    # --------------------------------------------------------

    print()

    print("=" * 70)
    print("Artifacts")
    print("=" * 70)

    print(
        f"Model:      {MODEL_FILE}"
    )

    print(
        f"Vocabulary: {VOCABULARY_FILE}"
    )

    print(
        f"Results:    {RESULTS_FILE}"
    )

    print()

    print(
        "BiLSTM training complete."
    )