# DPCexplorer REST API Documentation

This document describes the read-only REST API added to DPCexplorer in
version **v1.1.0**. It is written for two audiences: researchers who want to
pull DPCfam or DPCstruct data into their own scripts, and maintainers who
need to extend the API later.

The API sits next to the existing web pages; it does not replace them. Both
read from the same PostgreSQL database described in [**`ARCHITECTURE.md`**](ARCHITECTURE.md).

---

## 1. Why this API exists

Before this release, getting DPCfam or DPCstruct data programmatically meant
downloading gigabyte-scale archives from Zenodo (see the main [**`README.md`**](README.md)).
The API gives a lightweight alternative: send an MCID, or a short list of
MCIDs, and get back a small JSON payload instead of a multi-gigabyte file, improving the **FAIR**ness of our platform.

## 2. Access and authentication

- **Base URL (local):** `http://127.0.0.1:8000/api/`
- **Base URL (production):** `https://dpcexplorer.areasciencepark.it/api/`
- **Authentication:** none. The API is public and **read-only**, exactly
  like the rest of DPCexplorer. There is no login, token, or API key.
- **Format:** JSON by default. Because Django REST Framework's browsable
  API is enabled, opening any endpoint in a normal web browser renders a
  readable HTML page instead; append `?format=json` to force raw JSON from
  a browser.

## 3. Endpoints at a glance

| Endpoint | Method | Returns |
|---|---|---|
| `/api/dpcfam/mcs/` | GET | Paginated list of all 81,384 DPCfam metaclusters |
| `/api/dpcfam/mcs/?mcids=MC1,MC3,MC15` | GET | Only the requested DPCfam metaclusters |
| `/api/dpcfam/mcs/{mcid}/` | GET | Properties of one DPCfam metacluster |
| `/api/dpcfam/mcs/{mcid}/members/` | GET | Seed sequences of one DPCfam metacluster |
| `/api/dpcstruct/mcs/` | GET | Paginated list of all 28,246 DPCstruct metaclusters |
| `/api/dpcstruct/mcs/?mcids=MC1,MC5` | GET | Only the requested DPCstruct metaclusters |
| `/api/dpcstruct/mcs/{mc_id}/` | GET | Properties of one DPCstruct metacluster |
| `/api/dpcstruct/mcs/{mc_id}/members/` | GET | Seed sequences of one DPCstruct metacluster |

`{mcid}` and `{mc_id}` are metacluster identifiers such as `MC1` or
`MC15`, exactly as used elsewhere in DPCexplorer, case-sensitive.

## 4. DPCfam properties

`GET https://dpcexplorer.areasciencepark.it/api/dpcfam/mcs/MC1/`

```json
{
    "mcid": "MC1",
    "size_uniref50": 17931,
    "avg_len": 185.68,
    "std_avg_len": 28.77,
    "lc_percent": 4.72,
    "cc_percent": 0.0,
    "dis_percent": 18.44,
    "tm": 0.01,
    "pfam_da": "PF13614",
    "da_percent": 44.23,
    "avg_ov_percent": 80.82,
    "overlap_label": "Equivalent"
}
```

## 5. DPCfam members

`GET https://dpcexplorer.areasciencepark.it/api/dpcfam/mcs/MC1/members/`

```json
{
    "count": 17931,
    "next": "http://127.0.0.1:8000/api/dpcfam/mcs/MC1/members/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "protein_id": "B0C3J8",
            "seq_range": "589-773"
        },
        {
            "id": 2,
            "protein_id": "I4CCA7",
            "seq_range": "496-701"
        },
  ]
}
```

Members are paginated at 10 per page by default, since the largest DPCfam
metacluster holds over 130,000 seeds. Add `?page=2` or
`?page_size=500` (maximum 500) to the URL to move through the list.

## 6. DPCstruct properties and members

Same shape, using `mc_id` instead of `mcid`, and structural fields instead
of sequence-composition fields:

`GET https://dpcexplorer.areasciencepark.it/api/dpcstruct/mcs/MC5/`

