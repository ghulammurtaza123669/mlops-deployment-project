"""
train.py - Train Random Forest on Iris, log to MLflow, register with alias 'Challenger'
"""

import os
import pickle
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

DATA_DIR    = os.getenv("DATA_DIR", "data")
MLFLOW_URI  = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
EXPERIMENT  = os.getenv("MLFLOW_EXPERIMENT", "iris-mlops")
MODEL_NAME  = os.getenv("MODEL_NAME", "iris-random-forest")

# Hyperparameters (override via env vars in Jenkins)
N_ESTIMATORS = int(os.getenv("N_ESTIMATORS", "100"))
MAX_DEPTH    = int(os.getenv("MAX_DEPTH", "5"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))


def train():
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT)

    # Load data
    with open(f"{DATA_DIR}/train.pkl", "rb") as f:
        X_train, y_train = pickle.load(f)
    with open(f"{DATA_DIR}/test.pkl", "rb") as f:
        X_test, y_test = pickle.load(f)

    with mlflow.start_run() as run:
        # Log hyperparameters
        mlflow.log_params({
            "n_estimators": N_ESTIMATORS,
            "max_depth":    MAX_DEPTH,
            "random_state": RANDOM_STATE,
        })

        # Train
        model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE,
        )
        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        acc    = accuracy_score(y_test, y_pred)
        mlflow.log_metric("accuracy", acc)

        print(f"[train] Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred, target_names=["setosa","versicolor","virginica"]))

        # Log model artifact
        mlflow.sklearn.log_model(model, artifact_path="model")

        # Register model and assign alias 'Challenger'
        model_uri = f"runs:/{run.info.run_id}/model"
        mv = mlflow.register_model(model_uri, MODEL_NAME)

        client = mlflow.tracking.MlflowClient(MLFLOW_URI)
        client.set_registered_model_alias(MODEL_NAME, "Challenger", mv.version)

        print(f"[train] Registered model v{mv.version} with alias 'Challenger'")
        print(f"[train] Run ID: {run.info.run_id}")

        # Write run_id to file so downstream stages can reference it
        with open("run_id.txt", "w") as f:
            f.write(run.info.run_id)


if __name__ == "__main__":
    train()
