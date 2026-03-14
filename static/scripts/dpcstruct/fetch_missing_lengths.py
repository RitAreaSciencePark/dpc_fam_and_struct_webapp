#!/usr/bin/env python3
"""
Fetch lengths for protein IDs that were NOT found in the local FASTA files.

Reads dpcstruct_protein_lengths.csv (output of extract_lengths_from_fasta.py),
identifies rows with missing lengths, queries the UniProt REST API in two phases:
  Phase 1 — UniProtKB (active entries)
  Phase 2 — UniParc  (archived/deleted entries)

Then merges everything back into a single output CSV.

Re-running is safe: already-completed batches are skipped (resume support).

Usage:
    python3 fetch_missing_lengths.py
"""

import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

# ─── Configuration ───────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
FASTA_CSV   = BASE_DIR / "dpcstruct_protein_lengths.csv"
BATCH_DIR   = BASE_DIR / "api_batches"
FINAL_CSV   = BASE_DIR / "dpcstruct_protein_lengths_complete.csv"

BATCH_SIZE  = 80_000
API         = "https://rest.uniprot.org"
MAX_RETRIES = 3


# ─── API helpers ─────────────────────────────────────────────────────
def submit_job(ids: list, db_from: str, db_to: str) -> str:
    r = requests.post(
        f"{API}/idmapping/run",
        data={"from": db_from, "to": db_to, "ids": ",".join(ids)},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["jobId"]


def poll_job(job_id: str):
    while True:
        r = requests.get(f"{API}/idmapping/status/{job_id}", timeout=60)
        r.raise_for_status()
        if r.json().get("jobStatus") == "RUNNING":
            time.sleep(5)
            continue
        return


def download_tsv(job_id: str, endpoint: str, fields: str) -> pd.DataFrame:
    r = requests.get(
        f"{API}/idmapping/{endpoint}/results/stream/{job_id}",
        params={"fields": fields, "format": "tsv"},
        timeout=600,
    )
    r.raise_for_status()
    txt = r.text.strip()
    if not txt:
        return pd.DataFrame()
    return pd.read_csv(StringIO(txt), sep="\t")


def run_batches(ids: list, phase_dir: Path, db_from: str, db_to: str,
                endpoint: str, fields: str) -> pd.DataFrame:
    phase_dir.mkdir(parents=True, exist_ok=True)
    total = (len(ids) + BATCH_SIZE - 1) // BATCH_SIZE
    frames = []

    for i in range(0, len(ids), BATCH_SIZE):
        batch = ids[i : i + BATCH_SIZE]
        num = i // BATCH_SIZE + 1
        path = phase_dir / f"batch_{num:03d}.csv"

        if path.exists() and path.stat().st_size > 0:
            print(f"  Batch {num}/{total} — cached, skipping", flush=True)
            frames.append(pd.read_csv(path))
            continue

        print(f"  Batch {num}/{total}  ({len(batch):,} IDs) ... ",
              end="", flush=True)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                jid = submit_job(batch, db_from, db_to)
                poll_job(jid)
                df = download_tsv(jid, endpoint, fields)
                df.to_csv(path, index=False)
                frames.append(df)
                print(f"got {len(df):,} rows", flush=True)
                break
            except Exception as e:
                print(f"\n    attempt {attempt}: {e}", flush=True)
                if attempt < MAX_RETRIES:
                    time.sleep(30 * attempt)
                else:
                    print(f"    SKIPPED batch {num}", flush=True)
        time.sleep(1)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ─── Main ────────────────────────────────────────────────────────────
def main():
    # Load FASTA results and find missing IDs
    print(f"Loading {FASTA_CSV} ...")
    df_fasta = pd.read_csv(FASTA_CSV)
    missing_mask = df_fasta["length"].isna()
    missing_ids = df_fasta.loc[missing_mask, "protein_id"].tolist()
    print(f"  Total IDs: {len(df_fasta):,}")
    print(f"  Already have length: {(~missing_mask).sum():,}")
    print(f"  Missing (to fetch): {len(missing_ids):,}\n")

    if not missing_ids:
        print("Nothing to fetch — all lengths are present.")
        return

    t0 = time.time()

    # ── Phase 1: UniProtKB ───────────────────────────────────────────
    print("=" * 60)
    print(f"PHASE 1 — UniProtKB  ({len(missing_ids):,} IDs)")
    print("=" * 60, flush=True)

    df_kb = run_batches(
        missing_ids,
        phase_dir=BATCH_DIR / "uniprotkb",
        db_from="UniProtKB_AC-ID",
        db_to="UniProtKB",
        endpoint="uniprotkb",
        fields="accession,length",
    )

    kb_lengths = {}
    if not df_kb.empty:
        # Use 'From' (our queried accession), not 'Entry' (canonical accession)
        if "From" in df_kb.columns:
            df_kb.rename(columns={"From": "protein_id", "Length": "length"},
                         inplace=True)
        else:
            df_kb.rename(columns={"Entry": "protein_id", "Length": "length"},
                         inplace=True)
        df_kb = df_kb[["protein_id", "length"]].drop_duplicates(
            subset="protein_id", keep="first")
        # Only keep rows that actually have a length value
        df_kb_with_len = df_kb[df_kb["length"].notna()]
        kb_lengths = dict(zip(df_kb_with_len["protein_id"],
                              df_kb_with_len["length"]))

    print(f"\nPhase 1 result: {len(kb_lengths):,} IDs with length\n")

    # ── Phase 2: UniParc (for IDs still without length) ──────────────
    still_missing = [pid for pid in missing_ids if pid not in kb_lengths]

    print("=" * 60)
    print(f"PHASE 2 — UniParc  ({len(still_missing):,} archived/deleted IDs)")
    print("=" * 60, flush=True)

    parc_lengths = {}
    if still_missing:
        df_parc = run_batches(
            still_missing,
            phase_dir=BATCH_DIR / "uniparc",
            db_from="UniProtKB_AC-ID",
            db_to="UniParc",
            endpoint="uniparc",
            fields="upi,accession,length",
        )

        if not df_parc.empty:
            rename_map = {}
            if "From" in df_parc.columns:
                rename_map["From"] = "protein_id"
            if "Length" in df_parc.columns:
                rename_map["Length"] = "length"
            df_parc.rename(columns=rename_map, inplace=True)

            if "protein_id" in df_parc.columns and "length" in df_parc.columns:
                df_parc = df_parc[["protein_id", "length"]].drop_duplicates(
                    subset="protein_id", keep="first")
                parc_lengths = dict(zip(df_parc["protein_id"], df_parc["length"]))

        print(f"\nPhase 2 result: {len(parc_lengths):,} IDs recovered from UniParc\n")
    else:
        print("No missing IDs — Phase 2 skipped\n")

    # ── Merge back into the FASTA DataFrame ──────────────────────────
    print("=" * 60)
    print("MERGING RESULTS")
    print("=" * 60)

    api_lengths = {**kb_lengths, **parc_lengths}

    # Fill missing lengths in the original DataFrame
    df_fasta["length"] = df_fasta.apply(
        lambda row: api_lengths.get(row["protein_id"], row["length"])
        if pd.isna(row["length"]) else row["length"],
        axis=1,
    )
    df_fasta["length"] = pd.to_numeric(
        df_fasta["length"], errors="coerce").astype("Int64")

    has_length = df_fasta["length"].notna().sum()
    still_na = df_fasta["length"].isna().sum()
    elapsed = (time.time() - t0) / 60

    print(f"\n  Total IDs:        {len(df_fasta):,}")
    print(f"  With length:      {has_length:,}")
    print(f"  Still missing:    {still_na:,}")
    print(f"  From UniProtKB:   {len(kb_lengths):,}")
    print(f"  From UniParc:     {len(parc_lengths):,}")
    print(f"  Time elapsed:     {elapsed:.1f} min")

    df_fasta.to_csv(FINAL_CSV, index=False)
    print(f"\nSaved → {FINAL_CSV}")


if __name__ == "__main__":
    main()
