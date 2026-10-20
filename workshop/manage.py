"""Run ordinary Django commands against the small workshop database."""
import subprocess
import sys

from _environment import ROOT, environment

if __name__ == '__main__':
    raise SystemExit(subprocess.call(
        [sys.executable, str(ROOT / 'manage.py'), *sys.argv[1:]],
        cwd=ROOT, env=environment(),
    ))
