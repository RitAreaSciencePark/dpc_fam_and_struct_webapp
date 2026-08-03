#!/usr/bin/env python3
"""
example_api_client.py
======================
A minimal example client for the DPCexplorer REST API.

Given one MCID, or a comma-separated list of MCIDs, from either DPCfam or
DPCstruct, this script:

  1. Fetches the properties of every requested MCID (one API call).
  2. Fetches ALL members of the first MCID in the list, following every
     paginated "next" link until the whole member list has been collected.

This mirrors the example notebook (static/scripts/api_examples/
example_api_client_notebook.ipynb): properties for the whole batch,
full member list for the first metacluster only. Fetching every member
of every requested MCID in one run is intentionally left out here, since
some DPCfam metaclusters hold 130,000+ members; call the script again with
a single MCID (--mcids MC<id>) whenever you need another one's full list.

Usage
-----
    python3 example_api_client.py --dataset dpcfam --mcids MC3 --base-url https://dpcexplorer.areasciencepark.it/api
    python3 example_api_client.py --dataset dpcfam --mcids MC1,MC3,MC504492
    python3 example_api_client.py --dataset dpcstruct --mcids MC0,MC64574

Requires only the 'requests' library:
    pip install requests
"""

import argparse
import json
import sys

import requests
# URL of the API
# (A) Production
DEFAULT_BASE_URL = "https://dpcexplorer.areasciencepark.it/api"
# (B) Local development server
# DEFAULT_BASE_URL = "http://127.0.0.1:8000/api"


def fetch_properties(base_url, dataset, mcids):
    """Fetch properties for one or several MCIDs in a single call."""
    url = f"{base_url}/{dataset}/mcs/"
    params = {"mcids": ",".join(mcids)}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()["results"]


def fetch_all_members(base_url, dataset, mcid, page_size=None):
    """
    Fetch every member of a single MCID, across all pages.

    The /members/ endpoint is paginated (10 per page by default;
    see DPCexplorer_API_Documentation.md, Section 5). This follows the
    "next" link returned in each page until the API reports None, so the
    caller gets the complete list back in one call, exactly like
    fetch_all_members() in the example notebook.
    """
    url = f"{base_url}/{dataset}/mcs/{mcid}/members/"
    params = {"page_size": page_size} if page_size else None

    all_members = []
    page_count = 0
    while url:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        payload = response.json()
        all_members.extend(payload["results"])
        page_count += 1
        print(f"  fetched page {page_count} ({len(payload['results'])} member(s), "
              f"{len(all_members)}/{payload['count']} so far)")
        url = payload["next"]
        params = None  # 'next' already carries the page number and page_size

    return all_members


def main():
    parser = argparse.ArgumentParser(description="DPCexplorer API example client")
    parser.add_argument(
        "--dataset", choices=["dpcfam", "dpcstruct"], required=True,
        help="Which dataset to query.",
    )
    parser.add_argument(
        "--mcids", required=True,
        help="One MCID or a comma-separated list, e.g. MC1,MC3,MC504492",
    )
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--output", default="dpcexplorer_api_result.json",
        help="Path to the output JSON file.",
    )
    args = parser.parse_args()

    mcids = [m.strip() for m in args.mcids.split(",") if m.strip()]

    # --- 1. Properties for every requested MCID -----------------------
    print(f"Fetching properties for {len(mcids)} MCID(s) from {args.dataset} ...")
    try:
        properties = fetch_properties(args.base_url, args.dataset, mcids)
    except requests.RequestException as exc:
        print(f"Error contacting the API: {exc}", file=sys.stderr)
        sys.exit(1)

    id_field = "mcid" if args.dataset == "dpcfam" else "mc_id"
    found_ids = {p[id_field] for p in properties}
    missing = set(mcids) - found_ids
    if missing:
        print(f"Warning: these MCIDs were not found and are skipped: {sorted(missing)}")

    # --- 2. All members, but only for the first requested MCID --------
    first_mcid = mcids[0]
    if first_mcid not in found_ids:
        print(f"'{first_mcid}' was not found; skipping the members fetch.")
        members = []
    else:
        print(f"Fetching ALL members for {first_mcid} (every page) ...")
        try:
            members = fetch_all_members(args.base_url, args.dataset, first_mcid)
        except requests.RequestException as exc:
            print(f"Error contacting the API: {exc}", file=sys.stderr)
            sys.exit(1)
        print(f"Retrieved {len(members)} member(s) for {first_mcid} in total.")

    result = {
        "properties": properties,
        "members": {
            "mcid": first_mcid,
            "count": len(members),
            "results": members,
        },
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(
        f"Done. Wrote properties for {len(properties)} metacluster(s) and "
        f"{len(members)} member(s) of {first_mcid} to {args.output}"
    )


if __name__ == "__main__":
    main()
