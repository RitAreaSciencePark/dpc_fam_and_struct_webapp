#!/usr/bin/env bash

set -Eeuo pipefail

cleanup() {
    local status=$?

    trap - EXIT

    if [[ "${status}" -ne 0 ]]; then
        echo "Container test failed. Recent logs:"
        docker compose logs --tail=200 web || true
    fi

    docker compose down || true
    exit "${status}"
}

trap cleanup EXIT

if [[ ! -f .env ]]; then
    echo ".env is missing."
    exit 1
fi

if [[ ! -d static/production_files ]]; then
    echo "static/production_files is missing."
    exit 1
fi

if [[ ! -d static/downloads ]]; then
    echo "static/downloads is missing."
    exit 1
fi

docker compose config --quiet
docker compose up --detach --build

container_id="$(docker compose ps --quiet web)"

if [[ -z "${container_id}" ]]; then
    echo "The web container was not created."
    exit 1
fi

echo "Waiting for Docker health status..."

container_healthy=false

for attempt in $(seq 1 45); do
    health_status="$(
        docker inspect \
            --format '{{.State.Health.Status}}' \
            "${container_id}" 2>/dev/null || true
    )"

    if [[ "${health_status}" == "healthy" ]]; then
        container_healthy=true
        break
    fi

    if [[ "${health_status}" == "unhealthy" ]]; then
        echo "Container became unhealthy."
        exit 1
    fi

    sleep 2
done

if [[ "${container_healthy}" != "true" ]]; then
    echo "Container did not become healthy."
    exit 1
fi

echo "Container health check passed."

container_uid="$(docker compose exec -T web id -u)"

if [[ "${container_uid}" != "10001" ]]; then
    echo "Expected UID 10001; got ${container_uid}."
    exit 1
fi

echo "Non-root user check passed."

docker compose exec -T web sh -c '
    if touch /app/should-not-work 2>/dev/null; then
        echo "/app is unexpectedly writable."
        exit 1
    fi

    touch /tmp/write-test
    rm /tmp/write-test
'

echo "Read-only root filesystem check passed."

docker compose exec -T web sh -c '
    test -r /data/production_files/dpcfam/metaclusters_fasta/MC1.fasta

    if touch /data/should-not-work 2>/dev/null; then
        echo "/data is unexpectedly writable."
        exit 1
    fi
'

echo "Read-only biological-data check passed."

BASE_URL="http://127.0.0.1:8000" ./scripts/smoke-test.sh

echo "All container checks passed."
