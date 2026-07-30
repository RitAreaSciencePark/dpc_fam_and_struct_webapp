#!/usr/bin/env bash

set -Eeuo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

check_url() {
    local path="$1"
    echo "Checking ${path}"
    curl \
        --fail \
        --silent \
        --show-error \
        --output /dev/null \
        "${BASE_URL}${path}"
}

echo "Waiting for DPCexplorer at ${BASE_URL}..."

application_available=false

for attempt in $(seq 1 45); do
    if curl \
        --fail \
        --silent \
        --output /dev/null \
        "${BASE_URL}/health/live"
    then
        application_available=true
        break
    fi

    sleep 2
done

if [[ "${application_available}" != "true" ]]; then
    echo "Application did not become available."
    exit 1
fi

echo "Liveness check passed."

readiness_response="$(
    curl \
        --fail \
        --silent \
        --show-error \
        "${BASE_URL}/health/ready"
)"

python3 -c '
import json
import sys

response = json.load(sys.stdin)

assert response["status"] == "ready", response
assert all(response["checks"].values()), response

print("Readiness checks passed:", response["checks"])
' <<< "${readiness_response}"

check_url "/"
check_url "/dpcfam/"
check_url "/dpcfam/mcs/MC1/"
check_url "/dpcstruct/"
check_url "/dpcstruct/mcs/MC1/"
check_url "/admin/login/"

echo "Checking normal static assets."
curl \
    --fail \
    --silent \
    --show-error \
    --head \
    --output /dev/null \
    "${BASE_URL}/static/images/logo_dpcexplorer_web.png"

echo "Checking biological files."
curl \
    --fail \
    --silent \
    --show-error \
    --head \
    --output /dev/null \
    "${BASE_URL}/data/production_files/dpcfam/metaclusters_fasta/MC1.fasta"

curl \
    --fail \
    --silent \
    --show-error \
    --head \
    --output /dev/null \
    "${BASE_URL}/data/production_files/dpcstruct/dpcstruct_reps_pdbs/MC1_pdb/A0A7Y5H9I3_1.pdb"

echo "Checking path-traversal protection."

traversal_status="$(
    curl \
        --silent \
        --output /dev/null \
        --write-out "%{http_code}" \
        --path-as-is \
        "${BASE_URL}/data/../manage.py"
)"

if [[ "${traversal_status}" != "404" ]]; then
    echo "Expected traversal attempt to return 404; got ${traversal_status}."
    exit 1
fi

echo "Checking the production 404 page."

not_found_file="$(mktemp)"

not_found_status="$(
    curl \
        --silent \
        --output "${not_found_file}" \
        --write-out "%{http_code}" \
        "${BASE_URL}/this-page-does-not-exist"
)"

if [[ "${not_found_status}" != "404" ]]; then
    echo "Expected unknown page to return 404; got ${not_found_status}."
    rm -f "${not_found_file}"
    exit 1
fi

if grep -qE "Using the URLconf|DEBUG = True" "${not_found_file}"; then
    echo "The production 404 page exposed debug information."
    rm -f "${not_found_file}"
    exit 1
fi

rm -f "${not_found_file}"

echo "All HTTP smoke tests passed."
 
 