"""Start and measure a small PostgreSQL teaching database using installed PostgreSQL."""
import json
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

import psycopg2
from _environment import ENV_FILE, ROOT, environment

# Same schema and synthetic data as workshop/compose.yaml initializes in Docker.
SQL_FILES = [
    ROOT / 'static/scripts/dpc/create_dpc_tables.sql',
    ROOT / 'static/scripts/dpcfam/create_dpcfam_tables.sql',
    ROOT / 'static/scripts/dpcstruct/create_dpcstruct_tables.sql',
    ROOT / 'workshop/seed.sql',
]


def database_state(env):
    """Return (seeded, public table count); do not overwrite an existing database."""
    with psycopg2.connect(dbname=env['DB_NAME'], user=env['DB_USER'],
                          password=env['DB_PASSWORD'], host=env['DB_HOST'], port=env['DB_PORT'],
                          connect_timeout=10) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.workshop_dataset_info')")
            seeded = cursor.fetchone()[0] is not None
            cursor.execute("SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
            table_count = cursor.fetchone()[0]
            if seeded:
                cursor.execute('SELECT version FROM public.workshop_dataset_info')
                if cursor.fetchall() != [(1,)]:
                    raise SystemExit('Unexpected workshop dataset version; stopping.')
    return seeded, table_count


def main():
    if not shutil.which('psql'):
        raise SystemExit('PostgreSQL client psql is required. See workshop/README.md for prerequisites.')
    # Check credentials and database access before starting a timer.
    if not ENV_FILE.exists():
        raise SystemExit('Create .env.workshop with the existing PostgreSQL database credentials first.')
    env = environment()
    required = ('DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT')
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise SystemExit('Missing database settings: ' + ', '.join(missing))
    if env['DB_NAME'] in ('postgres', 'template0', 'template1'):
        raise SystemExit('Refusing to initialize a PostgreSQL system database.')
    seeded, table_count = database_state(env)
    if not seeded and table_count:
        raise SystemExit('Database is not empty. Use a NEW, dedicated workshop database.')
    for script in SQL_FILES:
        if not script.is_file():
            raise SystemExit(f'Missing SQL file: {script}')
    report = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'dataset': 'synthetic-v1', 'phases_seconds': {},
        'scope': 'Local database seed, Django migrations and data verification; excludes PostgreSQL and Python installation.',
        'limits': 'Local PostgreSQL resource limits are managed outside this script.',
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'database_seeded_before_setup': seeded,
    }
    sql_command = [
        'psql', '-X', '-w', '-v', 'ON_ERROR_STOP=1',
        '-h', env['DB_HOST'], '-p', env['DB_PORT'],
        '-U', env['DB_USER'], '-d', env['DB_NAME'],
    ]
    for script in SQL_FILES:
        sql_command += ['-f', str(script)]
    started = time.perf_counter()
    for name, command in [
        ('database_schema_and_seed', sql_command),
        ('migrations', [sys.executable, str(ROOT / 'manage.py'), 'migrate', '--noinput']),
        ('django_check', [sys.executable, str(ROOT / 'manage.py'), 'check']),
        ('dataset_verification', [sys.executable, str(ROOT / 'workshop/verify.py')]),
    ]:
        print(f'\n{name}', flush=True)
        phase_start = time.perf_counter()
        if name == 'database_schema_and_seed' and seeded:
            print('Workshop data already present; skipping SQL initialization.', flush=True)
        else:
            command_env = {**env, 'PGPASSWORD': env['DB_PASSWORD']} if name == 'database_schema_and_seed' else env
            subprocess.run(command, cwd=ROOT, env=command_env, check=True)
        report['phases_seconds'][name] = round(time.perf_counter() - phase_start, 3)
    report['total_seconds'] = round(time.perf_counter() - started, 3)
    # Measure the same database size as the Docker setup (no Docker-only metrics).
    with psycopg2.connect(dbname=env['DB_NAME'], user=env['DB_USER'],
                          password=env['DB_PASSWORD'], host=env['DB_HOST'], port=env['DB_PORT']) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_database_size(current_database())')
            report['database_bytes'] = cursor.fetchone()[0]
            cursor.execute('SHOW server_version')
            report['postgres_version'] = cursor.fetchone()[0]
    logs = ROOT / 'logs'
    logs.mkdir(exist_ok=True)
    destination = logs / ('workshop-small-local-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    print(f'\nReport saved: {destination}')
    print('Start the app: python workshop/manage.py runserver')

if __name__ == '__main__':
    try:
        main()
    except psycopg2.Error as error:
        raise SystemExit(f'PostgreSQL error: {error}') from error
    except subprocess.CalledProcessError as error:
        raise SystemExit(f'Setup stopped (exit {error.returncode}). Review the error above; no other database was reset.')
