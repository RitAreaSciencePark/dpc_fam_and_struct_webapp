<p align="center">
  <img src="https://raw.githubusercontent.com/RitAreaSciencePark/dpc_fam_and_struct_webapp/main/static/images/logo_dpcexplorer_web.png" alt="DPCexplorer Logo" height="100" />
</p>

---

# DPCexplorer: A Django Web Application for Interactive Exploration of DPCfam and DPCstruct Protein Domain Classifications

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp)
![Status](https://img.shields.io/badge/Status-Stable%20v1.0.3-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
[![DOI Software](https://zenodo.org/badge/DOI/10.5281/zenodo.20575268.svg)](https://doi.org/10.5281/zenodo.20575268)
[![DOI Data](https://zenodo.org/badge/DOI/10.5281/zenodo.20159208.svg)](https://doi.org/10.5281/zenodo.20159208)
[![CFF](https://img.shields.io/badge/Citation-CITATION.cff-blue?style=flat-square)](CITATION.cff)

Proteins carry out almost every function inside a living cell, but
scientists can only experimentally characterize a tiny fraction of
the millions known today. One powerful shortcut is to group proteins
into **families**: members of the same family typically share the same
evolutionary origin and, usually, a similar function. If one member
is well studied, that knowledge can be carefully transferred to the rest.

**Pfam** remains the most widely used protein family database, building
families from Multiple Sequence Alignments and profile Hidden Markov Models.
Recent advances like **Pfam-N**, which uses transformer-based models and
convolutional neural networks, have pushed coverage further by detecting
remote homologs that classical methods missed, increasing UniProtKB coverage
by **8.8%**. Yet a fundamental tension remains: expert curation is limited
by human bandwidth, and machine learning models are bounded by their training
data. A genuinely novel family, one with no known relatives, generally stays invisible
to both.

**DPCexplorer** makes two large, publicly available protein-family
datasets easy to explore, with no programming required. Both datasets were
produced by applying the **Density Peak Clustering (DPC)** algorithm to
automatically group protein domains into families called **metaclusters**,
without any manual curation.

| Dataset | Input data | Metaclusters | Original source | Preprocessed files |
|---------|-----------|:------------:|-----------------|-------------------|
| **DPCfam** | ~23 M sequences (UniRef50 v. 2017_07) | 81,384 | [zenodo.org/records/6900559](https://doi.org/10.5281/zenodo.6900559) | [zenodo.org/records/20159208](https://doi.org/10.5281/zenodo.20159208) |
| **DPCstruct** | ~15 M structures (AlphaFoldDB v4.0) | 28,246 | [zenodo.org/records/13334296](https://doi.org/10.5281/zenodo.13334296) | [zenodo.org/records/20159208](https://doi.org/10.5281/zenodo.20159208) |

Both datasets have been validated against established databases. DPCfam
recovers approximately **81%** of medium-to-large Pfam families and **72%**
of ECOD families. DPCstruct recovers **91%** of SCOP folds and **83%** of
CATH folds; when compared against Pfam at the clan level, **70%** of the
14,423 metaclusters with available Pfam labels achieved a perfect consistency
score of 1, meaning every member shared the same Pfam annotation. Furthermore,
**24%** of DPCstruct metaclusters show no significant similarity to any known
database, including Pfam, CATH, or SCOP, pointing toward a pool of potential
novel structural folds. The average intra-cluster sequence identity in DPCstruct
is only **34.5%**, placing most families well within the twilight zone where
standard sequence-based tools become unreliable.

About half of all metaclusters match known families from Pfam. The other half
consists of specifically **47,002** metaclusters (**33,179** in DPCfam and
**13,823** in DPCstruct) labeled **UNKNOWN** in DPCexplorer. They are not
errors or noise; rather, they are structurally and sequentially coherent
protein families that simply have not been named yet. Some may represent novel
folds, while others may be ancient families overlooked by curation-based
approaches. The evidence for their biological relevance is concrete: **63**
DPCfam UNKNOWN metaclusters were adopted as official new entries in
**Pfam release 35.0** (e.g., MC202620 → PF20147, MC15137 → PF20146). These UNKNOWN metaclusters are arguably the most
interesting ones. If you have a biological hypothesis about any of them,
please open an issue; we would genuinely love to hear from you.

The platform is built with **Django 6.0.1** and organized into three
focused applications: `dpc` (shared protein and Pfam registry),
`dpcfam` (sequence-based metaclusters), and `dpcstruct`
(structure-based metaclusters). You can search by DPCfam or DPCstruct
metacluster ID, by Pfam ID (family or clan), or by UniProt accession, and explore
results through interactive tables, a domain-architecture diagram, and
an embedded **3D molecular viewer** powered by PDBe-Molstar.

> 📚 **Further documentation.** Three companion guides live next to this README:
> [**`ARCHITECTURE.md`**](ARCHITECTURE.md) maps the repository, the source apps, the preprocessing notebooks and scripts, and the static assets, so you can find your way around;
> [**`ADMIN_PANEL.md`**](ADMIN_PANEL.md) documents the admin panel, its read-only default, and how to enable full CRUD; and
> [**`docs/DOCKER.md`**](docs/DOCKER.md) explains how to build, run, test, and stop the containerized application.

---

## 🎯 Production Status & Reproducibility

> 🌐 **Live Platform Deployment:** Our web platform will soon be officially hosted and available online at: [https://dpcexplorer.areasciencepark.it/](https://dpcexplorer.areasciencepark.it/)

Identify your exact use case below to run or update the local application instance:

---

### Scenario 1: First-Time Setup (New User)

Follow all steps (**1 to 7**) in order, as outlined in the **[Table of Contents](#table-of-contents)** below . This will clone the repository, install dependencies, download the datasets automatically, set up the database, and get the application running.

---

### Scenario 2: Rerunning the App (Daily Use) 

If you have already completed the first-time setup and just want to restart the application locally, open your terminal in the project root and run:

```bash
# 1. Start the database service
sudo service postgresql start

# 2. Activate your virtual environment
source .venv/bin/activate

# 3. Run the server
python3 manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser. You are already familiar with the rest.

> 💬 Should you have feedback for improving DPCexplorer, or a biological insight about an **UNKNOWN** metacluster, we genuinely can't wait to hear from you. Jump to **[Hints for Common Situations](#hints-for-common-situations)** to get in touch.

---

### Scenario 3: Syncing Changes (Returning User Updates)

If you are returning to the project after a while and need to pull down the latest codebase updates, schema migrations, or dependency changes, then, welcome back! Run these quick steps to sync the latest changes:

1. Move to the project directory: 

```bash
cd dpc_fam_and_struct_webapp
```

2. Pull the latest changes: 

```bash
git pull
```

> ⚠️ Should you experience any issue after pulling the latest changes, please check out our **[Hints for Common Situations](#hints-for-common-situations)** section before going further.

3. Activate your virtual environment: 

```bash
source .venv/bin/activate
```

4. Install any new dependencies: 

```bash
pip install -r requirements.txt
```

5. Start the PostgreSQL service: 

```bash
sudo service postgresql start
```

6. Sync the database: 

```bash
python3 manage.py migrate
```

7. Run the server: 

```bash
python3 manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser. 

 - To stop the server: Press `Ctrl+C`.

 - To stop PostgreSQL: Run:
  
 ```bash
 sudo service postgresql stop
 ```


---

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Clone the Repository](#2-clone-the-repository)
- [3. Installation & Data Fetching](#3-installation--data-fetching)
- [4. Database Initialization](#4-database-initialization)
  - [4.1 Create User and Database](#41-create-user-and-database)
  - [4.2 Create Tables and Populate Them](#42-create-tables-and-populate-them)
- [5. Django Migrations](#5-django-migrations)
- [6. Run the Server](#6-run-the-server)
- [7. Usage](#7-usage)
- [Hints for common situations](#hints-for-common-situations)
- [References](#references)

---

### 1. Prerequisites

![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04.3%20LTS-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12.3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.11-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Git](https://img.shields.io/badge/Git-2.43.0-F05032?style=for-the-badge&logo=git&logoColor=white)
![VS Code](https://img.shields.io/badge/VS%20Code-1.109.3-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

Our development environment runs smoothly on:

- [Ubuntu](https://ubuntu.com/) 24.04.3 LTS *(Required: or any modern Linux system)*
- [Python](https://www.python.org/) 3.12.3 *(Required: check with `python3 --version`)*
- [Git](https://git-scm.com/) 2.43.0 *(Required: check with `git --version`)*
- [PostgreSQL](https://www.postgresql.org/) 16.11 *(Required: check with `psql --version`)*
- [Visual Studio Code](https://code.visualstudio.com/) 1.109.3 *(Optional: use any editor you like!)*

> **Note:** If you are missing `Git` or `PostgreSQL` on an Ubuntu system, you can install them with these quick commands:

```bash
sudo apt update && sudo apt install -y git postgresql postgresql-contrib
```

**Expected file tree.** After Step 3, the `static/` directory will be organized as follows. The setup script builds this automatically; you do not need to create anything by hand.

```text
static/
├── dataframes/                                 # PostgreSQL-ready CSV files
│   ├── dpc/
│   ├── dpcfam/
│   └── dpcstruct/
:
├── downloads/                                  # DPCexplorer global downloads
│   ├── dpcfam/
│   │   ├── dpcfam_mcid_seeds.tar.gz            # Seed FASTA files (one per MCID)
│   │   ├── dpcfam_mcid_msas.tar.gz             # MSA files (one per MCID)
│   │   ├── dpcfam_mcid_hmms.tar.gz             # HMM profiles (one per MCID)
│   │   └── dpcfam_all_metaclusters_hmms.tar.gz # All MCs HMM profiles in two files (Standard + DPCfamB)
│   └── dpcstruct/
│       ├── dpcstruct_mcid_seeds.tar.gz         # Representative FASTA files (one per MCID)
│       └── dpcstruct_mcid_pdbs.tar.gz          # Representative PDB files (one zip per MCID)
:
└── production_files/                           # DPCexplorer local downloads (Per-MCID files served on detail pages)
    ├── dpcfam/
    │   ├── metaclusters_fasta/                 # MCID.fasta
    │   ├── metaclusters_hmms/                  # MCID.hmm
    │   └── metaclusters_cdhit_msas/            # MCID_msa.fasta
    └── dpcstruct/
        ├── dpcstruct_reps_seqs/                # MCID.fasta
        ├── dpcstruct_reps_pdbs_zipped/         # MCID_pdb.zip
        └── dpcstruct_reps_pdbs/                # MCID_pdb/ folders with .pdb files (for the Mol* viewer)
```

---

### 2. Clone the Repository

```bash
git clone https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp
cd dpc_fam_and_struct_webapp
```

---

### 3. Installation & Data Fetching

![pip](https://img.shields.io/badge/pip-Package%20Manager-3775A9?style=flat-square&logo=pypi&logoColor=white)
![venv](https://img.shields.io/badge/venv-Virtual%20Environment-3776AB?style=flat-square&logo=python&logoColor=white)

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate a `.env` file with secure credentials:

   ```bash
   python3 -c "
   import secrets
   from django.core.management.utils import get_random_secret_key
   print(f'''DJANGO_SECRET_KEY={get_random_secret_key()}
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DB_NAME=dpcexplorer_db
   DB_USER=dpcexplorer_admin
   DB_PASSWORD={secrets.token_urlsafe(16)}
   DB_HOST=localhost
   DB_PORT=5432
   DPCEXPLORER_ADMIN_WRITABLE=False''')
   " > .env
   ```

   > **Note:** This creates a `.env` file with a `random Django secret key` and a `random database password`. You do not need to edit it manually. If you prefer your own values, simply open `.env` and change them. The `DPCEXPLORER_ADMIN_WRITABLE` flag controls the admin panel: it is `False` (read-only) by default; set it to `True` only to enable full CRUD. See [ADMIN_PANEL.md](ADMIN_PANEL.md).

4. **Download and prepare the datasets:**

   Run the setup script in your terminal:

   ```bash
   bash setup_dpcexplorer_data.sh
   ```

   When you run this script, you can choose between two installation choices depending on your computer's free space. You may want to grab a coffee (or two) ☕ because downloading and preparing the data takes some time.

   * **Option 1: Full Installation (Default)**

     This downloads and installs everything (DPCfam, DPCstruct, and all DPCexplorer CSV files).

     > ⚠️ **Important Storage Notice:** This option downloads about **11 GB** of compressed data from Zenodo. After uncompressing over 200,000 files and loading millions of rows into the PostgreSQL database, your computer will need **at least 50 GB of free disk space**. We strongly recommend using a fast SSD.

   * **Option 2: Lightweight Mode (Fast Review)**

     This option downloads only the structural data (**DPCstruct files**) and the database tables (**DPCexplorer CSV files**). It skips the heavy DPCfam files completely.

     > ⚠️ **Important Storage Notice:** This option needs **only about 25 GB of free disk space**.

     > *Note:* If you choose this option, the web application Downloads pages for DPCfam will be empty. This mode is perfect for a quick review of the database queries and the 3D structure viewer.

---

### 4. Database Initialization

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.11-336791?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Scripts-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)

Start the local database service daemon:

```bash
sudo service postgresql start
```

#### 4.1 Create User and Database

The following reads the credentials from your `.env` file and creates the PostgreSQL user and database:

```bash
# 1. Load your local environment configurations
export $(grep -v '^#' .env | xargs)

# 2. Create the user role and database independently
sudo -u postgres psql \
  -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" \
  -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
```

#### 4.2 Create Tables and Populate Them

Run the three pairs of scripts below, in order. Each pair creates the tables, then loads the data from CSV files and create indexes.

##### A. dpc (Core Registry)

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpc/create_dpc_tables.sql
```

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpc/populate_dpc_tables.sql
```

##### B. dpcfam (Sequence-Based Metaclusters)

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcfam/create_dpcfam_tables.sql
```

>**Note**: The following step loads ~16 million rows and will take a few minutes. Please wait until it finishes.

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcfam/populate_dpcfam_tables.sql
```

##### C. dpcstruct (Structure-Based Metaclusters)

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcstruct/create_dpcstruct_tables.sql
```

```bash
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcstruct/populate_dpcstruct_tables.sql
```

---

### 5. Django Migrations

![Django](https://img.shields.io/badge/Django-Migrations-092E20?style=flat-square&logo=django&logoColor=white)

All Django migrations are already included in the repository. Just run:

```bash
python3 manage.py migrate
```

After migrating, you can create an admin account to reach the admin panel at `/admin/`:

```bash
python3 manage.py createsuperuser
```

> **Note:** The admin panel is read-only by default; it inspects the data, never edits it. To enable full CRUD, set `DPCEXPLORER_ADMIN_WRITABLE=True` in your `.env`. See [ADMIN_PANEL.md](ADMIN_PANEL.md).

---

### 6. Run the Server

![Django](https://img.shields.io/badge/Django-runserver-092E20?style=flat-square&logo=django&logoColor=white)
![localhost](https://img.shields.io/badge/localhost-8000-blue?style=flat-square)

```bash
python3 manage.py runserver
```

---

## 7. Usage

![Chrome](https://img.shields.io/badge/Google%20Chrome-Recommended-4285F4?style=flat-square&logo=googlechrome&logoColor=white)

Open your browser and go to:

```
http://127.0.0.1:8000/
```

You can search by DPCfam MCID (e.g., `MC1`), DPCstruct MCID (e.g., `MC5`), Pfam ID (e.g., `PF02990`), or UniProt accession (e.g., `A0A182N2I3`).

> **Note:** Congratulations, you made it! 🎉

> To stop the server, press `Ctrl+C`. 

> To stop PostgreSQL, run:

```bash
sudo service postgresql stop
```

> **Tip:** Once the database is fully loaded, you can delete the CSV files in `static/dataframes/` to free up disk space.

If you find a bug or have feedback, please open an issue on our GitHub page. We are actively developing DPCexplorer, and many more features are coming soon!

> Thank you for trying out **DPCexplorer**, your feedback is greatly appreciated!

> Should you run into a problem at any point, or have a hypothesis about an **UNKNOWN** metacluster, check out our **[Hints for Common Situations](#hints-for-common-situations)** section, it is the right place to start.

---

## Hints for Common Situations

> These tips assume you have already cloned the repository and gone through
> the first-time setup at least once. They exist so you do not have to dig
> through PostgreSQL documentation when something goes wrong.

### Dropping the database and user (clean reset)

If you need to start the database from scratch, for example after a failed
import or a settings change, run these two commands. They are safe even if
the database or user do not exist yet:

```bash
sudo -u postgres psql -d postgres \
  -c "DROP DATABASE IF EXISTS dpcexplorer_db;"
sudo -u postgres psql -d postgres \
  -c "DROP ROLE IF EXISTS dpcexplorer_admin;"
```

Then go back to **Step 4** of the first-time setup to recreate them.

---

### Inspecting our database optimization

Curious about how the indexes actually perform, or want to help us improve
them? This command runs our full verification suite and saves the output to
a text file you can read at your own pace:

```bash
# 1. Load your local environment configurations
export $(grep -v '^#' .env | xargs)
# 2. Write outputs to a file
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME \
  -f static/scripts/verify_dpcexplorer_db_indexes.sql \
  > dpcexplorer_schema_outputs.txt
```

> **Note:** This assumes you have a running PostgreSQL instance with the
> database already populated (after Step 4.2). Open
> `dpcexplorer_schema_outputs.txt` in any text editor to read the results.
> Section 7 of that report is especially useful: it tells you the
> index usage rate for every table.

---

### Recovering from a broken local clone

If `git pull` throws merge conflicts or your local copy is out of sync,
the cleanest fix is to start from scratch. Drop your database first, then
remove the clone:

```bash
# 1. Drop the database and user (see section above)
sudo -u postgres psql -d postgres -c "DROP DATABASE IF EXISTS dpcexplorer_db;"
sudo -u postgres psql -d postgres -c "DROP ROLE IF EXISTS dpcexplorer_admin;"

# 2. Remove the local clone (⚠ this deletes everything in the folder)
cd ..
rm -rf dpc_fam_and_struct_webapp

# 3. Clone again and restart from Step 1
git clone https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp
cd dpc_fam_and_struct_webapp
```

Then follow the full first-time setup from **Step 3** onwards.

---

### Do you have a hypothesis about an UNKNOWN metacluster?

Both DPCfam and DPCstruct contain **47,002** of metaclusters labelled
**UNKNOWN**, meaning they carry **no known Pfam annotation**. If you have biological expertise and believe
you can identify what one of these families does, we genuinely want to hear from you.

Please open an issue on our GitHub page and describe:

- the MCID you are looking at (e.g. `MC15` for DPCfam, `MC2` for DPCstruct)
  
- your hypothesis and any supporting evidence (literature, BLAST hits, etc.)

Every confirmed annotation helps close the protein annotation gap, which is
exactly why this project exists.

> Open an issue here:
> [https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp/issues](https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp)

---

## References

## How to Cite This Work

If you use DPCexplorer in your work, please cite the software:

> Nyandu Kagarabi, E., Saadat, E., & Piomponi, V. (2026). *DPCexplorer: A Django Web Application for Interactive Exploration of DPCfam and DPCstruct Protein Domain Classifications* [Software]. Zenodo. https://doi.org/10.5281/zenodo.20575268

This concept DOI always resolves to the latest release. The related works (the preprocessed dataset, the eScience 2026 paper, and the Master's thesis) are linked from the Zenodo record.

## Underlying Methods and Datasets

DPCexplorer builds on the following works; please cite them where relevant.

* **DPCfam (method):** Russo, E. T., Barone, F., Bateman, A., Cozzini, S., Punta, M., & Laio, A. (2022). DPCfam: Unsupervised protein family classification by density peak clustering of large sequence datasets. *PLOS Computational Biology*, *18*(10), e1010610. https://doi.org/10.1371/journal.pcbi.1010610
* **DPCfam (source dataset):** Russo, E. T., & Barone, F. (2022). *Metaclusters by DPCfam clustering of UniRef50 v 2017_07* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6900559
* **DPCstruct (method):** Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2025). Unsupervised domain classification of AlphaFold2-predicted protein structures. *PRX Life*, *3*(2), 023009. https://doi.org/10.1103/PRXLife.3.023009
* **DPCstruct (source dataset):** Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2024). *DPCstruct classification of AlphaFold2-predicted protein structures* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.13334296
* **Clustering algorithm:** Rodriguez, A., & Laio, A. (2014). Clustering by fast search and find of density peaks. *Science*, *344*(6191), 1492–1496. https://doi.org/10.1126/science.1242072

---

### 📜 Acknowledgments

This work was carried out during a Research Internship at the **Laboratory of Data Engineering (LADE)**, Area Science Park, Trieste, Italy, as part of the MDMC Master's programme at SISSA. 

This project was funded by the European Union - NextGenerationEU via:
* **[NFFA-DI](https://nffa-di.it/)** (cod. IR0000015)
* **[EFC](https://educatingfuturecitizens.com/)** (cod. SSU2024-00002)
* **PRP@CERIC** (cod. IR0000028); PNRR Mission 4, Component 2, Investment 3.1, Action 3.1.1 ([prp-ri.eu](https://prp-ri.eu/))
  
---
