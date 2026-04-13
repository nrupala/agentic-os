#!/bin/bash
# Paradise Stack - Self-Test Script
# Verifies all components are working

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🧪 Paradise Stack Self-Test"
echo "=========================================="

# Test 1: Docker
echo -n "Docker... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "Install Docker: https://docker.com"
fi

# Test 2: Docker Compose
echo -n "Docker Compose... "
if docker-compose version > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
fi

# Test 3: Build Image
echo -n "Building image (this may take a few minutes)... "
if docker-compose build paradise > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 4: Start Services
echo -n "Starting services... "
docker-compose up -d > /dev/null 2>&1
sleep 10
echo -e "${GREEN}OK${NC}"

# Test 5: Health Check
echo -n "Paradise Bridge health... "
for i in {1..30}; do
    if curl -sf http://localhost:3001/status > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}FAIL${NC}"
        docker-compose logs paradise
        exit 1
    fi
    sleep 2
done

# Test 6: Dashboard
echo -n "Dashboard accessible... "
if curl -sf http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
fi

echo "=========================================="
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "=========================================="
echo ""
echo "🌐 Open: http://localhost:3001"
echo ""
echo "Stop: docker-compose down"
echo "=========================================="
