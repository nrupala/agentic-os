#!/bin/bash
# OMEGA-CODE Health Check
# Verifies service responsiveness and memory pressure
# Usage: docker run --health-cmd="/app/docker/healthcheck.sh" ...

STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
MEM_USAGE=$(free 2>/dev/null | grep Mem | awk '{print $3/$2 * 100.0}' || echo "0")

if [ "$STATUS_CODE" -eq 200 ] && [ $(echo "$MEM_USAGE < 90" | bc -l 2>/dev/null || echo "1") -ne 0 ]; then
    echo "[OK] Service responsive. Memory: ${MEM_USAGE}%"
    exit 0
else
    echo "[CRITICAL] Status: $STATUS_CODE | Mem: ${MEM_USAGE}%"
    exit 1
fi
