#!/usr/bin/env bash

set -Eeuo pipefail

container_name="dpcfam-moved-page-test"
image_name="dpcfam-moved-page:ci"
base_url="http://127.0.0.1:18080"

cleanup() {
    local exit_status=$?

    trap - EXIT

    if docker container inspect "${container_name}" >/dev/null 2>&1; then
        if [[ "${exit_status}" -ne 0 ]]; then
            echo "Legacy-page container test failed. Recent logs:"
            docker logs "${container_name}" || true
        fi

        docker rm --force "${container_name}" >/dev/null || true
    fi

    exit "${exit_status}"
}

trap cleanup EXIT

docker build \
    --file Dockerfile.legacy-page \
    --tag "${image_name}" \
    .

docker run \
    --detach \
    --rm \
    --name "${container_name}" \
    --publish 127.0.0.1:18080:8080 \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=16m \
    --user 101:101 \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    "${image_name}"

echo "Waiting for container health status..."

container_healthy=false

for attempt in $(seq 1 30); do
    health_status="$(
        docker inspect \
            --format '{{.State.Health.Status}}' \
            "${container_name}" 2>/dev/null || true
    )"

    if [[ "${health_status}" == "healthy" ]]; then
        container_healthy=true
        break
    fi

    if [[ "${health_status}" == "unhealthy" ]]; then
        break
    fi

    sleep 1
done

if [[ "${container_healthy}" != "true" ]]; then
    echo "Container did not become healthy."
    exit 1
fi

echo "Container health check passed."

test "$(docker exec "${container_name}" id -u)" = "101"

docker exec "${container_name}" sh -c '
    if touch /usr/share/nginx/html/should-not-work 2>/dev/null; then
        echo "The document root is unexpectedly writable."
        exit 1
    fi

    touch /tmp/write-test
    rm /tmp/write-test
'

echo "Container security checks passed."

for test_path in \
    / \
    /uhgp \
    /some/old/dpcfam/path
do
    curl \
        --fail \
        --silent \
        --show-error \
        "${base_url}${test_path}" |
    grep -F "DPCfam has moved" >/dev/null

    echo "PASS: ${test_path}"
done

for image in \
    logo_dpcexplorer_web.png \
    logo_area_science_park.png \
    logo_sissa.png
do
    curl \
        --fail \
        --silent \
        --show-error \
        --output /dev/null \
        "${base_url}/static/images/${image}"

    echo "PASS: ${image}"
done

curl \
    --fail \
    --silent \
    --show-error \
    "${base_url}/" |
grep -F 'href="https://dpcexplorer.areasciencepark.it/"' >/dev/null

curl \
    --fail \
    --silent \
    --show-error \
    --head \
    "${base_url}/" |
grep -qi '^Content-Security-Policy:' >/dev/null

echo "Legacy DPCfam page checks passed."
