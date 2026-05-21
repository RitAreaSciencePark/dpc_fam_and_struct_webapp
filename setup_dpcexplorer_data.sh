#!/bin/bash

# ==============================================================================
# Script Name : setup_dpcexplorer_data.sh
# Description : Downloads, extracts, and organizes all datasets (FASTA, HMM,
#               MSA, PDB, CSV) from Zenodo so that DPCexplorer is ready to run.
#
# Usage       : bash setup_dpcexplorer_data.sh
# Note        : Run this from the root of the repository (where manage.py is).
#               If the script is interrupted, just run it again; it resumes.
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

# Prompt user to install missing system utilities automatically.
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

# ==============================================================================
# INSTALLATION MODALITY SELECTOR
# ==============================================================================
echo ""
echo "Select your dataset installation profiling:"
echo " 1) Full Installation (DPCfam, DPCstruct, and DPCexplorer CSVs) -> Requires ~100 GB space"
echo " 2) Lightweight Evaluation (DPCstruct and DPCexplorer CSVs Only) -> Requires ~15 GB space"
echo ""
read -p "Enter your choice (1 or 2): " REPO_INSTALL_PROFILE

# Default validation hooks
RUN_DPCFAM=true

if [ "$REPO_INSTALL_PROFILE" == "2" ]; then
    RUN_DPCFAM=false
    echo ""
    echo "⚠️  WARNING: You selected the Lightweight Mode!"
    echo "   - This option WILL NOT download any DPCfam biological files (FASTA, MSA, HMM)."
    echo "   - You won't be able to download DPCfam data through the web application."
    echo "   - DPCstruct (structure-based metaclusters) and PostgreSQL database tables will be fully active."
    echo ""
    read -p "Proceed with Lightweight Mode? (y/n): " CONFIRM_LIGHTWEIGHT
    if [[ "$CONFIRM_LIGHTWEIGHT" != "y" && "$CONFIRM_LIGHTWEIGHT" != "Y" ]]; then
        echo "Exiting setup script..."
        exit 0
    fi
fi

# ------------------------------------------------------------------------------
# Check for sufficient free disk space based on selection.
# ------------------------------------------------------------------------------
if [ "$RUN_DPCFAM" = true ]; then
    REQUIRED_DISK_GB=100
else
    REQUIRED_DISK_GB=15
fi

AVAILABLE_DISK_GB=$(df "$BASE_DIR" --output=avail -BG | tail -1 | tr -dc '0-9')

echo ""
echo "========================================================"
echo "              STORAGE REQUIREMENTS CHECK                "
echo "========================================================"
echo "Recommended free disk space for configuration : ${REQUIRED_DISK_GB} GB"
echo "Detected available workspace space             : ${AVAILABLE_DISK_GB} GB"
echo ""

if [ "$AVAILABLE_DISK_GB" -lt "$REQUIRED_DISK_GB" ]; then
    echo "WARNING: Low disk space detected!"
    echo "DPCexplorer might experience database generation or extraction errors."
    echo ""
else
    echo "Disk space check passed."
    echo ""
fi

# ------------------------------------------------------------------------------
# Helper function: download_file
# Downloads a file from a URL using wget with resume support (-c).
# Skips the download if the file already exists locally.
# ------------------------------------------------------------------------------
download_file() {
    local url=$1
    local output_file=$2
    if [ ! -f "$output_file" ]; then
        echo "Downloading $output_file ..."
        wget -c -O "$output_file" "$url"
    else
        echo "$output_file already exists. Skipping download."
    fi
}

