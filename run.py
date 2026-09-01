import subprocess
import sys
import time


print("======================================")
print("       RESQNET SYSTEM STARTING")
print("======================================")


# Start FastAPI backend
print("\n[1] Starting FastAPI backend...")

backend = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--reload"
    ]
)


time.sleep(2)


# Start simulator
print("[2] Starting sensor simulator...")

simulator = subprocess.Popen(
    [
        sys.executable,
        "simulator/simulator.py"
    ]
)


time.sleep(2)


# Start Streamlit dashboard
print("[3] Starting Streamlit dashboard...")

dashboard = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py"
    ]
)


print("\n======================================")
print("       RESQNET SYSTEM RUNNING")
print("======================================")

print("\nBackend   : http://127.0.0.1:8000")
print("Dashboard : http://localhost:8501")
print("\nPress CTRL+C to stop everything.")


try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping ResQNet...")

    backend.terminate()
    simulator.terminate()
    dashboard.terminate()

    print("ResQNet stopped.")