## How to run (on Ubuntu)?: 

You may follow the steps below, although our code is still under development:

1. **Clone the repository**:

    `git clone https://github.com/emmanuelnyandukagarabi/dpc_fam_and_struct_webapp`

2. **Change directory**:

    `cd dpc_fam_and_struct_webapp`

3. **Set up a virtual environment**:

    - Create and activate

        `python3 -m venv .area_internship_venv` (if not yet existent)

        `source .area_internship_venv/bin/activate`

    - Install dependencies:

    `pip install -r requirements.txt`

4. **Run the development server**:

    `python3 manage.py runserver`

5. **Open your web browser(preferably Chrome) and visit**:

    `http://127.0.0.1:8000/`

## Data Organization (Static Files)

To enable the "Downloads" feature and serve sequence data, the `static/` directory must be organized as follows:

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