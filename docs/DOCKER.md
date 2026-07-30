# DPCexplorer Container Guide

DPCexplorer runs as one Django/Gunicorn application container.

PostgreSQL and the biological datasets remain outside the image:

- PostgreSQL runs as an external service.
- Biological data is mounted read-only at `/data`.
- Normal web assets are included in the image and served by WhiteNoise.
- Application logs are written to stdout.

## Prerequisites

You need:

- Docker with the Compose plugin
- A configured `.env` file
- A populated PostgreSQL database
- `static/downloads/`
- `static/production_files/`

Check Docker:

```bash
docker version
docker compose version
```

## Start PostgreSQL

```bash
sudo service postgresql start
pg_isready -h localhost -p 5432
```

PostgreSQL should report that it is accepting connections.

## Build the application

```bash
docker compose build
```

The image does not contain PostgreSQL, database credentials, or biological
datasets.

## Start the application

```bash
docker compose up --detach
docker compose ps
```

Follow the logs:

```bash
docker compose logs --follow web
```

Open <http://127.0.0.1:8000/>.

## Run the automated test

The test builds and starts the image, checks its security restrictions, tests
the application, and removes the test container:

```bash
./scripts/test-container.sh
```

To test an application that is already running:

```bash
BASE_URL=http://127.0.0.1:8000 ./scripts/smoke-test.sh
```

## Gunicorn command

The container runs:

```bash
gunicorn dpc_fam_and_struct_webapp.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --graceful-timeout 30 \
  --worker-tmp-dir /tmp \
  --access-logfile - \
  --error-logfile -
```

## Security controls

The application container:

- Runs as non-root UID `10001`
- Uses a read-only root filesystem
- Mounts biological data read-only
- Uses an ephemeral writable `/tmp`
- Drops all Linux capabilities
- Disables privilege escalation

## Stop the application

```bash
docker compose down
```

This removes the application container. It does not stop PostgreSQL or delete
biological data.

## Troubleshooting

Check PostgreSQL:

```bash
pg_isready -h localhost -p 5432
```

Check the container:

```bash
docker compose ps
docker compose logs --tail=200 web
```

Check application health:

```bash
curl -i http://127.0.0.1:8000/health/live
curl -i http://127.0.0.1:8000/health/ready
```

Rebuild after code or dependency changes:

```bash
docker compose build --no-cache
docker compose up --detach
```

## Kubernetes note

The Compose file uses host networking only for local Linux testing. Kubernetes
will use normal pod networking and the PostgreSQL Service DNS name.
