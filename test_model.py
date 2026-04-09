"""
test_model.py - Send test data to the deployed model server and evaluate accuracy
               Exits with code 1 on failure so Jenkins marks the stage as failed
"""

import os
import sys
import json
import pickle
import requests
import numpy as np
from sklearn.metrics import accuracy_score, classification_report

DATA_DIR       = os.getenv("DATA_DIR", "data")
SERVE_HOST     = os.getenv("SERVE_HOST", "127.0.0.1")
SERVE_PORT     = int(os.getenv("SERVE_PORT", "5001"))
ACCURACY_THRESHOLD = float(os.getenv("ACCURACY_THRESHOLD", "0.90"))

ENDPOINT = f"http://{SERVE_HOST}:{SERVE_PORT}/invocations"
HEADERS  = {"Content-Type": "application/json"}


def test():
    # Load test split
    with open(f"{DATA_DIR}/test.pkl", "rb") as f:
        X_test, y_test = pickle.load(f)

    # Build request payload (MLflow expects 'dataframe_split' format)
    payload = {
        "dataframe_split": {
            "columns": list(X_test.columns),
            "data": X_test.values.tolist(),
        }
    }

    print(f"[test] Sending {len(X_test)} samples to {ENDPOINT}")
    response = requests.post(ENDPOINT, headers=HEADERS, data=json.dumps(payload), timeout=30)

    if response.status_code != 200:
        print(f"[test] ERROR: Server returned {response.status_code}")
        print(response.text)
        sys.exit(1)

    predictions = response.json()["predictions"]
    y_pred      = np.array(predictions)
    acc         = accuracy_score(y_test, y_pred)

    print(f"\n[test] Accuracy: {acc:.4f}  (threshold: {ACCURACY_THRESHOLD})")
    print(classification_report(
        y_test, y_pred,
        target_names=["setosa", "versicolor", "virginica"]
    ))

    # Write result for shared library to read
    result = "PASS" if acc >= ACCURACY_THRESHOLD else "FAIL"
    with open("test_result.txt", "w") as f:
        f.write(f"{result}\n{acc:.4f}")

    if acc < ACCURACY_THRESHOLD:
        print(f"[test] FAILED — accuracy {acc:.4f} below threshold {ACCURACY_THRESHOLD}")
        sys.exit(1)

    print(f"[test] PASSED — accuracy {acc:.4f}")


if __name__ == "__main__":
    test()
