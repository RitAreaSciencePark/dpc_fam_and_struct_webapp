# Web Application for DPCfam and DPCstruct Data Exploration

![Status](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp)

Hi! Thank you for visiting our repository. In this project we are building **DPCexplorer** : a Django project designed to facilitate the interactive exploration of DPCfam and DPCstruct protein domain classifications. We work with the [DPCFam](https://zenodo.org/records/6900559) and [DPCStruct](https://zenodo.org/records/13334296) datasets, which provide clusterings of protein sequences and protein structures, respectively, at the domain level.

| Dataset | Description | Zenodo |
|---------|-------------|--------|
| **DPCFam** | Sequence-based domain clusters | [![DOI](https://img.shields.io/badge/Zenodo-DPCFam-blue?style=flat-square&logo=zenodo)](https://zenodo.org/records/6900559) |
| **DPCStruct** | Structure-based domain clusters | [![DOI](https://img.shields.io/badge/Zenodo-DPCStruct-blue?style=flat-square&logo=zenodo)](https://zenodo.org/records/13334296) |

Proteins are automatically grouped into families called `metaclusters`. Some of these families are equivalent to manually curated families in databases like `Pfam`. Most importantly, the pipelines have flagged out some potential new families, which we display as `UNKNOWN` on this portal. If you have some hints about their annotation, your feedback will be highly appreciated!


The project currently consists of three django-applications: `dpc` (core: shared registry), `dpcfam` (sequence-based metaclusters), and `dpcstruct` (structure-based metaclusters). 

To reproduce the current state of this project, we have defined a streamlined process. Whether you are a **new user** setting up the environment from scratch, or a **returning user** just updating the latest code, follow the instructions tailored to you below.

---

## 🎯 Reproducibility: New Users vs. Returning Users

### Option A: New Users (Full Setup)

If this is your first time setting this up on your machine, follow **all steps** from 1 to 7 below in chronological order. This will clone the repository, install Python and system dependencies, download the datasets using the automated setup script, initialize the database, and explore the web application.

### Option B: Returning Users (Updates)

If you already have a functional environment and simply `pulled` the latest commits:

1. Activate your virtual environment: `source .venv/bin/activate`
2. Install any new requirements: `pip install -r requirements.txt`
3. Execute any new database migrations: `python3 manage.py migrate`
4. Run the data setup script again to pull any missing/updated assets: `bash setup_dpcexporer_data.sh` *(Note: The script is idempotent and will skip already-downloaded files, saving time!)*
5. Run the server: `python3 manage.py runserver`

---

## Table of Contents

- [Web Application for DPCfam and DPCstruct Data Exploration](#web-application-for-dpcfam-and-dpcstruct-data-exploration)
  - [🎯 Reproducibility: New Users vs. Returning Users](#-reproducibility-new-users-vs-returning-users)
    - [Option A: New Users (Full Setup)](#option-a-new-users-full-setup)
    - [Option B: Returning Users (Updates)](#option-b-returning-users-updates)
  - [Table of Contents](#table-of-contents)
    - [1. Prerequisites](#1-prerequisites)
    - [2. Clone the Repository](#2-clone-the-repository)
    - [3. Installation](#3-installation)
    - [4. Database Initialization](#4-database-initialization)
      - [4.1 Create User and Database](#41-create-user-and-database)
      - [4.2 Create Tables and Indexes, then Populate Tables from CSV Files](#42-create-tables-and-indexes-then-populate-tables-from-csv-files)
        - [A. Application 1: dpc (Core Registry)](#a-application-1-dpc-core-registry)
        - [B. Application 2: dpcfam (Sequence-Based Metaclusters)](#b-application-2-dpcfam-sequence-based-metaclusters)
        - [C. Application 3: dpcstruct (Structure-Based Metaclusters)](#c-application-3-dpcstruct-structure-based-metaclusters)
    - [5. Migrations](#5-migrations)
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

Our development environment uses:

* [Ubuntu](https://ubuntu.com/) 24.04.3 LTS
* [Python](https://www.python.org/) 3.12.3
* [Visual Studio Code](https://code.visualstudio.com/) 1.109.3
* [Git](https://git-scm.com/) 2.43.0
* [PostgreSQL](https://www.postgresql.org/) 16.11

DPCexplorer expects the following file tree layout to work completely:

```text
static/
├── dataframes/                                 # PostgreSQL-ready CSV files for DPCexplorer
│   ├── dpc/                                    # CSV files for the core dpc application
│   ├── dpcfam/                                 # CSV files for the dpcfam application
│   └── dpcstruct/                              # CSV files for the dpcstruct application
:
├── downloads/                                  # DPCexplorer global downloads directory
│   ├── dpcfam/
│   │   ├── dpcfam_mcid_seeds.tar.gz            # Seed sequences for each MCID, in the format MCID.fasta
│   │   ├── dpcfam_mcid_msas.tar.gz             # MSA for each MCID, in the format MCID_msa.fasta
│   │   ├── dpcfam_mcid_hmms.tar.gz             # HMM for each MCID, in the format MCID.hmm
│   │   └── dpcfam_all_metaclusters_hmms.tar.gz # All metacluster HMM profiles : 2 .hmm files, one for standard DPCfam and one for DPCfamB
│   └── dpcstruct/
│       ├── dpcstruct_mcid_seeds.tar.gz         # Representative seed sequences for each MCID, in the format MCID.fasta
│       └── dpcstruct_mcid_pdbs.tar.gz          # Representative PDB files for each MCID, in the format MCID_pdb.zip 
:
└── production_files/                           # DPCexplorer local downloads files (Downlaodable per MCID)
    ├── dpcfam/
    │   ├── metaclusters_fasta/                  # MCID.fasta files
    │   ├── metaclusters_hmms/                   # MCID.hmm files
    │   └── metaclusters_cdhit_msas/             # MCID_msa.fasta files
    └── dpcstruct/
        ├── dpcstruct_reps_seqs/                 # MCID.fasta files
        ├── dpcstruct_reps_pdbs_zipped/          # MCID_pdb.zip files
        └── dpcstruct_reps_pdbs/                 # MCID/.pdb files  -> PDBe Mol* viewer
```

### 2. Clone the Repository

![GitHub](https://img.shields.io/badge/GitHub-Clone-181717?style=flat-square&logo=github&logoColor=white)

Clone the project:

```bash
git clone https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp
cd dpc_fam_and_struct_webapp
```

### 3. Installation

![pip](https://img.shields.io/badge/pip-Package%20Manager-3775A9?style=flat-square&logo=pypi&logoColor=white)
![venv](https://img.shields.io/badge/venv-Virtual%20Environment-3776AB?style=flat-square&logo=python&logoColor=white)

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Generate a secure, random Django Secret Key and Database Password to automatically create your `.env` file in one command:
   ```bash
   python3 -c "import secrets; from django.core.management.utils import get_random_secret_key; print(f'DJANGO_SECRET_KEY={get_random_secret_key()}\nDEBUG=True\nALLOWED_HOSTS=127.0.0.1,localhost\nDB_NAME=dpc_db\nDB_USER=dpc_admin\nDB_PASSWORD={secrets.token_urlsafe(16)}\nDB_HOST=localhost\nDB_PORT=5432')" > .env
   ```
   *Note: This command magically secures your environment so you do not need to manually configure or type any passwords below!*

 In order to build automatically DPCexplorer tree as shown above, please, run the following bash script (located at the root of the repository):
 
 > **Note:** Running this script for the first time will take a while as it downloads large datasets from Zenodo, you may grab some coffee!. You are expected to have at least 50 GB of free disk space and a stable internet connection. If the script is interrupted, running it again will resume where it left off!

 ```bash
bash setup_dpcexplorer_data.sh
```


### 4. Database Initialization

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.11-336791?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Scripts-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)

Start the PostgreSQL service:

```bash
sudo service postgresql start
```

#### 4.1 Create User and Database

We securely extract the credentials you generated in your `.env` file to set up PostgreSQL effortlessly. Run the following:

```bash
export $(grep -v '^#' .env | xargs)
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '${DB_PASSWORD}'; CREATE DATABASE $DB_NAME OWNER $DB_USER;"
```

#### 4.2 Create Tables and Indexes, then Populate Tables from CSV Files

##### A. Application 1: dpc (Core Registry)

1. Run the following script to create dpc tables and indexes:

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpc/create_dpc_tables.sql
   ```

2. Run the following script to populate dpc tables by loading data from CSV files:

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpc/populate_dpc_tables.sql
   ```

##### B. Application 2: dpcfam (Sequence-Based Metaclusters)

1. Run the following script to create dpcfam tables and indexes:

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcfam/create_dpcfam_tables.sql
   ```

2. Run the following script to populate dpcfam tables by loading data from CSV files. (This will take a while; please wait until the process completes!):

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcfam/populate_dpcfam_tables.sql
   ```

##### C. Application 3: dpcstruct (Structure-Based Metaclusters)

1. Run the following script to create dpcstruct tables and indexes:

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcstruct/create_dpcstruct_tables.sql
   ```

2. Run the following script to populate dpcstruct tables by loading data from CSV files:

   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f static/scripts/dpcstruct/populate_dpcstruct_tables.sql
   ```

### 5. Migrations

![Django](https://img.shields.io/badge/Django-Migrations-092E20?style=flat-square&logo=django&logoColor=white)

We have already created and pushed all migrations in this project. Optionally, you may run:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 6. Run the Server

![Django](https://img.shields.io/badge/Django-runserver-092E20?style=flat-square&logo=django&logoColor=white)
![localhost](https://img.shields.io/badge/localhost-8000-blue?style=flat-square)

```bash
python3 manage.py runserver
```

### 7. Usage

![Chrome](https://img.shields.io/badge/Google%20Chrome-Recommended-4285F4?style=flat-square&logo=googlechrome&logoColor=white)

Visit the following URL in your web browser ([Chrome](https://www.google.com/chrome/) is my friend!):

```bash
http://127.0.0.1:8000/
```

**Note:** Congratulations, you made it! To stop the server, press `Ctrl+C`. To stop PostgreSQL, run `sudo service postgresql stop`. Once the database is successfully populated, you may safely delete the CSV files located in `static/dataframes/` to save disk space. If you have any feedback or encounter issues, please reach out to us via any contact address on our GitHub profile. More features are coming soon!

*Thank you for trying out this tool. Your feedback is highly appreciated!*

---

### References

If you use this project or the associated datasets, please cite:

1. Nyandu Kagarabi, E., Piomponi, V., & Saadat, E. (2026). Preprocessed Datasets for Interactive Exploration of DPCfam and DPCstruct Protein Domain Classifications (1.0.0) [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.20159208](https://doi.org/10.5281/zenodo.20159208)

2. Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2025). Unsupervised domain classification of AlphaFold2-predicted protein structures. *PRX Life*, *3*(2), 023009. [https://doi.org/10.1103/PRXLife.3.023009](https://doi.org/10.1103/PRXLife.3.023009)

3. Russo, E. T., Barone, F., Bateman, A., Cozzini, S., Punta, M., & Laio, A. (2022). DPCfam: Unsupervised protein family classification by density peak clustering of large sequence datasets. *PLOS Computational Biology*, *18*(10), e1010610. [https://doi.org/10.1371/journal.pcbi.1010610](https://doi.org/10.1371/journal.pcbi.1010610)