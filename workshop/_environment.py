"""Keep the teaching database configuration separate from the normal .env."""
import os
from pathlib import Path

from decouple import RepositoryEnv

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / '.env.workshop'


def environment():
    if not ENV_FILE.exists():
        raise SystemExit('Run: python workshop/setup.py')
    values = RepositoryEnv(str(ENV_FILE)).data
    result = os.environ.copy()
    result.update(values)
    result['DJANGO_SETTINGS_MODULE'] = 'dpc_fam_and_struct_webapp.settings'
    # The student app runs on the host, with PostgreSQL on a separate local port.
    result['DB_HOST'] = '127.0.0.1'
    return result


def compose_command():
    return ['docker', 'compose', '--project-name', 'dpcexplorer-workshop',
            '--env-file', str(ENV_FILE), '-f', str(ROOT / 'workshop/compose.yaml')]
