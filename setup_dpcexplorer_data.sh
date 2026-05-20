#!/bin/bash

# ==============================================================================
# Script Name : setup_dpcexplorer_data.sh
# Description : Downloads, extracts, and organizes all datasets (FASTA, HMM,
#               MSA, PDB, CSV) from Zenodo so that DPCexplorer is ready to run.
#
# Usage       : bash setup_dpcexplorer_data.sh
# Note        : Run this from the root of the repository (where manage.py is).
#               If the script is interrupted, just run it again, it resumes.
# ==============================================================================

# Stop immediately if any command fails.
set -e

echo "========================================"
echo "         DPC EXPLORER DATA SETUP        "
echo "========================================"
echo ""

# Make sure the script is running from the repository root.
BASE_DIR="$(pwd)"
if [ ! -f "manage.py" ]; then
    echo "Error: Please run this script from the root of the repository (where manage.py is located)."
    exit 1
fi

# ------------------------------------------------------------------------------
# Check that all required system tools are available.
# wget handles all downloads.
# tree is optional (only used for the final directory preview).
# ------------------------------------------------------------------------------
REQUIRED_COMMANDS=("wget" "tar" "unzip" "gunzip" "tree")
MISSING_COMMANDS=()

for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_COMMANDS+=("$cmd")
    fi
done

