#!/usr/bin/env bash

set -Eeuo pipefail

readonly DATA_ROOT="/data"
readonly READY_MARKER="${DATA_ROOT}/.dpcexplorer-data-ready"
readonly SETUP_LOG="/tmp/dpcexplorer-data-setup.log"

check_required_files() {
    test -s \
        "${DATA_ROOT}/production_files/dpcfam/metaclusters_fasta/MC1.fasta"

    test -s \
        "${DATA_ROOT}/production_files/dpcstruct/dpcstruct_reps_pdbs/MC1_pdb/A0A7Y5H9I3_1.pdb"

    test -d "${DATA_ROOT}/downloads/dpcfam"
    test -d "${DATA_ROOT}/downloads/dpcstruct"
}

if [[ -f "${READY_MARKER}" ]]; then
    check_required_files
    echo "The biological-data volume is already populated."
    exit 0
fi

cd /loader

# Select option 1: complete DPCfam and DPCstruct installation.
printf '1\n' |
    bash ./setup_dpcexplorer_data.sh |
    tee "${SETUP_LOG}"

grep --fixed-strings --quiet \
    "Congratulations! All selected DPCexplorer datasets were installed correctly." \
    "${SETUP_LOG}"

check_required_files

touch "${READY_MARKER}"

echo "The biological-data volume was populated successfully."
