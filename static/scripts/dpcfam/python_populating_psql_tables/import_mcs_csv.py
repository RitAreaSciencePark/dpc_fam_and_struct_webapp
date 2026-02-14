from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import csv
import psycopg2
from psycopg2.extras import execute_values
import os


class Command(BaseCommand):
    help = 'Import mcs_properties CSV into the existing mcs_properties table using upsert.'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to the CSV file to import')
        parser.add_argument('--batch', type=int, default=5000, help='Batch size for inserts')

    def handle(self, *args, **options):
        csvpath = options['csvfile']
        batch = options['batch']

        if not os.path.exists(csvpath):
            raise CommandError(f'File not found: {csvpath}')

        db = settings.DATABASES['default']
        conn = psycopg2.connect(
            dbname=db.get('NAME'),
            user=db.get('USER'),
            password=db.get('PASSWORD'),
            host=db.get('HOST') or 'localhost',
            port=db.get('PORT') or 5432,
        )
        cur = conn.cursor()

        cols = [
            'mcid','size_uniref50','avg_len','std_avg_len','lc_percent','cc_percent',
            'dis_percent','tm','pfam_da','da_percent','size_pfam','avg_ov_percent','overlap_label'
        ]

        placeholders = ','.join(['%s'] * len(cols))

        insert_sql = f"""
        INSERT INTO mcs_properties ({','.join(cols)})
        VALUES %s
        ON CONFLICT (mcid) DO UPDATE SET
        size_uniref50 = EXCLUDED.size_uniref50,
        avg_len = EXCLUDED.avg_len,
        std_avg_len = EXCLUDED.std_avg_len,
        lc_percent = EXCLUDED.lc_percent,
        cc_percent = EXCLUDED.cc_percent,
        dis_percent = EXCLUDED.dis_percent,
        tm = EXCLUDED.tm,
        pfam_da = EXCLUDED.pfam_da,
        da_percent = EXCLUDED.da_percent,
        size_pfam = EXCLUDED.size_pfam,
        avg_ov_percent = EXCLUDED.avg_ov_percent,
        overlap_label = EXCLUDED.overlap_label
        """

        self.stdout.write(f'Importing {csvpath} in batches of {batch}...')

        rows = []
        count = 0
        with open(csvpath, newline='') as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                vals = [
                    r.get('mcid') or r.get('MCID') or r.get('mc_id'),
                    self._as_int(r.get('size_uniref50')),
                    self._as_float(r.get('avg_len')),
                    self._as_float(r.get('std_avg_len')),
                    self._as_float(r.get('lc_percent')),
                    self._as_float(r.get('cc_percent')),
                    self._as_float(r.get('dis_percent')),
                    self._as_float(r.get('tm')),
                    r.get('pfam_da'),
                    self._as_float(r.get('da_percent')),
                    self._as_int(r.get('size_pfam')),
                    self._as_float(r.get('avg_ov_percent')),
                    r.get('overlap_label') or r.get('overlap_type'),
                ]
                rows.append(tuple(vals))
                if len(rows) >= batch:
                    execute_values(cur, insert_sql, rows, template=None)
                    conn.commit()
                    count += len(rows)
                    self.stdout.write(f'Inserted/Updated {count} rows...')
                    rows = []

        if rows:
            execute_values(cur, insert_sql, rows, template=None)
            conn.commit()
            count += len(rows)

        cur.close()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f'Import completed, {count} rows processed.'))

    def _as_int(self, v):
        try:
            return int(v) if v not in (None, '') else None
        except Exception:
            return None

    def _as_float(self, v):
        try:
            return float(v) if v not in (None, '') else None
        except Exception:
            return None
