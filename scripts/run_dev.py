import subprocess
import sys
import time

def run():
    print("Starting CISA Development Servers...")
    
    # Start Backend
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    time.sleep(2)  # Give backend a moment to start
    
    # Start Frontend
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

if __name__ == "__main__":
    run()
