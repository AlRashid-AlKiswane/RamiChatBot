#!/bin/bash
set -e  # Exit on error

source ENV/bin/activate

# Start first FastAPI app
python -m src &
PID1=$!

# Start second FastAPI app
uvicorn src.main:app --host 0.0.0.0 --port 12000 &
PID2=$!

# Wait for both and trap exit signals
trap "kill $PID1 $PID2" SIGINT SIGTERM

wait $PID1
wait $PID2