```json
{
    "mc_id": "MC5",
    "mc_size": 46,
    "len_aa": 159.04,
    "len_std": 38.84,
    "len_ratio": 0.24,
    "plddt": 81.34,
    "disorder": 0.19,
    "tmscore": 0.56,
    "lddt": 0.57,
    "pident": 17.34,
    "pfam_score": 100.0,
    "pfam_da": "CL0263"
}
```

`GET https://dpcexplorer.areasciencepark.it/api/dpcstruct/mcs/MC5/members/` returns `id`, `protein_id`, and
`prot_range` for each of that metacluster's seed
sequences, in the same paginated shape as the DPCfam example above.

## 7. Requesting several MCIDs at once

Pass a comma-separated list through the `mcids` query parameter on the
**list** endpoint, not the detail endpoint:

```
GET https://dpcexplorer.areasciencepark.it/api/dpcfam/mcs/?mcids=MC1,MC3,MC15
GET https://dpcexplorer.areasciencepark.it/api/dpcstruct/mcs/?mcids=MC1,MC5
```

IDs that do not exist are silently skipped; unmatched IDs are not reported
as errors, so it is safe to send a mixed batch and simply check which MCIDs
came back. For very large lists (say, several thousand IDs), split the
request into batches of a few hundred to keep the URL length reasonable;
there is no bulk POST endpoint in this release (see Section 9).

## 8. Errors

| Situation | Response |
|---|---|
| Unknown single MCID (`/api/dpcfam/mcs/MC2/`) | `404 Not Found`, `{"detail": "No DpcfamMcsProperty matches the given query."}` |
| Unknown MCID inside a `?mcids=` list | Silently omitted from `results`, no error |
| Malformed page number | `{"detail": "Invalid page."}` |

## 9. Known limitations and planned extensions

- No bulk `POST` endpoint yet: a client sending thousands of MCIDs must
  batch requests through the `?mcids=` query parameter.
- No Pfam ID or UniProt accession endpoints yet; only DPCfam and DPCstruct
  metacluster lookups are exposed, matching the specific request that
  motivated this release.
- No response caching; every request hits PostgreSQL directly. The
  underlying indexes (`ARCHITECTURE.md`, `verify_dpcexplorer_db_indexes.sql`)
  keep this fast, but a high-traffic integration should still cache results
  client-side.

These are natural next steps and were intentionally left out of v1.1.0 to
keep the first release small and easy to review.

## 10. Example client

A minimal Python script and an equivalent Jupyter notebook are provided in
`static/scripts/api_examples/`:

- [`example_api_client.py`](static/scripts/api_examples/example_api_client.py)
- [`example_api_client_notebook.ipynb`](static/scripts/api_examples/example_api_client_notebook.ipynb)

Both accept a dataset choice (`dpcfam` or `dpcstruct`) and either a single
MCID or a comma-separated list, fetch the properties and all members of the first MCID, and save the combined result to a local JSON file (e.g. [`static/scripts/api_examples/dpcexplorer_api_result.json`](static/scripts/api_examples/dpcexplorer_api_result.json)). See
the script's own docstring for usage, or run:

```bash
python3 static/scripts/api_examples/example_api_client.py --help
```

## 11. Maintainers: where the code lives

| File | Role |
|---|---|
| `api/serializers.py` | Maps model instances to JSON fields |
| `api/views.py` | `ViewSet`s, the `?mcids=` filter, and the `/members/` action |
| `api/urls.py` | `DPCexplorerRouter` registration for both datasets |
| `dpc_fam_and_struct_webapp/settings.py` | `rest_framework` + `api` in `INSTALLED_APPS`, the `REST_FRAMEWORK` block |
| `dpc_fam_and_struct_webapp/urls.py` | `path('api/', include('api.urls'))` |

To add a new field to a response, edit the relevant `fields` list in
`api/serializers.py` only; no view or URL changes are needed. To add a new
resource (for example, a future Pfam or UniProt endpoint), copy the
pattern of one existing `ViewSet` and register it in `api/urls.py`.

## 12. Step-by-Step DPCexplorer REST API Implementation

Check out [**`docs/DPCexplorer_API_implementation.md`**](docs/DPCexplorer_API_implementation.md) for a detailed, step-by-step implementation guide.
