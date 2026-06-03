#!/usr/bin/env python3
"""QSAR AutoDescriptor Pipeline.

A single-file command line utility that discovers a CSV file next to this
script, validates SMILES with RDKit, calculates basic molecular descriptors and
Morgan fingerprints, optionally trains a binary RandomForest classifier when an
``Activity`` column is available, and writes processed data, metrics, a model,
and plots to disk.
"""

from __future__ import annotations

import glob
import os
import pickle
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski, rdMolDescriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------------------------
# Config section
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path(os.getcwd())
OUTPUT_DATA = SCRIPT_DIR / "processed_data.csv"
OUTPUT_MODEL = SCRIPT_DIR / "model.pkl"
OUTPUT_METRICS = SCRIPT_DIR / "metrics.txt"
PLOTS_DIR = SCRIPT_DIR / "plots"

SMILES_COLUMN = "SMILES"
ACTIVITY_COLUMN = "Activity"

MORGAN_RADIUS = 2
MORGAN_N_BITS = 2048
MORGAN_PREFIX = "Morgan_"

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_ESTIMATORS = 300
MIN_SAMPLES_PER_CLASS_FOR_SPLIT = 2

DESCRIPTOR_COLUMNS = [
    "MolWt",
    "MolLogP",
    "NumHDonors",
    "NumHAcceptors",
    "TPSA",
    "NumRotatableBonds",
]


@dataclass
class ModelResult:
    """Container with model outputs used by reporting and plotting."""

    model: Optional[RandomForestClassifier]
    y_test: Optional[pd.Series]
    y_pred: Optional[np.ndarray]
    y_proba: Optional[np.ndarray]
    feature_names: List[str]
    metrics: dict


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Print a human-readable pipeline message."""
    print(f"[QSAR] {message}")



def find_csv(directory: Path = SCRIPT_DIR) -> Path:
    """Find a CSV file in the script directory.

    The specification asks for automatic discovery. When multiple CSV files are
    present, the lexicographically first file is used and a warning is printed.
    Generated output files are ignored when any other CSV candidate exists so a
    rerun is less likely to accidentally use its own descriptor table.
    """
    pattern = str(directory / "*.csv")
    csv_files = sorted(Path(path) for path in glob.glob(pattern))
    if not csv_files:
        raise FileNotFoundError(f"No .csv files found in {directory}")

    non_generated = [path for path in csv_files if path.name != OUTPUT_DATA.name]
    candidates = non_generated or csv_files

    if len(candidates) > 1:
        warnings.warn(
            "Multiple CSV files found; using the first one: "
            f"{candidates[0].name}",
            RuntimeWarning,
        )
    return candidates[0]



def load_data(csv_path: Path) -> pd.DataFrame:
    """Load a CSV file and assert that the SMILES column exists."""
    log(f"Loading data from {csv_path}")
    data = pd.read_csv(csv_path)
    if SMILES_COLUMN not in data.columns:
        raise ValueError(f"Input CSV must contain a '{SMILES_COLUMN}' column")
    return data



def canonical_smiles(mol: Chem.Mol) -> str:
    """Return canonical isomeric SMILES for duplicate detection."""
    return Chem.MolToSmiles(mol, isomericSmiles=True)



def validate_smiles(data: pd.DataFrame) -> Tuple[pd.DataFrame, List[Chem.Mol]]:
    """Remove empty, invalid, and duplicate SMILES rows.

    RDKit ``Chem.MolFromSmiles`` returns ``None`` for malformed SMILES. Valid
    molecules are canonicalized and duplicate canonical structures are dropped.
    """
    valid_rows = []
    valid_mols: List[Chem.Mol] = []
    seen_canonical = set()

    for index, row in data.iterrows():
        raw_smiles = row.get(SMILES_COLUMN)
        if pd.isna(raw_smiles):
            continue

        smiles = str(raw_smiles).strip()
        if not smiles:
            continue

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            continue

        canonical = canonical_smiles(mol)
        if canonical in seen_canonical:
            continue

        seen_canonical.add(canonical)
        cleaned_row = row.copy()
        cleaned_row[SMILES_COLUMN] = canonical
        valid_rows.append(cleaned_row)
        valid_mols.append(mol)

    cleaned = pd.DataFrame(valid_rows).reset_index(drop=True)
    return cleaned, valid_mols



def compute_descriptors(mols: Sequence[Chem.Mol]) -> pd.DataFrame:
    """Compute the requested RDKit descriptors for each molecule."""
    records = []
    for mol in mols:
        records.append(
            {
                "MolWt": Descriptors.MolWt(mol),
                "MolLogP": Crippen.MolLogP(mol),
                "NumHDonors": Lipinski.NumHDonors(mol),
                "NumHAcceptors": Lipinski.NumHAcceptors(mol),
                "TPSA": rdMolDescriptors.CalcTPSA(mol),
                "NumRotatableBonds": Lipinski.NumRotatableBonds(mol),
            }
        )
    return pd.DataFrame(records, columns=DESCRIPTOR_COLUMNS)



def compute_fingerprints(
    mols: Sequence[Chem.Mol],
    radius: int = MORGAN_RADIUS,
    n_bits: int = MORGAN_N_BITS,
) -> pd.DataFrame:
    """Compute Morgan fingerprints and return them as binary feature columns."""
    fingerprint_rows = np.zeros((len(mols), n_bits), dtype=np.uint8)
    for row_index, mol in enumerate(mols):
        bit_vector = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        DataStructs.ConvertToNumpyArray(bit_vector, fingerprint_rows[row_index])

    columns = [f"{MORGAN_PREFIX}{bit_index}" for bit_index in range(n_bits)]
    return pd.DataFrame(fingerprint_rows, columns=columns)



def prepare_activity(activity: pd.Series) -> pd.Series:
    """Normalize activity labels to binary integers when possible."""
    non_null = activity.dropna()
    if non_null.empty:
        raise ValueError("Activity column is empty")

    if pd.api.types.is_numeric_dtype(non_null):
        labels = activity.astype("Int64")
    else:
        codes, uniques = pd.factorize(activity.astype(str), sort=True)
        if len(uniques) > 2:
            raise ValueError("Activity column must contain at most two classes")
        labels = pd.Series(codes, index=activity.index, dtype="int64")

    unique_labels = sorted(pd.Series(labels).dropna().unique().tolist())
    if len(unique_labels) != 2:
        raise ValueError("Binary classification requires exactly two Activity classes")

    mapping = {label: integer for integer, label in enumerate(unique_labels)}
    return pd.Series(labels.map(mapping), index=activity.index, dtype="int64")



def build_feature_matrix(processed: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Select descriptor and fingerprint columns for model training."""
    fingerprint_columns = [column for column in processed.columns if column.startswith(MORGAN_PREFIX)]
    feature_names = DESCRIPTOR_COLUMNS + fingerprint_columns
    return processed[feature_names].copy(), feature_names


