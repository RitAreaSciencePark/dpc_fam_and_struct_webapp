# Web Application for DPCfam and DPCstruct Data Exploration

Hi! Thank you for visiting our repository. This is a Django project designed to facilitate the exploration of proteins at the domain level. We are basically working with the [DPCFam](https://zenodo.org/records/6900559) and [DPCStruct](https://zenodo.org/records/13334296) datasets, which provide clusterizations of protein sequences and protein structures, respectively, with the purpose of classifying protein domains at large scale. 

If you want to reproduce this project, please follow the steps below:

### 1. Prerequisites

Our development environment uses:
* [Ubuntu](https://ubuntu.com/) 24.04.3 LTS
* [Python](https://www.python.org/) 3.12.3
* [Visual Studio Code](https://code.visualstudio.com/) 1.109.3
* [Git](https://git-scm.com/) 2.43.0
* [PostgreSQL](https://www.postgresql.org/) 16.11
* **CSV Data Files**: Available upon request; in `static/dataframes/dpcfam/`.
* **Static files**: To enable the "Downloads" feature and serve sequence data, organize the `static/` directory as follows:

```text
static/
├── downloads/
│   └── dpcfam/
│       ├── alphafolddb_reps.zip
│       ├── dpcfamb_dataset.zip
│       ├── dpcfam_full_seeds.zip
│       ├── dpcfam_hmm_profiles.zip
│       └── dpcfam_msa_profiles.zip
└── production_files/
    ├── dpcfam/
    │   ├── metaclusters_fasta/       # .fasta files
    │   ├── metaclusters_hmms/        # .hmm files
    │   └── metaclusters_msas_cdhit/  # .msa files
    └── dpcstruct/
```

### 2. Clone the Repository
If it's your first time, clone the project:
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
1. Create (for first-time users) and activate a virtual environment:
   ```bash
   python3 -m venv .area_internship_venv
   source .area_internship_venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Database Initialization
1. **Create User and Database** (only once):
   Use the provided script to set up the PostgreSQL user and database:
```bash
sudo -u postgres psql -f static/scripts/dpcfam/create_a_user_and_a_database.sql
```

2. **Create Tables and Indexes**:
   Run the schema setup script:
   ```bash
   PGPASSWORD="***REMOVED***" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcfam/create_dpcfam_tables.sql
   ```
3. **Populate Tables**:
   Load the data from  CSV files into the database:
  ```bash
   PGPASSWORD="***REMOVED***" psql -U enyanduk -h localhost -d dpcfam_mcs_db -f static/scripts/dpcfam/populate_dpcfam_tables.sql
   ```

### 5. Run the server
```bash
python3 manage.py runserver
```

### 6. Usage
Visit the following URL in your web browser ( [Chrome](https://www.google.com/chrome/) is my friend!):
 ```bash
    http://127.0.0.1:8000/
 ```

**Note**: Grazie, you made it!. To stop the server, use `CTRL+C`. To stop PostgreSQL, run `sudo service postgresql stop`. Once the database is successfully populated, you may delete the CSV files(`static/dataframes/`) to save space. Other steps are comming soon! .
