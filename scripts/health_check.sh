#!/bin/bash

echo "===== 2-Tier Application Health Check ====="

check_service() {
    local service=$1

    if docker compose ps "$service" | grep -q "Up"; then
        echo "$service: RUNNING"
    else
        echo "$service: NOT RUNNING"
    fi
}

echo
echo "Host:"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo

echo "Disk Usage:"
df -h / | tail -n 1

echo
echo "Docker Services:"
check_service app
check_service db

echo
echo "Database:"
docker compose exec -T db pg_isready -U appuser -d appdb

echo
echo "Application:"
if curl -s http://localhost:5000/ | grep -q "Python + PostgreSQL application is running"; then
    echo "Flask: HEALTHY"
else
    echo "Flask: NOT HEALTHY"
fi

echo
echo "===== Health Check Complete ====="
