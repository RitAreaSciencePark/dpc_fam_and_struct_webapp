#!/usr/bin/env python3
"""
fetch_uniprot_complete.py
=========================
Retrieve protein sequence length and database source for all unique protein IDs
in dpcstruct_mcs_sequences.csv.

Method (two-phase approach):
  Phase 1 — Query UniProtKB (canonical): returns length + review status for
            all active entries (Swiss-Prot = reviewed, TrEMBL = unreviewed).
  Phase 2 — Query UniParc (archive): for IDs that returned no length in Phase 1
            (entries removed from UniProtKB but archived in UniParc).

Output columns:
  protein_id  — original accession
  length      — amino-acid sequence length
  source      — "UniProtKB/Swiss-Prot" | "UniProtKB/TrEMBL" | "UniParc" | "not_found"

Each batch is saved individually for resume support.
Re-running the script skips already-completed batches.

Usage:
    python3 fetch_uniprot_complete.py
"""

import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

# ─── Configuration ───────────────────────────────────────────────────
INPUT_CSV  = "/root/dpc_fam_and_struct_webapp/static/dataframes/dpcstruct/dpcstruct_mcs_sequences.csv"
BATCH_DIR  = Path("./batches")
FINAL_CSV  = "./dpcstruct_protein_info.csv"
BATCH_SIZE = 80_000
API        = "https://rest.uniprot.org"


# ─── Helpers ─────────────────────────────────────────────────────────
def submit_job(ids, db_from, db_to):
    """Submit an ID-mapping job and return the job ID."""
    r = requests.post(f"{API}/idmapping/run",
                      data={"from": db_from, "to": db_to, "ids": ",".join(ids)},
                      timeout=120)
    r.raise_for_status()
    return r.json()["jobId"]


def poll_job(job_id):
    """Wait until the job finishes."""
    while True:
        r = requests.get(f"{API}/idmapping/status/{job_id}", timeout=60)
        r.raise_for_status()
        if r.json().get("jobStatus") == "RUNNING":
            time.sleep(5)
            continue
        return


def download_tsv(job_id, endpoint, fields):
    """Download results as a DataFrame."""
    r = requests.get(f"{API}/idmapping/{endpoint}/results/stream/{job_id}",
                     params={"fields": fields, "format": "tsv"},
                     timeout=600)
    r.raise_for_status()
    txt = r.text.strip()
    if not txt:
        return pd.DataFrame()
    return pd.read_csv(StringIO(txt), sep="\t")


def run_batches(ids, phase_dir, db_from, db_to, endpoint, fields):
    """
    Process a list of IDs in batches.
    Returns a merged DataFrame of all batch results.
    """
    phase_dir.mkdir(parents=True, exist_ok=True)
    total = (len(ids) + BATCH_SIZE - 1) // BATCH_SIZE
    frames = []

    for i in range(0, len(ids), BATCH_SIZE):
        batch = ids[i : i + BATCH_SIZE]
        num = i // BATCH_SIZE + 1
        path = phase_dir / f"batch_{num:03d}.csv"

        # Resume: skip if already saved
        if path.exists() and path.stat().st_size > 0:
            print(f"  Batch {num}/{total} — cached, skipping", flush=True)
            frames.append(pd.read_csv(path))
            continue

        print(f"  Batch {num}/{total}  ({len(batch)} IDs) ... ", end="", flush=True)

        for attempt in range(1, 4):
            try:
                jid = submit_job(batch, db_from, db_to)
                poll_job(jid)
                df = download_tsv(jid, endpoint, fields)
                df.to_csv(path, index=False)
                frames.append(df)
                print(f"got {len(df)} rows", flush=True)
                break
            except Exception as e:
                print(f"\n    ✗ attempt {attempt}: {e}", flush=True)
                if attempt < 3:
                    time.sleep(30 * attempt)
                else:
                    print(f"    SKIPPED batch {num}", flush=True)
        time.sleep(1)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ─── Main ────────────────────────────────────────────────────────────
print(f"Reading {INPUT_CSV} ...", flush=True)
unique_ids = pd.read_csv(INPUT_CSV, usecols=["protein_id"])["protein_id"].unique().tolist()
print(f"Unique protein IDs: {len(unique_ids)}\n", flush=True)
t0 = time.time()

# ── Phase 1: UniProtKB ──────────────────────────────────────────────
print("═" * 60, flush=True)
print("PHASE 1 — UniProtKB  (active entries: length + review status)", flush=True)
print("═" * 60, flush=True)

df_kb = run_batches(
    unique_ids,
    phase_dir=BATCH_DIR / "uniprotkb",
    db_from="UniProtKB_AC-ID",
    db_to="UniProtKB",
    endpoint="uniprotkb",
    fields="accession,length,reviewed",
)

