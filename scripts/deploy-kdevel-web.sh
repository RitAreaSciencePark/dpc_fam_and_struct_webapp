#!/usr/bin/env bash

set -Eeuo pipefail

readonly namespace="dpcdom"
readonly deployment="dpcexplorer-web"
readonly container="web"
readonly image_repository="ghcr.io/ritareasciencepark/dpc_fam_and_struct_webapp"
readonly rollout_timeout="${ROLLOUT_TIMEOUT:-10m}"

readonly script_directory="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
  pwd
)"
readonly repository_root="$(cd -- "${script_directory}/.." && pwd)"
readonly kustomization="${repository_root}/k8s/overlays/kdevel/kustomization.yaml"

usage() {
  echo "Usage: $0 --dry-run|--apply" >&2
}

if [[ "$#" -ne 1 ]]; then
  usage
  exit 2
fi

readonly mode="$1"

if [[ "${mode}" != "--dry-run" && "${mode}" != "--apply" ]]; then
  usage
  exit 2
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required." >&2
  exit 1
fi

if [[ ! -f "${kustomization}" ]]; then
  echo "Kustomization not found: ${kustomization}" >&2
  exit 1
fi

readonly expected_context="${EXPECTED_KUBE_CONTEXT:-}"

if [[ -z "${expected_context}" ]]; then
  echo "EXPECTED_KUBE_CONTEXT must be set explicitly." >&2
  exit 1
fi

readonly current_context="$(kubectl config current-context)"

if [[ "${current_context}" != "${expected_context}" ]]; then
  echo "Refusing to continue in Kubernetes context '${current_context}'." >&2
  echo "Expected context: '${expected_context}'." >&2
  exit 1
fi

readonly pinned_digest="$(
  awk -v image="${image_repository}" '
    $1 == "-" && $2 == "name:" {
      selected = ($3 == image)
      next
    }

    selected && $1 == "digest:" {
      print $2
      exit
    }
  ' "${kustomization}"
)"

if [[ ! "${pinned_digest}" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  echo "The kdevel web-image digest is missing or invalid." >&2
  exit 1
fi

require_permission() {
  local verb="$1"
  local resource="$2"

  if [[ "$(
    kubectl auth can-i "${verb}" "${resource}" --namespace "${namespace}"
  )" != "yes" ]]; then
    echo "Kubernetes identity cannot ${verb} ${resource} in ${namespace}." >&2
    exit 1
  fi
}

require_permission get deployments.apps
require_permission patch deployments.apps

if [[ "${mode}" == "--apply" ]]; then
  require_permission watch deployments.apps
fi

get_live_image() {
  kubectl get deployment "${deployment}" \
    --namespace "${namespace}" \
    --output 'jsonpath={.spec.template.spec.containers[?(@.name=="web")].image}'
}

readonly current_image="$(get_live_image)"

if [[ -z "${current_image}" ]]; then
  echo "Container '${container}' was not found in Deployment '${deployment}'." >&2
  exit 1
fi

readonly candidate_image="${image_repository}@${pinned_digest}"

echo "Context:         ${current_context}"
echo "Namespace:       ${namespace}"
echo "Deployment:      ${deployment}"
echo "Current image:   ${current_image}"
echo "Reviewed image:  ${candidate_image}"
echo
echo "Performing Kubernetes server-side dry run..."

kubectl set image \
  "deployment/${deployment}" \
  "${container}=${candidate_image}" \
  --namespace "${namespace}" \
  --dry-run=server \
  --output=name

if [[ "$(get_live_image)" != "${current_image}" ]]; then
  echo "ERROR: the live Deployment changed during dry-run validation." >&2
  exit 1
fi

echo "Server-side dry run passed."

if [[ "${mode}" == "--dry-run" ]]; then
  echo "The live Deployment was not changed."
  exit 0
fi

if [[ "${candidate_image}" == "${current_image}" ]]; then
  echo "The reviewed image is already deployed."
  kubectl rollout status "deployment/${deployment}" \
    --namespace "${namespace}" \
    --timeout "${rollout_timeout}"
  exit 0
fi

rollback() {
  echo "Rolling back to ${current_image}..." >&2

  kubectl set image \
    "deployment/${deployment}" \
    "${container}=${current_image}" \
    --namespace "${namespace}"

  kubectl rollout status "deployment/${deployment}" \
    --namespace "${namespace}" \
    --timeout "${rollout_timeout}"
}

echo "Applying the reviewed image..."

kubectl set image \
  "deployment/${deployment}" \
  "${container}=${candidate_image}" \
  --namespace "${namespace}"

if ! kubectl rollout status "deployment/${deployment}" \
  --namespace "${namespace}" \
  --timeout "${rollout_timeout}"; then
  echo "The new rollout failed." >&2
  rollback || true
  exit 1
fi

readonly deployed_image="$(get_live_image)"

if [[ "${deployed_image}" != "${candidate_image}" ]]; then
  echo "The live image does not match the reviewed image." >&2
  rollback || true
  exit 1
fi

echo "Kdevel web deployment completed successfully."
echo "Deployed image: ${deployed_image}"
