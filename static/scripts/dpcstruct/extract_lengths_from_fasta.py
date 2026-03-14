#!/usr/bin/env python3
"""
Extract protein sequence lengths from local UniProtKB FASTA files
for protein IDs listed in dpcstruct_protein_df2_remaining.csv.

Usage:
    python3 extract_lengths_from_fasta.py
"""

import gzip
import time
from pathlib import Path

import pandas as pd

# ─── Configuration ───────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "dpcstruct_protein_df2_remaining.csv"
FINAL_CSV = BASE_DIR / "dpcstruct_protein_lengths.csv"

FASTA_FILES = [
    BASE_DIR / "uniprot_sprot.fasta.gz",
    BASE_DIR / "uniprot_trembl.fasta.gz",
]


# ─── Helpers ─────────────────────────────────────────────────────────
def stream_fasta_lengths(fasta_path: Path, needed_ids: set) -> dict:
    """
    Stream a gzipped UniProtKB FASTA file and return {accession: length}
    for accessions found in needed_ids.
    """
    lengths = {}
    if not fasta_path.exists():
        print(f"  WARNING: {fasta_path} not found, skipping")
        return lengths

    current_acc = None
    current_len = 0
    matched = False
    found_count = 0
    entry_count = 0

    print(f"  Streaming {fasta_path.name} ...")
    t0 = time.time()

    with gzip.open(fasta_path, "rt", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(">"):
                # Save previous entry if it matched
                if matched and current_acc is not None:
                    lengths[current_acc] = current_len
                    found_count += 1

                entry_count += 1
                if entry_count % 5_000_000 == 0:
                    elapsed = time.time() - t0
                    print(f"    ... {entry_count:,} entries, "
                          f"{found_count:,} matches ({elapsed:.0f}s)")

                # Parse header: >db|ACCESSION|entry_name ...
                parts = line[1:].split("|", 2)
                if len(parts) >= 2:
                    current_acc = parts[1].strip()
                else:
                    current_acc = line[1:].split()[0].strip()

                matched = current_acc in needed_ids
                current_len = 0

                # Early exit if we found everything
                if found_count == len(needed_ids):
                    break
            elif matched:
                current_len += len(line.strip())

    # Don't forget the last entry
    if matched and current_acc is not None and current_acc not in lengths:
        lengths[current_acc] = current_len
        found_count += 1

    elapsed = time.time() - t0
    print(f"    Done: {entry_count:,} entries, "
          f"{found_count:,} matches ({elapsed:.0f}s)")
    return lengths


# ─── Main ────────────────────────────────────────────────────────────
def main():
    print(f"Loading protein IDs from {INPUT_CSV} ...")
    all_ids = set(pd.read_csv(INPUT_CSV, usecols=["protein_id"])["protein_id"])
    print(f"  Total IDs: {len(all_ids):,}\n")

    remaining = set(all_ids)
    fasta_lengths = {}

    for fasta_path in FASTA_FILES:
        if not remaining:
            print("  All IDs found — skipping remaining files")
            break

        found = stream_fasta_lengths(fasta_path, remaining)
        fasta_lengths.update(found)
        remaining -= set(found.keys())
        print(f"  Found so far: {len(fasta_lengths):,}, "
              f"still missing: {len(remaining):,}\n")

    # Build output
    records = [{"protein_id": pid, "length": fasta_lengths.get(pid)}
               for pid in sorted(all_ids)]
    df_final = pd.DataFrame(records)
    df_final["length"] = df_final["length"].astype("Int64")

    has_length = df_final["length"].notna().sum()
    missing = df_final["length"].isna().sum()
    print(f"  Total IDs:      {len(df_final):,}")
    print(f"  With length:    {has_length:,}")
    print(f"  Missing length: {missing:,}")

    df_final.to_csv(FINAL_CSV, index=False)
    print(f"\nSaved → {FINAL_CSV}")


if __name__ == "__main__":
    main()
