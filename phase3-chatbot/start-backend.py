import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting backend server...")

    # Change to the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)

    # Install dependencies if needed
    try:
        import uvicorn
    except ImportError:
        print("Installing uvicorn...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn"])

    try:
        import fastapi
    except ImportError:
        print("Installing fastapi...")
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi"])

    # Start the server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]

    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    start_backend()