"""
ingest.py - Load and split the Iris dataset, save to disk
"""

import os
import pickle
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

DATA_DIR = os.getenv("DATA_DIR", "data")


def ingest():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Load Iris dataset
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name="target")

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Save splits
    with open(f"{DATA_DIR}/train.pkl", "wb") as f:
        pickle.dump((X_train, y_train), f)

    with open(f"{DATA_DIR}/test.pkl", "wb") as f:
        pickle.dump((X_test, y_test), f)

    print(f"[ingest] Train size: {len(X_train)} | Test size: {len(X_test)}")
    print(f"[ingest] Data saved to '{DATA_DIR}/'")


if __name__ == "__main__":
    ingest()
