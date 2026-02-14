from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import csv
import psycopg2
from psycopg2.extras import execute_values
import os


class Command(BaseCommand):
    help = 'Import alphafold CSV into the alphafold_reps table.'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to the CSV file to import')
        parser.add_argument('--batch', type=int, default=5000, help='Batch size for inserts')
        parser.add_argument('--truncate', action='store_true', help='Truncate table before insert')

    def handle(self, *args, **options):
        csvpath = options['csvfile']
        batch_size = options['batch']
        truncate = options.get('truncate', False)

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

        if truncate:
            cur.execute('TRUNCATE TABLE alphafold_reps;')
            conn.commit()
            self.stdout.write('Truncated alphafold_reps table.')

        # Columns: mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt
        sql = """
            INSERT INTO alphafold_reps (mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt)
            VALUES %s
        """

        batch = []
        count = 0
        
        with open(csvpath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if not row or not row.get('mcid'):
                    continue
                
                # Extract data from CSV columns
                mcid = row.get('mcid', '').strip()
                alphafold_prot = row.get('alphafold_prot', '').strip()
                seq_range = row.get('seq_range', '').strip()
                
                try:
                    hmm_coverage = float(row.get('hmm_coverage', 0))
                except ValueError:
                    hmm_coverage = 0.0
                
                try:
                    avg_plddt = float(row.get('avg_plddt', 0))
                except ValueError:
                    avg_plddt = 0.0
                
                batch.append((mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt))
                
                if len(batch) >= batch_size:
                    execute_values(cur, sql, batch)
                    conn.commit()
                    count += len(batch)
                    batch = []
                    self.stdout.write(f"Imported {count} rows...")

            if batch:
                execute_values(cur, sql, batch)
                conn.commit()
                count += len(batch)

        cur.close()
        conn.close()
        self.stdout.write(self.style.SUCCESS(f"Import completed, {count} rows processed."))
