#!/bin/bash
set -e

# Colors
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${BLUE}🔧 Preparing the environment...${NC}"
echo -e "${YELLOW}🐍 Activating Python virtual environment...${NC}"
source ENV/bin/activate
echo -e "${GREEN}✅ Virtual environment activated!${NC}"

# Start App 1
echo -e "${YELLOW}🚀 Launching App 1: python -m src ...${NC}"
python -m src &
PID1=$!
echo -e "${GREEN}🎉 App 1 is up (PID: $PID1)!${NC}"

# Start App 2 (if it's a *different* app!)
echo -e "${YELLOW}🚀 Launching App 2: uvicorn src.other_main:app ...${NC}"
uvicorn src.main:app --host 0.0.0.0 --port 5500 
PID2=$!
echo -e "${GREEN}🎉 App 2 is up (PID: $PID2)!${NC}"

echo -e "${BLUE}✨ Both apps launched. Waiting for them to complete...${NC}" 
echo -e "${GREEN}🌟 All processes done. Goodbye! 👋${NC}"
wait
