# DPCexplorer Repository Architecture

> 🗺️ Open this file to understand how the repository is organized: where the code lives, where the preprocessing material sits, and where to look next. It complements the **[README](README.md)**, which focuses on setup and on the data layout that the setup script generates.

DPCexplorer is a **Django 6.0.1** project organized into three focused applications, a project package, the HTML templates, and a `static/` directory that carries both the site assets and the full preprocessing trail. The protein data itself is not committed to the repository; it is fetched and built locally by `setup_dpcexplorer_data.sh` (see the README).

---

## 🌳 Top-level layout

```text
dpc_fam_and_struct_webapp/
├── manage.py                       # Django entry point
├── requirements.txt                # Python dependencies
├── setup_dpcexplorer_data.sh       # one-shot fetcher/builder for the datasets
├── .env.example                    # template for your local .env
├── README.md                       # setup, usage, reproducibility
├── ADMIN_PANEL.md                  # the admin panel: modes, how, why
├── ARCHITECTURE.md                 # this file
├── CITATION.cff                    # how to cite DPCexplorer
├── LICENSE                         # MIT
├── dpcexplorer_schema_outputs.txt  # saved database index/verification report
├── logs/                           # runtime logs (django_errors.log)
│
├── dpc_fam_and_struct_webapp/      # Django project package
│   ├── settings.py                 # configuration (incl. DPCEXPLORER_ADMIN_WRITABLE)
│   ├── urls.py                     # root routing + admin branding
│   ├── views.py                    # project-level search router
│   └── wsgi.py / asgi.py           # server entry points
│
├── dpc/                            # shared app: protein + Pfam registry
├── dpcfam/                         # sequence-based metaclusters
├── dpcstruct/                      # structure-based metaclusters
│
├── templates/                      # site-wide HTML (index, about, faqs, detail pages)
└── static/                         # assets, preprocessing material, and reports
```

---

## 🧩 The Django applications

Each application follows the standard Django layout (`models.py`, `admin.py`, `views.py`, `urls.py`, plus `tables.py` and `filters.py` for the interactive tables). Their database models use `managed = False`, because the tables are created and filled by our SQL loaders, not by Django migrations.

| Component | Responsibility |
|-----------|----------------|
| `dpc/` | Shared registry: UniProt proteins, Pfam domains, and the UniRef50 to Pfam mapping. |
| `dpcfam/` | Sequence-based metaclusters: properties, member sequences, and AlphaFold representatives. |
| `dpcstruct/` | Structure-based metaclusters: properties, sequences, and CATH/SCOP fold annotations. |
| `dpc_fam_and_struct_webapp/` | Project package: settings, root URLs, the search router, and server entry points. |

> 🔐 For how the admin panel exposes these models (read-only by default, full CRUD on demand), see **[ADMIN_PANEL.md](ADMIN_PANEL.md)**.

---

## 🗃️ Inside `static/`

The committed part of `static/` carries everything beyond the live application: the brand assets and the complete preprocessing trail.

```text
static/
├── images/              # logos: DPCexplorer, DPCfam, DPCstruct, AREA Science Park, SISSA
├── notebooks/           # Jupyter notebooks used for preprocessing, grouped by dataset
│   ├── dpc/             # shared: protein lengths, Pfam IDs
│   ├── dpcfam/          # DPCfam exploration and master-CSV builders
│   └── dpcstruct/       # DPCstruct exploration, CATH/SCOP, representatives
├── scripts/             # SQL and Python helpers for the data pipeline
│   ├── dpc/             # create/populate shared tables, env check, schema diagram
│   ├── dpcfam/          # UniRef extraction, table SQL, per-subset Zenodo READMEs
│   ├── dpcstruct/       # UniProt length retrieval, table SQL
│   ├── inspect_db_and_table_volumes.sql
│   └── verify_dpcexplorer_db_indexes.sql
├── profiling_reports/   # EDA reports for most CSVs, plus correlation figures
│   ├── dpcfam/
│   ├── dpcstruct/
│   └── weekly_tasks/    # weekly progress reports (PDF)
│
└── (generated at setup) dataframes/ · downloads/ · production_files/
```

A few pointers on what each part is for:

- **`images/`** holds the logos used across the site and in the About page.
- **`notebooks/` and `scripts/`** are the heart of the preprocessing. They turn the raw DPCfam and DPCstruct sources into the PostgreSQL-ready CSVs that the application ingests. The notebooks explore and build the master tables; the scripts handle the heavy extraction (for example streaming the 81 GB UniRef XML, or querying the UniProt REST API for missing protein lengths) and the SQL that creates and populates the database.
- **`profiling_reports/`** contains the **EDA profiling reports** (HTML) for most of the CSVs, along with the correlation figures, and `weekly_tasks/` keeps the weekly progress reports.
- **`dataframes/`, `downloads/`, and `production_files/`** are not committed: the setup script builds them locally. Their expected layout is documented in the README.

> 📖 To explore the preprocessing in depth: **Chapter 3** of the thesis describes the methodology, and **Appendix A** lists every notebook and script with its exact purpose. The preprocessed outputs live on Zenodo at [doi.org/10.5281/zenodo.20159208](https://doi.org/10.5281/zenodo.20159208). The thesis itself is reserved under the concept DOI [doi.org/10.5281/zenodo.20847161](https://doi.org/10.5281/zenodo.20847161); once published, you will be able to follow the whole preprocessing story end to end.

---

## 🔁 How a request flows

A visit to a metacluster or protein page travels a short, predictable path: `urls.py` routes the request to the matching app view, the view queries the `managed = False` models over PostgreSQL, and the result is rendered through **django-tables2** (interactive tables) and **django-filter** (search filters), with structures shown in an embedded **3D molecular viewer** (PDBe-Molstar). The admin panel sits beside this, on `/admin/`, as a read-only inspection console by default.

> 💬 Should you add a new feature or dataset, keep this structure in mind: a new data table belongs to one of the three apps, its loader to `static/scripts/`, and its exploration to `static/notebooks/`. 
