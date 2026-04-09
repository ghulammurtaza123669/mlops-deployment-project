"""
deploy.py - Start MLflow model server for a given alias
           Called in Dev, Pre-prod, and Prod pipelines
"""

import os
import subprocess
import sys
import time
import requests

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "iris-random-forest")
MODEL_ALIAS = os.getenv("MODEL_ALIAS", "Challenger")          # overridden per pipeline
SERVE_PORT  = int(os.getenv("SERVE_PORT", "5001"))
SERVE_HOST  = os.getenv("SERVE_HOST", "127.0.0.1")


def wait_for_server(host, port, timeout=60):
    """Poll until the model server responds."""
    url = f"http://{host}:{port}/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print(f"[deploy] Server is up at {url}")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(2)
    return False


def deploy():
    model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    print(f"[deploy] Serving model: {model_uri} on port {SERVE_PORT}")

    cmd = [
        "mlflow", "models", "serve",
        "--model-uri", model_uri,
        "--host", SERVE_HOST,
        "--port", str(SERVE_PORT),
        "--no-conda",
    ]

    # Launch as background process and write PID for cleanup
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    with open("serve.pid", "w") as f:
        f.write(str(proc.pid))

    print(f"[deploy] Server PID {proc.pid} — waiting for readiness...")

    if wait_for_server(SERVE_HOST, SERVE_PORT):
        print(f"[deploy] Model server ready at http://{SERVE_HOST}:{SERVE_PORT}")
    else:
        print("[deploy] ERROR: Server did not start in time")
        proc.terminate()
        sys.exit(1)


def stop():
    """Gracefully stop model server (called at end of Jenkins stage)."""
    try:
        with open("serve.pid") as f:
            pid = int(f.read().strip())
        os.kill(pid, 15)  # SIGTERM
        print(f"[deploy] Stopped server PID {pid}")
    except FileNotFoundError:
        print("[deploy] No PID file found — server may already be stopped")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    if action == "stop":
        stop()
    else:
        deploy()
