"""
This script runs the FastAPI application using Uvicorn on host 0.0.0.0 and port 5000.
It is designed to start the server with auto-reload during development.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