# ==============================================================================
# I. DPCfam Data Processing Pipeline (Conditionally Executed)
# ==============================================================================
if [ "$RUN_DPCFAM" = true ]; then
    echo -e "\n--- I. Downloading and organizing DPCfam data ---"

    mkdir -p "$BASE_DIR/static/downloads/dpcfam/"
    cd "$BASE_DIR/static/downloads/dpcfam/"

    # Step 1.1: Download preprocessed seeds from the derivative repository (Zenodo 1)
    download_file "https://zenodo.org/records/20159208/files/dpcfam_mcid_seeds.tar.gz?download=1" "dpcfam_mcid_seeds.tar.gz"

    mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/"
    if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/" 2>/dev/null)" ]; then
        echo "Extracting seed FASTA files ..."
        tar -xzf dpcfam_mcid_seeds.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/"
    fi

    # Step 1.2: Download biological alignments/HMM profiles from original repository (Zenodo 2)
    download_file "https://zenodo.org/records/6900559/files/metaclusters_hmms.tar.gz?download=1" "standard_dpcfam_mcid_hmms.tar.gz"
    download_file "https://zenodo.org/records/6900559/files/B_metaclusters_hmms.tar.gz?download=1" "dpcfamB_mcid_hmms.tar.gz"

    mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/"
    if [ ! -f "dpcfam_mcid_hmms.tar.gz" ]; then
        echo "Extracting and merging single HMM files ..."
        mkdir -p hmms_temp
        tar -xzf standard_dpcfam_mcid_hmms.tar.gz -C hmms_temp/
        tar -xzf dpcfamB_mcid_hmms.tar.gz -C hmms_temp/
        find hmms_temp -type f -name "*.hmm" -exec mv {} "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/" \;
        rm -rf hmms_temp
        
        echo "Packaging consolidated individual HMMs archive for frontend downloads..."
        tar -czf dpcfam_mcid_hmms.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/" .
    fi

    # Step 1.3: Handle combined aggregate HMM model collections
    download_file "https://zenodo.org/records/6900559/files/all_metaclusters_hmm.tar.gz?download=1" "standard_dpcfam_all_metaclusters_hmms.tar.gz"
    download_file "https://zenodo.org/records/6900559/files/B_all_metaclusters_hmm.tar.gz?download=1" "dpcfamB_all_metaclusters_hmms.tar.gz"

    if [ ! -f "dpcfam_all_metaclusters_hmms.tar.gz" ]; then
        echo "Extracting and merging aggregate HMM catalog profiles ..."
        tar -xzf standard_dpcfam_all_metaclusters_hmms.tar.gz -C .
        tar -xzf dpcfamB_all_metaclusters_hmms.tar.gz -C .
        tar -czf dpcfam_all_metaclusters_hmms.tar.gz *.hmm
        rm -f *.hmm
    fi

    # Step 1.4: Download and extract raw Multiple Sequence Alignments (MSAs)
    download_file "https://zenodo.org/records/6900559/files/B_metaclusters_msas.tar.gz?download=1" "dpcfamB_mcid_msas.tar.gz"
    download_file "https://zenodo.org/records/6900559/files/metaclusters_msas.tar.gz?download=1" "standard_dpcfam_mcid_msas.tar.gz"

    mkdir -p "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/"
    if [ ! -f "dpcfam_mcid_msas.tar.gz" ]; then
        echo "Extracting, unzipping, and standardizing MSA files ..."
        mkdir -p dpcfam_mcid_msas_temp
        tar -xzf dpcfamB_mcid_msas.tar.gz -C dpcfam_mcid_msas_temp/
        tar -xzf standard_dpcfam_mcid_msas.tar.gz -C dpcfam_mcid_msas_temp/
        find dpcfam_mcid_msas_temp -type f -name "*.gz" -exec gunzip {} +
        
        find dpcfam_mcid_msas_temp -type f -name "*.msa" | while read -r msa_file; do
            new_name=$(echo "$msa_file" | sed 's/_cdhit\.fasta\.msa/_msa.fasta/')
            mv "$msa_file" "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/$(basename "$new_name")"
        done
        rm -rf dpcfam_mcid_msas_temp
        
        echo "Packaging unified MSA file collection archive for web downloads..."
        tar -czf dpcfam_mcid_msas.tar.gz -C "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/" .
    fi

    echo "Cleaning up intermediate DPCfam raw source archives..."
    rm -f "$BASE_DIR/static/downloads/dpcfam/dpcfamB_all_metaclusters_hmms.tar.gz" \
          "$BASE_DIR/static/downloads/dpcfam/dpcfamB_mcid_hmms.tar.gz" \
          "$BASE_DIR/static/downloads/dpcfam/dpcfamB_mcid_msas.tar.gz" \
          "$BASE_DIR/static/downloads/dpcfam/standard_dpcfam_all_metaclusters_hmms.tar.gz" \
          "$BASE_DIR/static/downloads/dpcfam/standard_dpcfam_mcid_hmms.tar.gz" \
          "$BASE_DIR/static/downloads/dpcfam/standard_dpcfam_mcid_msas.tar.gz"
