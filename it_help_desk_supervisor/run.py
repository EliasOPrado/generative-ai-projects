import subprocess
import time

# Start FastAPI
fastapi = subprocess.Popen(
    [
        "uvicorn",
        "main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8001",
        "--reload",
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

# Give FastAPI a moment to start
time.sleep(2)

# Start Streamlit
streamlit = subprocess.Popen(
    [
        "streamlit",
        "run",
        "frontend.py",
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

print("✅ FastAPI started")
print("✅ Streamlit started")

try:
    fastapi.wait()
    streamlit.wait()
except KeyboardInterrupt:
    print("Stopping applications...")

    fastapi.terminate()
    streamlit.terminate()