# Normalise columns
if not df_kb.empty:
    df_kb.rename(columns={"Entry": "protein_id", "Length": "length", "Reviewed": "reviewed"}, inplace=True)
    # Drop the "From" column if present (some API versions include it)
    df_kb = df_kb.drop(columns=[c for c in df_kb.columns if c not in ("protein_id", "length", "reviewed")], errors="ignore")
    review_map = {"reviewed": "UniProtKB/Swiss-Prot", "unreviewed": "UniProtKB/TrEMBL",
                  "true": "UniProtKB/Swiss-Prot", "false": "UniProtKB/TrEMBL",
                  True: "UniProtKB/Swiss-Prot", False: "UniProtKB/TrEMBL"}
    df_kb["source"] = df_kb["reviewed"].map(review_map)
    df_kb.drop(columns=["reviewed"], inplace=True)
    df_kb.drop_duplicates(subset="protein_id", keep="first", inplace=True)

has_length = df_kb["length"].notna() if not df_kb.empty else pd.Series(dtype=bool)
kb_ok = set(df_kb.loc[has_length, "protein_id"]) if not df_kb.empty else set()
print(f"\nPhase 1 result: {len(kb_ok)} IDs with length out of {len(unique_ids)}", flush=True)

# ── Phase 2: UniParc (fallback for missing IDs) ─────────────────────
missing_ids = [uid for uid in unique_ids if uid not in kb_ok]

print(f"\n{'═' * 60}", flush=True)
print(f"PHASE 2 — UniParc  (archived entries for {len(missing_ids)} IDs without length)", flush=True)
print("═" * 60, flush=True)

if missing_ids:
    df_parc = run_batches(
        missing_ids,
        phase_dir=BATCH_DIR / "uniparc",
        db_from="UniProtKB_AC-ID",
        db_to="UniParc",
        endpoint="uniparc",
        fields="upi,accession,length",
    )

    if not df_parc.empty:
        # UniParc results: "From" = our query ID, "Entry" = UPI, "Length" = seq length
        parc_cols = {"From": "protein_id", "Length": "length"}
        df_parc.rename(columns={k: v for k, v in parc_cols.items() if k in df_parc.columns}, inplace=True)
        if "protein_id" in df_parc.columns and "length" in df_parc.columns:
            df_parc = df_parc[["protein_id", "length"]].copy()
            df_parc["source"] = "UniParc"
            df_parc.drop_duplicates(subset="protein_id", keep="first", inplace=True)
            parc_ok = set(df_parc["protein_id"])
            print(f"\nPhase 2 result: {len(parc_ok)} IDs recovered from UniParc", flush=True)
        else:
            print(f"\nPhase 2: unexpected columns {list(df_parc.columns)}", flush=True)
            df_parc = pd.DataFrame()
    else:
        print("\nPhase 2: no results from UniParc", flush=True)
else:
    df_parc = pd.DataFrame()
    print("No missing IDs — Phase 2 skipped", flush=True)

# ── Merge both phases ───────────────────────────────────────────────
print(f"\n{'═' * 60}", flush=True)
print("MERGING RESULTS", flush=True)
print("═" * 60, flush=True)

# Start with UniProtKB results that have length
parts = []
if not df_kb.empty:
    parts.append(df_kb[df_kb["length"].notna()][["protein_id", "length", "source"]])
if not df_parc.empty:
    parts.append(df_parc[["protein_id", "length", "source"]])

if parts:
    df_final = pd.concat(parts, ignore_index=True)
    df_final.drop_duplicates(subset="protein_id", keep="first", inplace=True)
else:
    df_final = pd.DataFrame(columns=["protein_id", "length", "source"])

# Add rows for IDs not found anywhere (so we have a complete record)
found_ids = set(df_final["protein_id"])
nowhere = [uid for uid in unique_ids if uid not in found_ids]
if nowhere:
    df_nowhere = pd.DataFrame({
        "protein_id": nowhere,
        "length": pd.NA,
        "source": "not_found",
    })
    df_final = pd.concat([df_final, df_nowhere], ignore_index=True)

df_final["length"] = pd.to_numeric(df_final["length"], errors="coerce").astype("Int64")
df_final.reset_index(drop=True, inplace=True)

# ── Summary ──────────────────────────────────────────────────────────
elapsed = (time.time() - t0) / 60
print(f"\nTotal IDs queried:  {len(unique_ids)}", flush=True)
print(f"  Swiss-Prot:       {(df_final['source'] == 'UniProtKB/Swiss-Prot').sum()}", flush=True)
print(f"  TrEMBL:           {(df_final['source'] == 'UniProtKB/TrEMBL').sum()}", flush=True)
print(f"  UniParc:          {(df_final['source'] == 'UniParc').sum()}", flush=True)
print(f"  Not found:        {(df_final['source'] == 'not_found').sum()}", flush=True)
print(f"  With length:      {df_final['length'].notna().sum()}", flush=True)
print(f"  Missing length:   {df_final['length'].isna().sum()}", flush=True)
print(f"  Time elapsed:     {elapsed:.1f} min", flush=True)

# ── Save ─────────────────────────────────────────────────────────────
df_final.to_csv(FINAL_CSV, index=False)
print(f"\nSaved ({df_final.shape}) → {FINAL_CSV}", flush=True)
print("Done!", flush=True)