# ---------------------------------------------------------------------------
# ML functions
# ---------------------------------------------------------------------------


def train_model(processed: pd.DataFrame) -> ModelResult:
    """Train a RandomForestClassifier when an Activity column is available."""
    if ACTIVITY_COLUMN not in processed.columns:
        return ModelResult(
            model=None,
            y_test=None,
            y_pred=None,
            y_proba=None,
            feature_names=[],
            metrics={"status": "skipped", "reason": "Activity column not found"},
        )

    labeled = processed.dropna(subset=[ACTIVITY_COLUMN]).copy()
    if labeled.empty:
        return ModelResult(
            model=None,
            y_test=None,
            y_pred=None,
            y_proba=None,
            feature_names=[],
            metrics={"status": "skipped", "reason": "Activity column is empty"},
        )

    try:
        y = prepare_activity(labeled[ACTIVITY_COLUMN])
    except ValueError as exc:
        return ModelResult(
            model=None,
            y_test=None,
            y_pred=None,
            y_proba=None,
            feature_names=[],
            metrics={"status": "skipped", "reason": str(exc)},
        )

    X, feature_names = build_feature_matrix(labeled)
    class_counts = y.value_counts()
    if len(y) < 5 or len(class_counts) != 2:
        return ModelResult(
            model=None,
            y_test=None,
            y_pred=None,
            y_proba=None,
            feature_names=feature_names,
            metrics={"status": "skipped", "reason": "Not enough labeled samples"},
        )

    stratify = y if class_counts.min() >= MIN_SAMPLES_PER_CLASS_FOR_SPLIT else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = None
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]

    metrics = evaluate_model(y_test, y_pred, y_proba)
    return ModelResult(
        model=model,
        y_test=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        feature_names=feature_names,
        metrics=metrics,
    )



def evaluate_model(
    y_test: pd.Series,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray] = None,
) -> dict:
    """Calculate accuracy, confusion matrix, and ROC-AUC when possible."""
    metrics = {
        "status": "trained",
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    if y_proba is not None and len(np.unique(y_test)) == 2:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba))
        except ValueError as exc:
            metrics["roc_auc"] = f"not available: {exc}"
    else:
        metrics["roc_auc"] = "not available"
    return metrics



def save_model(model_result: ModelResult, output_path: Path = OUTPUT_MODEL) -> None:
    """Serialize the trained model if one exists."""
    if model_result.model is None:
        log("Model was not trained; model.pkl will not be written")
        return
    with output_path.open("wb") as handle:
        pickle.dump(
            {
                "model": model_result.model,
                "feature_names": model_result.feature_names,
                "descriptor_columns": DESCRIPTOR_COLUMNS,
                "fingerprint_radius": MORGAN_RADIUS,
                "fingerprint_bits": MORGAN_N_BITS,
            },
            handle,
        )
    log(f"Saved trained model to {output_path}")



