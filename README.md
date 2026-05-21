# Web Application for DPCfam and DPCstruct Data Exploration

![Status](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp)

Hi! Thank you for visiting our repository.

Welcome to **DPCexplorer**: a Django web application for the interactive exploration of *protein domain families*. Our platform relies primarily on two datasets, **DPCfam** and **DPCstruct**, where protein sequences and structures are automatically grouped into domain families (called *metaclusters*) using the Density Peak Clustering (DPC) algorithm.

| Dataset | Description | Metaclusters | Original Source | Preprocessed Derivative |
|---------|-------------|--------------|-----------------|-------------------------|
| **DPCfam** | Sequence-based domain clusters | 81,384 | [DOI: 10.5281/zenodo.6900559](https://doi.org/10.5281/zenodo.6900559) | [DOI: 10.5281/zenodo.20159208](https://doi.org/10.5281/zenodo.20159208) |
| **DPCstruct** | Structure-based domain clusters | 28,246 | [DOI: 10.5281/zenodo.13334296](https://doi.org/10.5281/zenodo.13334296) | [DOI: 10.5281/zenodo.20159208](https://doi.org/10.5281/zenodo.20159208) |

Some of these metaclusters match known families from databases like **Pfam**. Others are completely new and labeled as **UNKNOWN**, and that is where it gets exciting! If you have a hypothesis about what any of these unknown clusters could be, we would love to hear from you.

This Django project consists of three applications: `dpc` (shared data registry), `dpcfam` (sequence-based metaclusters), and `dpcstruct` (structure-based metaclusters).

---

## 🎯 Production Status & Reproducibility

> 🌐 **Live Platform Deployment:** Our web platform will soon be officially hosted and available online at: [https://dpcexplorer.areasciencepark.it/](https://dpcexplorer.areasciencepark.it/)

Identify your exact use case below to run or update the local application instance:

### Scenario 1: First-Time Setup (New User)

Follow all steps (**1 to 7**) in order, as outlined in the **Table of Contents** below . This will clone the repository, install dependencies, download the datasets automatically, set up the database, and get the application running.

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
- [PostgreSQL](https://www.postgresql.org/) 16.13 *(Required: check with `psql --version`)*
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
git clone https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp
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
   DB_NAME=dpc_db
   DB_USER=dpc_admin
   DB_PASSWORD={secrets.token_urlsafe(16)}
   DB_HOST=localhost
   DB_PORT=5432''')
   " > .env
   ```

   > **Note:** This creates a `.env` file with a `random Django secret key` and a `random database password`. You do not need to edit it manually. If you prefer your own values, simply open `.env` and change them.

4. **Download and prepare the datasets:**

   Run the setup script in your terminal:

   ```bash
   bash setup_dpcexplorer_data.sh
   ```

   When you run this script, you can choose between two installation choices depending on your computer's free space. You may want to grab a coffee (or two) ☕ because downloading and preparing the data takes some time.

   * **Option 1: Full Installation (Default)**

     This downloads and installs everything (DPCfam, DPCstruct, and all DPCexplorer CSV files).

     > ⚠️ **Important Storage Notice:** This option downloads about **11 GB** of compressed data from Zenodo. After uncompressing over 200,000 files and loading millions of rows into the PostgreSQL database, your computer will need **at least 100 GB of free disk space**. We strongly recommend using a fast SSD.

   * **Option 2: Lightweight Mode (Fast Review)**

     This option downloads only the structural data (**DPCstruct files**) and the database tables (**DPCexplorer CSV files**). It skips the heavy DPCfam files completely.

     > ⚠️ **Important Storage Notice:** This option needs **only about 15 GB of free disk space**.

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
export $(grep -v '^#' .env | xargs)
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '${DB_PASSWORD}'; CREATE DATABASE $DB_NAME OWNER $DB_USER;"
```

#### 4.2 Create Tables and Populate Them

Run the three pairs of scripts below, in order. Each pair creates the tables (+ indexes) and then loads the data from CSV files.

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

## References

If you use this project, the web application, or the associated datasets, please cite:

#### 1. Project & Preprocessed Datasets
* **Web Application & Master Thesis:** Nyandu Kagarabi, E. (2026). *Web Application for DPCfam and DPCstruct Data Exploration*. Master's thesis, Master in Data Management and Curation, SISSA. Supervised by Dr. Valerio Piomponi & Dr. Elaheh Saadat. [Zenodo Link Pending Review]
* **Preprocessed Datasets:** Nyandu Kagarabi, E., Piomponi, V., & Saadat, E. (2026). Preprocessed Datasets for Interactive Exploration of DPCfam and DPCstruct Protein Domain Classifications (1.0.0) [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.20159208](https://doi.org/10.5281/zenodo.20159208)

#### 2. DPCfam (Sequence-Based Metaclusters)
* **Method Paper:** Russo, E. T., Barone, F., Bateman, A., Cozzini, S., Punta, M., & Laio, A. (2022). DPCfam: Unsupervised protein family classification by density peak clustering of large sequence datasets. *PLOS Computational Biology*, *18*(10), e1010610. [https://doi.org/10.1371/journal.pcbi.1010610](https://doi.org/10.1371/journal.pcbi.1010610)
* **Source Dataset:** Russo, E. T., & Barone, F. (2022). Metaclusters by DPCfam clustering of UniRef50 v 2017_07 [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.6900559](https://doi.org/10.5281/zenodo.6900559)

#### 3. DPCstruct (Structure-Based Metaclusters)
* **Method Paper:** Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2025). Unsupervised domain classification of AlphaFold2-predicted protein structures. *PRX Life*, *3*(2), 023009. [https://doi.org/10.1103/PRXLife.3.023009](https://doi.org/10.1103/PRXLife.3.023009)
* **Source Dataset:** Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2024). DPCstruct classification of AlphaFold2-predicted protein structures [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.13334296](https://doi.org/10.5281/zenodo.13334296)

#### 4. Clustering Algorithm Foundations
* Rodriguez, A., & Laio, A. (2014). Clustering by fast search and find of density peaks. *Science*, *344*(6191), 1492–1496. [https://doi.org/10.1126/science.1242072](https://doi.org/10.1126/science.1242072)

---

### 📜 Acknowledgments

This work was carried out during a Research Internship at the **Laboratory of Data Engineering (LADE)**, Area Science Park, Trieste, Italy, as part of the MDMC Master's programme at SISSA. 

This project was funded by the European Union - NextGenerationEU via:
* **NFFA-DI** (cod. IR0000015)
* **EFC** (cod. SSU2024-00002)
  
---