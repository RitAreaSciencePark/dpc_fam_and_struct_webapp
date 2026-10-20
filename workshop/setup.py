"""Start and measure a small, isolated PostgreSQL teaching database."""
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

from _environment import ENV_FILE, ROOT, compose_command, environment


def main():
    if not shutil.which('docker'):
        raise SystemExit('Docker with Compose is required. See workshop/README.md for prerequisites.')
    # Check daemon access before creating files or starting a timer.
    subprocess.run(['docker', 'info', '--format', '{{.ServerVersion}}'], check=True)
    subprocess.run(['docker', 'compose', 'version'], check=True)
    if not ENV_FILE.exists():
        values = {
            'DJANGO_SECRET_KEY': secrets.token_urlsafe(64), 'DEBUG': 'True',
            'ALLOWED_HOSTS': '127.0.0.1,localhost',
            'DB_NAME': 'dpcexplorer_workshop', 'DB_USER': 'workshop',
            'DB_PASSWORD': secrets.token_urlsafe(24),
            'DB_HOST': '127.0.0.1', 'DB_PORT': '55432',
            'DPCEXPLORER_ADMIN_WRITABLE': 'False',
        }
        descriptor = os.open(ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w') as file:
            file.write(''.join(f'{key}={value}\n' for key, value in values.items()))
    env = environment()
    image_cached = subprocess.run(
        ['docker', 'image', 'inspect', 'postgres:16-alpine'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    volume_existed = subprocess.run(
        ['docker', 'volume', 'inspect', 'dpcexplorer-workshop_database'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    report = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'dataset': 'synthetic-v1', 'phases_seconds': {},
        'scope': 'Database startup, seed, Django migrations and data verification; excludes Python installation.',
        'limits': 'Database container: 256 MiB RAM, 1 CPU; these are caps, not measured peaks.',
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'image_cached_before_setup': image_cached,
        'database_volume_existed_before_setup': volume_existed,
    }
    started = time.perf_counter()
    for name, command in [
        ('database_start_and_seed', compose_command() + ['up', '-d', '--wait', '--wait-timeout', '120']),
        ('migrations', [sys.executable, str(ROOT / 'manage.py'), 'migrate', '--noinput']),
        ('django_check', [sys.executable, str(ROOT / 'manage.py'), 'check']),
        ('dataset_verification', [sys.executable, str(ROOT / 'workshop/verify.py')]),
    ]:
        print(f'\n{name}', flush=True)
        phase_start = time.perf_counter()
        subprocess.run(command, cwd=ROOT, env=env, check=True)
        report['phases_seconds'][name] = round(time.perf_counter() - phase_start, 3)
    report['total_seconds'] = round(time.perf_counter() - started, 3)
    # Measure the actual database, image, volume and a point-in-time RAM reading.
    import psycopg2
    with psycopg2.connect(dbname=env['DB_NAME'], user=env['DB_USER'],
                          password=env['DB_PASSWORD'], host=env['DB_HOST'], port=env['DB_PORT']) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_database_size(current_database())')
            report['database_bytes'] = cursor.fetchone()[0]
    container = subprocess.check_output(compose_command() + ['ps', '-q', 'db'], text=True, env=env).strip()
    report['container_memory_snapshot'] = subprocess.check_output(
        ['docker', 'stats', '--no-stream', '--format', '{{.MemUsage}}', container], text=True).strip()
    image = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', container], text=True).strip()
    report['postgres_image_id'] = image
    report['image_bytes_uncompressed_shared'] = int(subprocess.check_output(
        ['docker', 'image', 'inspect', '--format', '{{.Size}}', image], text=True).strip())
    report['postgres_data_directory_kib'] = int(subprocess.check_output(
        compose_command() + ['exec', '-T', 'db', 'du', '-sk', '/var/lib/postgresql/data'], text=True, env=env).split()[0])
    logs = ROOT / 'logs'
    logs.mkdir(exist_ok=True)
    destination = logs / ('workshop-small-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    print(f'\nReport saved: {destination}')
    print('Start the app: python workshop/manage.py runserver')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(f'Setup stopped (exit {error.returncode}). Review the error above; no other database was reset.')