def save_metrics(model_result: ModelResult, output_path: Path = OUTPUT_METRICS) -> None:
    """Write model metrics or a skip reason to a text file."""
    lines = ["QSAR AutoDescriptor Pipeline metrics", ""]
    for key, value in model_result.metrics.items():
        lines.append(f"{key}: {value}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"Saved metrics to {output_path}")


# ---------------------------------------------------------------------------
# Visualization functions
# ---------------------------------------------------------------------------


def ensure_plots_dir() -> None:
    """Create the plots directory if it does not already exist."""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)



def plot_distributions(processed: pd.DataFrame) -> None:
    """Plot molecular weight and LogP distributions."""
    ensure_plots_dir()
    histogram_specs = [
        ("MolWt", "Molecular Weight Distribution", "Molecular Weight", "hist_molwt.png"),
        ("MolLogP", "LogP Distribution", "MolLogP", "hist_logp.png"),
    ]

    for column, title, xlabel, filename in histogram_specs:
        plt.figure(figsize=(8, 5))
        plt.hist(processed[column].dropna(), bins=30, color="#4c72b0", edgecolor="black")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel("Count")
        plt.tight_layout()
        output_path = PLOTS_DIR / filename
        plt.savefig(output_path, dpi=150)
        plt.close()
        log(f"Saved plot {output_path}")



def plot_confusion_matrix(model_result: ModelResult) -> None:
    """Plot the confusion matrix heatmap for a trained model."""
    if model_result.y_test is None or model_result.y_pred is None:
        log("Confusion matrix plot skipped because no model predictions exist")
        return

    ensure_plots_dir()
    cm = confusion_matrix(model_result.y_test, model_result.y_pred)
    display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
    display.plot(cmap="Blues", values_format="d")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    output_path = PLOTS_DIR / "confusion_matrix.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    log(f"Saved plot {output_path}")



def plot_feature_importance(model_result: ModelResult, top_n: int = 20) -> None:
    """Plot the top RandomForest feature importances."""
    if model_result.model is None:
        log("Feature importance plot skipped because no model was trained")
        return

    ensure_plots_dir()
    importances = pd.Series(
        model_result.model.feature_importances_,
        index=model_result.feature_names,
        dtype="float64",
    ).sort_values(ascending=False)
    top_importances = importances.head(top_n).sort_values()

    plt.figure(figsize=(9, 7))
    top_importances.plot(kind="barh", color="#55a868")
    plt.title(f"Top {len(top_importances)} RandomForest Feature Importances")
    plt.xlabel("Importance")
    plt.tight_layout()
    output_path = PLOTS_DIR / "feature_importance.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    log(f"Saved plot {output_path}")


# ---------------------------------------------------------------------------
# Main execution block
# ---------------------------------------------------------------------------


def run_pipeline() -> int:
    """Run the full QSAR pipeline and return a process exit code."""
    log("Starting QSAR AutoDescriptor Pipeline")
    try:
        csv_path = find_csv(SCRIPT_DIR)
        log(f"Found CSV: {csv_path.name}")

        raw_data = load_data(csv_path)
        molecules_before = len(raw_data)
        log(f"Molecules before cleaning: {molecules_before}")

        cleaned_data, mols = validate_smiles(raw_data)
        molecules_after = len(cleaned_data)
        log(f"Molecules after cleaning: {molecules_after}")
        if molecules_after == 0:
            raise ValueError("No valid molecules remain after SMILES validation")

        log("Computing RDKit descriptors")
        descriptors = compute_descriptors(mols)

        log(
            "Computing Morgan fingerprints "
            f"(radius={MORGAN_RADIUS}, nBits={MORGAN_N_BITS})"
        )
        fingerprints = compute_fingerprints(mols)

        processed = pd.concat(
            [cleaned_data.reset_index(drop=True), descriptors, fingerprints],
            axis=1,
        )
        processed.to_csv(OUTPUT_DATA, index=False)
        log(f"Saved processed data to {OUTPUT_DATA}")

        log("Building visualizations")
        plot_distributions(processed)

        log("Training/evaluating model when Activity is available")
        model_result = train_model(processed)
        save_metrics(model_result)
        save_model(model_result)
        plot_confusion_matrix(model_result)
        plot_feature_importance(model_result)

        log("Metrics:")
        for key, value in model_result.metrics.items():
            log(f"  {key}: {value}")

        log("Pipeline finished successfully")
        return 0
    except Exception as exc:  # noqa: BLE001 - command line entry point should report cleanly
        print(f"[QSAR][ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run_pipeline())
