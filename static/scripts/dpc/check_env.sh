#!/bin/bash

# ==============================================================================
# Environment Properties Checker
# Description: This script gathers hardware and software specifications for 
#              reproducibility reporting in HPC environments.
# ==============================================================================

echo "========================================"
echo "      ENVIRONMENT PROPERTIES CHECK      "
echo "========================================"

echo -e "\n=== 1. CPU Architecture & Processor Info ==="
# lscpu provides detailed information about the CPU architecture, 
# vendor, model name, sockets, cores, and threads.
lscpu | grep -E "Architecture|Model name|CPU\(s\):|Thread\(s\) per core|Core\(s\) per socket|Socket\(s\)|CPU max MHz"

echo -e "\n=== 2. Allocated Job Cores (SLURM) ==="
# nproc returns the number of processing units available to the CURRENT process.
# In a SLURM job, this reflects the cores allocated, not the whole node.
echo "Usable CPUs (Allocated): $(nproc)"

echo -e "\n=== 3. Memory Information ==="
# free -h displays total, used, and free memory in human-readable format (GB/MB).
free -h

echo -e "\n=== 4. GPU Information ==="
# nvidia-smi checks for NVIDIA GPUs. We use 'command -v' to check if it exists 
# first, to avoid "command not found" errors on non-GPU nodes like 'epyc'.
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=gpu_name,memory.total --format=csv,noheader
else
    echo "No NVIDIA GPU detected (nvidia-smi command not found)."
fi

echo -e "\n=== 5. File System & Storage ==="
# df -h displays disk space usage. We aim it at the current directory ($PWD)
# to see the specific mount point (e.g., CephFS) handling our data.
df -h "$PWD"

echo -e "\n=== 6. Python Environment ==="
# Check the Python 3 version available in the current environment
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo "Python 3 is not installed or not in PATH."
fi

echo -e "\n========================================"
echo "             CHECK COMPLETE             "
echo "========================================"
