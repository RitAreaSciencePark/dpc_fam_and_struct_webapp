# Small API workshop database

Use this setup for the four-hour Django REST Framework workshop instead of
downloading the full scientific datasets. It reuses the application's PostgreSQL
schema and all existing models, views, and serializers. The three exercise
endpoints are left for students to write.

**All records supplied here are synthetic teaching data.** Protein IDs beginning
with `WS`, sequences, confidence scores, cluster properties and Pfam associations
are invented. They must not be interpreted as biological findings. For a workshop
requiring real observations, an instructor should provide a curated, relationally
complete subset exported from the scientific database instead.

## 0. Check your tools

This guide is the complete setup path for the API workshop. Follow it instead
of the root README's full scientific-data installation. Do not run
`setup_dpcexplorer_data.sh` for this workshop.

You need Python **3.12 or newer**, Git, and Docker Engine or Docker Desktop with
Docker Compose. Docker must be running and your user must be able to access it.
Check these before the workshop:

```bash
python3 --version
git --version
docker compose version
docker info --format '{{.ServerVersion}}'
```

On Ubuntu, a missing virtual-environment module can be installed with
`sudo apt install python3-venv`. If Docker is missing, follow the
[official Ubuntu installation guide](https://docs.docker.com/engine/install/ubuntu/)
and its [user-access instructions](https://docs.docker.com/engine/install/linux-postinstall/).
For Windows or macOS, install [Docker Desktop](https://docs.docker.com/desktop/).
Complete any installation and login/restart steps before class. An Ubuntu or WSL
terminal is used for the commands below. On macOS, the same shell commands work
once `python3` is Python 3.12+; on Windows, use a WSL terminal with Docker Desktop's
WSL integration enabled.

Native PostgreSQL, database credentials from the instructor, and an existing
`.env` file are not required.

## 1. Clone the workshop branch

The workshop is on its own branch; the application on `main` is unchanged.
Use a new folder for this run:

```bash
git clone --branch workshop/student-setup https://github.com/RitAreaSciencePark/dpc_fam_and_struct_webapp.git dpc_workshop_student
cd dpc_workshop_student
```

Confirm that `manage.py`, `api/urls.py`, and `dpcfam/models.py` are present:

```bash
ls manage.py api/urls.py dpcfam/models.py
```

## 2. Install the workshop's Python packages

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r workshop/requirements.txt
```

This installs the app's runtime dependencies, leaving out optional deployment
and research/documentation tools. `(.venv)` should appear in your prompt.

## 3. Create and verify the small database

```bash
python workshop/setup.py
```

The script generates credentials, starts a dedicated PostgreSQL container, loads
the included teaching dataset, runs Django migrations, and verifies the existing
API and core web pages. It prints `Verified:` and saves a measurement report on
success. It does not require an instructor database or solve the exercises.

## 4. Start Django

```bash
python workshop/manage.py runserver
```

Open <http://127.0.0.1:8000/>. Leave this terminal running, and open a second
terminal in `dpc_workshop_student` for requests. Run all later Django commands as
`python workshop/manage.py <command>` so that they use this database. For example:

```bash
python workshop/manage.py check
python workshop/manage.py shell
```

The helper creates a private, git-ignored `.env.workshop` and a separate database
on `127.0.0.1:55432`. The normal `.env`, native PostgreSQL databases, existing
Docker applications and their volumes are left as they are. If port 55432 is
already occupied, change `DB_PORT` in `.env.workshop` before starting.

If port 8000 is occupied, start Django with
`python workshop/manage.py runserver 8001`, then use port 8001 in your requests.
Do not launch the root `manage.py` directly during the workshop; the wrapper
selects `.env.workshop` so Django connects to the teaching database.

## 5. Check the existing API, then start the exercises

In the second terminal:

```bash
curl -i http://127.0.0.1:8000/api/dpcfam/mcs/MC1/
curl -i http://127.0.0.1:8000/api/dpcstruct/mcs/MC5/
curl -i 'http://127.0.0.1:8000/api/dpcfam/mcs/MC1/members/?page_size=3'
```

All three should return HTTP 200 and JSON. For the members request, look for
`count`, `next`, and three entries in `results`.

Now continue with the PDF's first coding exercise (the DPCfam summary). Use
`WSDEMO0001` as the known protein ID for the protein-domain exercise and
`WSMISSING` as a missing ID. For the structural search, use the PDF's pLDDT and
size thresholds. Add your exercise code in the normal `api/` files. No workshop
endpoint implementations are supplied in this setup.

## Resource use and measurements

The database runs with a 256 MiB RAM cap and a one-CPU cap, including its normal
initialization. These are resource limits, not promised measurements. The first
run may also download the PostgreSQL Docker image; later runs reuse it. There are
no Zenodo dataset downloads or large CSV imports. Python packages and Docker's
installation take additional space and setup time.

Each setup run saves timing and resource measurements in
`logs/workshop-small-<timestamp>.json`: phase duration, database bytes, PostgreSQL
data-directory size, shared image size, and a container memory snapshot. The
memory snapshot is not a measured peak. A first run with a cached Docker image
does not measure image download time. Setup can be repeated without deleting
student data; record a fresh-volume run separately from a repeated run.
Reports identify whether the PostgreSQL image and database volume existed before
setup, and record the Python version and Docker image ID.

The generated logs, secrets, virtual environment, and database volume are local
artifacts. The files under `workshop/` are sufficient to distribute the dataset;
do not publish `.env.workshop` or a private database dump.

One verified run on the development laptop, using a new database volume and an
already cached PostgreSQL image, measured:

| Measurement | Result |
| --- | --- |
| Startup, seed, migrations, Django check and verification | 13.4 seconds |
| Application database | 9.3 MiB |
| Complete PostgreSQL data directory, including its other databases and WAL | 47.6 MiB |
| Container RAM snapshot after setup | 37.8 MiB |
| Shared PostgreSQL image, uncompressed | 280.7 MiB |

These are observed values, not requirements or guaranteed student timings. This
run excludes Docker installation, Python installation, image download, and
starting the Django development server. The image is shared across containers;
it is not additional storage for each student database on the same machine.

## Data coverage for the exercise prompts

Only the task pages of `Django_Workshop_Second_Try.pdf` informed this dataset.
Solution pages are not needed.

| Task | Available data |
| --- | --- |
| Inspect existing API | DPCfam `MC1`, DPCstruct `MC5`, and multiple pages of members |
| Summarize a cluster | 40 DPCfam clusters; nullable and `UNKNOWN` Pfam labels; `MC999999` is absent |
| Filter structural clusters | 40 clusters with varied sizes; pLDDT 0, 79.9, 80, 100, and NULL; more than 10 records meet pLDDT >= 80 and size >= 10 |
| Protein domains | `WSDEMO0001` has 130 entries in each of the three mapping tables, so the 100-entry limit can be checked |
| Empty lists | `WSEMPTY0001` exists with no mappings; `WSFAMONLY`, `WSSTRUCTONLY`, and `WSPFAMONLY` have one mapping type each |
| Missing protein | `WSMISSING` is absent |

The dataset has 1,005 protein records. Cluster sizes count their teaching member
rows. Repeat-domain examples are artificial and intentionally simple. Foreign
keys use the original schema. CATH and SCOP have five synthetic examples each;
the AlphaFold representative table exists but has no records.

Recheck the data and existing application:

```bash
python workshop/verify.py
```

This validates existing API behavior and dataset coverage, not the student-written
workshop endpoints. Students should still run the final status-code checks in the
PDF after implementing their endpoints.

Protein structure files, downloadable FASTA/HMM/MSA archives, and 3D rendering
assets are outside this API workshop setup. Download links requiring these files
will return 404, and the full production `/health/ready` endpoint will report
missing data files. This does not prevent the database API exercises.

## Stop or reset only this teaching database

Stop and keep its data:

```bash
docker compose --project-name dpcexplorer-workshop --env-file .env.workshop -f workshop/compose.yaml down
```

For a fresh student run, delete its dedicated volume and initialize again:

```bash
docker compose --project-name dpcexplorer-workshop --env-file .env.workshop -f workshop/compose.yaml down --volumes
python workshop/setup.py
```

Initialization SQL runs only on an empty PostgreSQL data directory. Changing
`seed.sql` requires resetting this dedicated volume to apply the new dataset.
See the [official PostgreSQL image documentation](https://hub.docker.com/_/postgres).

For classroom delivery, preinstall Python dependencies and Docker, and cache the
PostgreSQL image before the session. Give students this folder alongside the
application code. Keep the full scientific deployment as an optional follow-up.