if [ ${#MISSING_COMMANDS[@]} -ne 0 ]; then
    echo "Warning: The following tools are missing: ${MISSING_COMMANDS[*]}"
    read -p "Would you like to install them automatically via apt? (y/n): " INSTALL_CHOICE
    if [[ "$INSTALL_CHOICE" == "y" || "$INSTALL_CHOICE" == "Y" ]]; then
        sudo apt-get update
        sudo apt-get install -y "${MISSING_COMMANDS[@]}"
    else
        echo "Error: Cannot proceed without the required tools. Please install them and try again."
        exit 1
    fi
else
    echo "All required tools are available."
fi

# ------------------------------------------------------------------------------
# Helper function: download_file
# Downloads a file from a URL using wget with resume support (-c).
# Skips the download if the file already exists locally.
# Arguments:
#   $1 - Download URL
#   $2 - Output filename
# ------------------------------------------------------------------------------
download_file() {
    local url=$1
    local output_file=$2
    if [ ! -f "$output_file" ]; then
        echo "Downloading $output_file ..."
        wget -c -O "$output_file" "$url"
    else
        echo "$output_file already exists. Skipping (delete it to force a fresh download)."
    fi
}

# ==============================================================================
# I. DPCfam Data
# ==============================================================================
echo -e "\n--- I. Downloading and organizing DPCfam data ---"

mkdir -p "$BASE_DIR/static/downloads/dpcfam/"
cd "$BASE_DIR/static/downloads/dpcfam/"

# --- I.1 Seed sequences (FASTA) ---
# One .fasta file per metacluster, covering both Standard and DPCfamB subsets.
# Source: our Zenodo preprocessed deposit.
download_file "https://zenodo.org/records/20159208/files/dpcfam_mcid_seeds.tar.gz?download=1" "dpcfam_mcid_seeds.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/"
if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/" 2>/dev/null)" ]; then
    echo "Extracting seed FASTA files ..."
    tar -xzf dpcfam_mcid_seeds.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/"
fi

# --- I.2 HMM profiles (per MCID) ---
# Downloaded separately for Standard DPCfam and DPCfamB from the original Zenodo record,
# then merged into a single archive for the application.
download_file "https://zenodo.org/records/6900559/files/metaclusters_hmms.tar.gz?download=1" "standard_dpcfam_mcid_hmms.tar.gz"
download_file "https://zenodo.org/records/6900559/files/B_metaclusters_hmms.tar.gz?download=1" "dpcfamB_mcid_hmms.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/"
if [ ! -f "dpcfam_mcid_hmms.tar.gz" ]; then
    echo "Extracting and merging HMM files ..."
    tar -xzf standard_dpcfam_mcid_hmms.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/"
    tar -xzf dpcfamB_mcid_hmms.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/"

    echo "Creating merged HMM archive: dpcfam_mcid_hmms.tar.gz ..."
    tar -czf dpcfam_mcid_hmms.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/" .
fi

# --- I.3 Aggregated HMM files (one file covering all metaclusters) ---
# The original Zenodo record provides two aggregate .hmm files: one for Standard,
# one for DPCfamB. We extract them and repack as a single archive.
download_file "https://zenodo.org/records/6900559/files/all_metaclusters_hmm.tar.gz?download=1" "standard_dpcfam_all_metaclusters_hmms.tar.gz"
download_file "https://zenodo.org/records/6900559/files/B_all_metaclusters_hmms.tar.gz?download=1" "dpcfamB_all_metaclusters_hmms.tar.gz"

if [ ! -f "dpcfam_all_metaclusters_hmms.tar.gz" ]; then
    echo "Extracting aggregate HMM files ..."
    tar -xzf standard_dpcfam_all_metaclusters_hmms.tar.gz -C .
    tar -xzf dpcfamB_all_metaclusters_hmms.tar.gz -C .

    echo "Packing both .hmm files into a single archive: dpcfam_all_metaclusters_hmms.tar.gz ..."
    tar -czf dpcfam_all_metaclusters_hmms.tar.gz *.hmm
    rm -f *.hmm
fi

# --- I.4 MSA files ---
# Raw MSA files from the original Zenodo record are gzip-compressed and have the
# naming pattern MCID_cdhit.fasta.msa. We decompress them and rename each one to
# MCID_msa.fasta for clarity before serving them from the application.
download_file "https://zenodo.org/records/6900559/files/B_metaclusters_msas.tar.gz?download=1" "dpcfamB_mcid_msas.tar.gz"
download_file "https://zenodo.org/records/6900559/files/metaclusters_msas.tar.gz?download=1" "standard_dpcfam_mcid_msas.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/"
if [ ! -f "dpcfam_mcid_msas.tar.gz" ]; then
    echo "Extracting MSA files ..."
    rm -rf dpcfam_mcid_msas_temp && mkdir dpcfam_mcid_msas_temp
    # DPCFamB file format: MCID_cdhit.fasta.msa
    tar -xzf dpcfamB_mcid_msas.tar.gz -C dpcfam_mcid_msas_temp/
    # Standard DPCFam file format: MCID_cdhit.fasta.msa.gz
    tar -xzf standard_dpcfam_mcid_msas.tar.gz -C dpcfam_mcid_msas_temp/
    echo "Decompressing inner .gz files ..."
    for gz_file in dpcfam_mcid_msas_temp/*.gz; do
        [ -f "$gz_file" ] && gunzip "$gz_file"
    done

    echo "Renaming MSA files: MCID_cdhit.fasta.msa -> MCID_msa.fasta ..."
    for msa_file in dpcfam_mcid_msas_temp/*.msa; do
        if [ -f "$msa_file" ]; then
            new_name=$(echo "$msa_file" | sed 's/_cdhit\.fasta\.msa/_msa.fasta/')
            mv "$msa_file" "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/$(basename "$new_name")"
        fi
    done

    rm -rf dpcfam_mcid_msas_temp

    echo "Creating consolidated MSA archive: dpcfam_mcid_msas.tar.gz ..."
    tar -czf dpcfam_mcid_msas.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/" .
fi

# ==============================================================================
# II. DPCstruct Data
# ==============================================================================
echo -e "\n--- II. Downloading and organizing DPCstruct data ---"

mkdir -p "$BASE_DIR/static/downloads/dpcstruct/"
cd "$BASE_DIR/static/downloads/dpcstruct/"

# --- II.1 Representative seed sequences (FASTA) ---
# One .fasta file per metacluster, containing the representative domain sequences.
download_file "https://zenodo.org/records/20159208/files/dpcstruct_mcid_seeds.tar.gz?download=1" "dpcstruct_mcid_seeds.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/"
if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/" 2>/dev/null)" ]; then
    echo "Extracting DPCstruct FASTA files ..."
    tar -xzf dpcstruct_mcid_seeds.tar.gz -C "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/"
fi

# --- II.2 Representative PDB structures ---
# The Zenodo deposit provides one MCID_pdb.zip per metacluster.
# We extract the outer archive to get the zip files (served as downloads),
# then unzip each one into MCID_pdb/ subfolders so the Mol* viewer can load
# individual .pdb files directly.
download_file "https://zenodo.org/records/20159208/files/dpcstruct_mcid_pdbs.tar.gz?download=1" "dpcstruct_mcid_pdbs.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/"
mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/"

if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/" 2>/dev/null)" ]; then
    echo "Extracting PDB zip archives ..."
    tar -xzf dpcstruct_mcid_pdbs.tar.gz -C "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/"

    echo "Unzipping individual PDB files for the Mol* viewer ..."
    for zip_file in "$BASE_DIR"/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/*.zip; do
        if [ -f "$zip_file" ]; then
            # Each zip becomes its own MCID_pdb/ subfolder under dpcstruct_reps_pdbs/
            dest_dir="$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/$(basename "$zip_file" .zip)_pdb/"
            mkdir -p "$dest_dir"
            unzip -q "$zip_file" -d "$dest_dir"
        fi
    done
fi

# ==============================================================================
# III. PostgreSQL-ready CSV files
# ==============================================================================
echo -e "\n--- III. Downloading and organizing CSV files for the database ---"

mkdir -p "$BASE_DIR/static/dataframes/"
cd "$BASE_DIR/static/dataframes/"

# The master archive contains three sub-archives, one per Django application.
download_file "https://zenodo.org/records/20159208/files/dpcexplorer_csv.tar.gz?download=1" "dpcexplorer_csv_files.tar.gz"

mkdir -p dpcexplorer_csv_files dpc dpcfam dpcstruct
if [ -z "$(ls -A "$BASE_DIR/static/dataframes/dpc/" 2>/dev/null)" ]; then
    echo "Extracting master CSV archive ..."
    tar -xzf dpcexplorer_csv_files.tar.gz -C dpcexplorer_csv_files/

    echo "Placing CSV files into their application directories ..."
    tar -xzf dpcexplorer_csv_files/dpc_csv.tar.gz -C dpc/
    tar -xzf dpcexplorer_csv_files/dpcfam_csv.tar.gz -C dpcfam/
    tar -xzf dpcexplorer_csv_files/dpcstruct_csv.tar.gz -C dpcstruct/

    rm -rf dpcexplorer_csv_files/
fi

# ==============================================================================
# Done!
# ==============================================================================
echo -e "\n========================================================"
echo "Setup complete. DPCexplorer data is ready."
echo "========================================================"
echo ""
echo "Directory preview:"
tree "$BASE_DIR/static/downloads/" -L 2
tree "$BASE_DIR/static/dataframes/" -L 2
tree "$BASE_DIR/static/production_files/" -L 1