else
    echo -e "\n--- I. Skipping DPCfam data deployment (Lightweight Option Active) ---"
fi

# ==============================================================================
# II. DPCstruct Data Processing Pipeline
# ==============================================================================
echo -e "\n--- II. Downloading and organizing DPCstruct data ---"

mkdir -p "$BASE_DIR/static/downloads/dpcstruct/"
cd "$BASE_DIR/static/downloads/dpcstruct/"

# Step 2.1: Fetch structural core seeds (Zenodo 1)
download_file "https://zenodo.org/records/20159208/files/dpcstruct_mcid_seeds.tar.gz?download=1" "dpcstruct_mcid_seeds.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/"
if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/" 2>/dev/null)" ]; then
    echo "Extracting DPCstruct representative sequence files ..."
    tar -xzf dpcstruct_mcid_seeds.tar.gz -C "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/"
fi

# Step 2.2: Download zipped PDB coordinates required for Mol* components
download_file "https://zenodo.org/records/20159208/files/dpcstruct_mcid_pdbs.tar.gz?download=1" "dpcstruct_mcid_pdbs.tar.gz"

mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/"
mkdir -p "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/"

if [ -z "$(ls -A "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/" 2>/dev/null)" ]; then
    echo "Extracting multi-subfolder PDB coordinates bundle ..."
    tar -xzf dpcstruct_mcid_pdbs.tar.gz -C "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/"

    echo "Decompressing internal zip partitions into production environment paths..."
    for zip_file in "$BASE_DIR"/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/*.zip; do
        if [ -f "$zip_file" ]; then
            unzip -q "$zip_file" -d "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/"
        fi
    done
fi

# ==============================================================================
# III. Database Tables Extraction Engine (CSV Schema)
# ==============================================================================
echo -e "\n--- III. Downloading and organizing CSV files for the database ---"

mkdir -p "$BASE_DIR/static/dataframes/"
cd "$BASE_DIR/static/dataframes/"

# Download core tables compilation archive (Zenodo 1)
download_file "https://zenodo.org/records/20159208/files/dpcexplorer_csv.tar.gz?download=1" "dpcexplorer_csv_files.tar.gz"

mkdir -p dpcexplorer_csv_files dpc dpcfam dpcstruct
if [ -z "$(ls -A "$BASE_DIR/static/dataframes/dpc/" 2>/dev/null)" ]; then
    echo "Extracting relational tables metadata structures ..."
    tar -xzf dpcexplorer_csv_files.tar.gz -C dpcexplorer_csv_files/
    tar -xzf dpcexplorer_csv_files/dpc_csv.tar.gz -C dpc/
    tar -xzf dpcexplorer_csv_files/dpcfam_csv.tar.gz -C dpcfam/
    tar -xzf dpcexplorer_csv_files/dpcstruct_csv.tar.gz -C dpcstruct/
    rm -rf dpcexplorer_csv_files/
fi

# Drop root payload package to optimize server storage
rm -f dpcexplorer_csv_files.tar.gz

# ==============================================================================
# DPCexplorer Tree Visualizer
# ==============================================================================
echo -e "\n========================================================"
echo "DPCexplorer Tree -- static/"
echo "========================================================"
echo ""
echo "Directory preview:"
if [ -d "$BASE_DIR/static/downloads/" ]; then tree "$BASE_DIR/static/downloads/" -L 2; fi
tree "$BASE_DIR/static/dataframes/" -L 2
tree -d "$BASE_DIR/static/production_files/" -L 2

# ==============================================================================
# IV. Comprehensive Integrity Verification Suite
# ==============================================================================
echo ""
echo "========================================================"
echo "           DPCEXPLORER DATA VALIDATION                  "
echo "========================================================"

VALIDATION_FAILED=0

validate_count() {
    local label="$1"
    local expected="$2"
    local actual="$3"

    if [ "$expected" -eq "$actual" ]; then
        printf " [OK]   %-55s Expected: %-10s Found: %-10s\n" "$label" "$expected" "$actual"
    else
        printf " [FAIL] %-55s Expected: %-10s Found: %-10s\n" "$label" "$expected" "$actual"
        VALIDATION_FAILED=1
    fi
}

echo ""
echo "Checking downloaded consolidated production archives ..."
echo "--------------------------------------------------------"

if [ "$RUN_DPCFAM" = true ]; then
    DPCFAM_DOWNLOADS_COUNT=$(find "$BASE_DIR/static/downloads/dpcfam/" -maxdepth 1 -type f | wc -l)
    validate_count "static/downloads/dpcfam/ consolidated files" 4 "$DPCFAM_DOWNLOADS_COUNT"
else
    echo " [SKIP] static/downloads/dpcfam/ files (Lightweight option active)"
fi

DPCSTRUCT_DOWNLOADS_COUNT=$(find "$BASE_DIR/static/downloads/dpcstruct/" -maxdepth 1 -type f | wc -l)
validate_count "static/downloads/dpcstruct/ archive files" 2 "$DPCSTRUCT_DOWNLOADS_COUNT"

echo ""
echo "Checking DPCfam parsed biological features components ..."
echo "--------------------------------------------------------"

if [ "$RUN_DPCFAM" = true ]; then
    DPCFAM_FASTA_COUNT=$(find "$BASE_DIR/static/production_files/dpcfam/metaclusters_fasta/" -type f | wc -l)
    DPCFAM_MSA_COUNT=$(find "$BASE_DIR/static/production_files/dpcfam/metaclusters_cdhit_msas/" -type f | wc -l)
    DPCFAM_HMM_COUNT=$(find "$BASE_DIR/static/production_files/dpcfam/metaclusters_hmms/" -type f | wc -l)

    validate_count "DPCfam FASTA files" 81384 "$DPCFAM_FASTA_COUNT"
    validate_count "DPCfam MSA files" 81384 "$DPCFAM_MSA_COUNT"
    validate_count "DPCfam HMM files" 81358 "$DPCFAM_HMM_COUNT"
else
    echo " [SKIP] DPCfam biological file validations (Lightweight mode active)"
fi

echo ""
echo "Checking DPCstruct localized structural coordinate data ..."
echo "--------------------------------------------------------"

DPCSTRUCT_ZIPPED_COUNT=$(find "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs_zipped/" -type f -name "*.zip" | wc -l)
DPCSTRUCT_FASTA_COUNT=$(find "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_seqs/" -type f | wc -l)
DPCSTRUCT_PDB_DIR_COUNT=$(find "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/" -mindepth 1 -maxdepth 1 -type d | wc -l)
DPCSTRUCT_PDB_FILE_COUNT=$(find "$BASE_DIR/static/production_files/dpcstruct/dpcstruct_reps_pdbs/" -type f -name "*.pdb" | wc -l)

validate_count "DPCstruct representative seed sequences" 28246 "$DPCSTRUCT_FASTA_COUNT"
validate_count "DPCstruct representative zipped PDB archives" 28246 "$DPCSTRUCT_ZIPPED_COUNT"
validate_count "DPCstruct representative per-MCID PDB directories" 28246 "$DPCSTRUCT_PDB_DIR_COUNT"
validate_count "DPCstruct representative PDB files" 56438 "$DPCSTRUCT_PDB_FILE_COUNT"

echo ""
echo "========================================================"

if [ "$VALIDATION_FAILED" -eq 0 ]; then
    echo " Congratulations! All selected DPCexplorer datasets were installed correctly."
    if [ "$RUN_DPCFAM" = false ]; then
        echo " NOTE: Running in Lightweight Mode. DPCfam biological files will not be available."
    fi
    echo ""
    echo " Your local workspace instance is ready to deploy."
else
    echo " WARNING: Dataset validation integrity faults found. Inspect log data."
fi
echo "========================================================"
echo ""