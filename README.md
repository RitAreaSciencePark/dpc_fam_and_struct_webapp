# Web Application for DPCfam and DPCstruct Data Exploration

![Status](https://img.shields.io/badge/Status-Under%20Development-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp)

Hi! Thank you for visiting our repository. This is a Django project designed to facilitate the exploration of proteins at the domain level. We work with the [DPCFam](https://zenodo.org/records/6900559) and [DPCStruct](https://zenodo.org/records/13334296) datasets, which provide clusterings of protein sequences and protein structures, respectively, with the purpose of classifying protein domains at large scale.

| Dataset | Description | Zenodo |
|---------|-------------|--------|
| **DPCFam** | Sequence-based domain clusters | [![DOI](https://img.shields.io/badge/Zenodo-DPCFam-blue?style=flat-square&logo=zenodo)](https://zenodo.org/records/6900559) |
| **DPCStruct** | Structure-based domain clusters | [![DOI](https://img.shields.io/badge/Zenodo-DPCStruct-blue?style=flat-square&logo=zenodo)](https://zenodo.org/records/13334296) |

The project currently consists of two applications `dpcfam` and `dpcstruct` corresponding to the two datasets presented above. To reproduce the current state of this project (which is under development), please follow the steps below.
---
## Table of Contents

* [1. Prerequisites](#1-prerequisites)
* [2. Clone the Repository](#2-clone-the-repository)
* [3. Installation](#3-installation)
* [4. Database Initialization](#4-database-initialization)
  * [4.1 Create User and Database (only once)](#41-create-user-and-database-only-once)
  * [4.2 Create Tables and Indexes, then Populate Tables from CSV Files](#42-create-tables-and-indexes-then-populate-tables-from-csv-files)
    * [I. Application I: dpcfam](#i-application-i--dpcfam-almost-done)
    * [II. Application II: dpcstruct](#ii-application-ii--dpcstruct-under-development)
* [5. Migrations](#5-migrations)
* [6. Run the Server](#6-run-the-server)
* [7. Usage](#7-usage)
* [References](#references)
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
* **CSV Data Files**: Available upon request; place them in `static/dataframes/`.
* **Static files**: To enable the "Downloads" feature and serve domains data, organize the `static/` directory as follows:

```text
static/
├── downloads/
│   ├── dpcfam/
│   │   ├── alphafolddb_reps.zip
│   │   ├── dpcfamb_dataset.zip
│   │   ├── dpcfam_full_seeds.zip
│   │   ├── dpcfam_hmm_profiles.zip
│   │   └── dpcfam_msa_profiles.zip
│   └── dpcstruct/
│       ├── dpcstruct_reps_pdbs.tar.gz
│       └── dpcstruct_reps_seqs.tar.gz
└── production_files/
    ├── dpcfam/
    │   ├── metaclusters_fasta/       # MCID.fasta files
    │   ├── metaclusters_hmms/        # MCID.hmm files
    │   └── metaclusters_msas_cdhit/  # MCID.msa files
    └── dpcstruct/
        ├── dpcstruct_reps_seqs/           # MCID.fasta files (representatives only)
        ├── dpcstruct_reps_pdbs_zipped/    # MCID_pdb.zip files (representatives only)
        └── dpcstruct_reps_pdbs/           # MCID.pdb files (representatives only)
```

### 2. Clone the Repository

![GitHub](https://img.shields.io/badge/GitHub-Clone-181717?style=flat-square&logo=github&logoColor=white)

If this is your first time, clone the project:
```bash
git clone https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp
cd dpc_fam_and_struct_webapp
```
Otherwise, pull the latest changes:
```bash
cd dpc_fam_and_struct_webapp
git pull
```

### 3. Installation

![pip](https://img.shields.io/badge/pip-Package%20Manager-3775A9?style=flat-square&logo=pypi&logoColor=white)
![venv](https://img.shields.io/badge/venv-Virtual%20Environment-3776AB?style=flat-square&logo=python&logoColor=white)

1. Create (for first-time users) and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Database Initialization

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.11-336791?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Scripts-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)

Start the PostgreSQL service:
```bash
sudo service postgresql start
```

#### 4.1 Create User and Database (only once)

Use the provided script to set up the PostgreSQL user and database:
```bash
sudo -u postgres psql -f static/scripts/create_a_user_and_a_database.sql
```

#### 4.2 Create Tables and Indexes, then Populate Tables from CSV Files

**I. Application I : dpcfam (almost done)**

1. Run the following script to create dpcfam tables and indexes :
   ```bash
   PGPASSWORD="EmmaPSQL2026" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcfam/create_dpcfam_tables.sql
   ```
2. Run the following script to populate dpcfam tables by loading data from CSV files (It will take a while; please wait until the process is completed!):
   ```bash
   PGPASSWORD="EmmaPSQL2026" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcfam/populate_dpcfam_tables.sql
   ```

**II. Application II : dpcstruct (under development)**

1. Run the following script to create dpcstruct tables and indexes:
   ```bash
   PGPASSWORD="EmmaPSQL2026" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcstruct/create_dpcstruct_tables.sql
   ```
2. Run the following script to populate dpcstruct tables by loading data from CSV files:
   ```bash
   PGPASSWORD="EmmaPSQL2026" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcstruct/populate_dpcstruct_tables.sql
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
```
http://127.0.0.1:8000/
```

**Note:** Congratulations, you made it! To stop the server, use `Ctrl+C`. To stop PostgreSQL, run `sudo service postgresql stop`. Once the database is successfully populated, you may delete the CSV files (`static/dataframes/`) to save space. For any feedback, reach out to us via any address on our profile. More features are coming soon!

---

### References

If you use this project or the associated datasets, please cite:

1. Barone, F., Laio, A., Punta, M., Cozzini, S., Ansuini, A., & Cazzaniga, A. (2025). Unsupervised domain classification of AlphaFold2-predicted protein structures. *PRX Life*, *3*(2), 023009. [https://doi.org/10.1103/PRXLife.3.023009](https://doi.org/10.1103/PRXLife.3.023009)

2. Russo, E. T., Barone, F., Bateman, A., Cozzini, S., Punta, M., & Laio, A. (2022). DPCfam: Unsupervised protein family classification by density peak clustering of large sequence datasets. *PLOS Computational Biology*, *18*(10), e1010610. [https://doi.org/10.1371/journal.pcbi.1010610](https://doi.org/10.1371/journal.pcbi.1010610)

<details>
<summary>BibTeX</summary>

```bibtex
@article{barone2025unsupervised,
  title={Unsupervised domain classification of AlphaFold2-predicted protein structures},
  author={Barone, Federico and Laio, Alessandro and Punta, Marco and Cozzini, Stefano and Ansuini, Alessio and Cazzaniga, Alberto},
  journal={PRX Life},
  volume={3},
  number={2},
  pages={023009},
  year={2025},
  publisher={APS}
}

@article{russo2022dpcfam,
  title={Dpcfam: unsupervised protein family classification by density peak clustering of large sequence datasets},
  author={Russo, Elena Tea and Barone, Federico and Bateman, Alex and Cozzini, Stefano and Punta, Marco and Laio, Alessandro},
  journal={PLOS Computational Biology},
  volume={18},
  number={10},
  pages={e1010610},
  year={2022},
  publisher={Public Library of Science San Francisco, CA USA}
}
```

</details>
