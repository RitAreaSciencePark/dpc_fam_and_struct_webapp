from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import csv
import psycopg2
from psycopg2.extras import execute_values
import os

class Command(BaseCommand):
    help = 'Import mcs_sequences CSV into the mcs_sequences table.'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to the CSV file to import')
        parser.add_argument('--batch', type=int, default=5000, help='Batch size for inserts')

    def handle(self, *args, **options):
        csvpath = options['csvfile']
        batch_size = options['batch']

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

        # Create table if it doesn't exist (since managed=False)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS mcs_sequences (
            id SERIAL PRIMARY KEY,
            mcid TEXT NOT NULL,
            protein TEXT,
            range_str TEXT,
            aa_length INTEGER,
            amino_acids TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_mcs_sequences_mcid ON mcs_sequences(mcid);
        """
        cur.execute(create_table_sql)
        conn.commit()
        self.stdout.write(self.style.SUCCESS("Ensured table mcs_sequences exists."))

        # Columns in CSV: MCID, Protein, Range, AALength, AA, AA_Length (Redundant)
        # We need: mcid (0), protein (1), range_str (2), aa_length (3), amino_acids (4)
        
        sql = """
            INSERT INTO mcs_sequences (mcid, protein, range_str, aa_length, amino_acids)
            VALUES %s
        """

        batch = []
        count = 0
        
        with open(csvpath, 'r') as f:
            reader = csv.reader(f, delimiter=',') # Updated to comma
            # Check if header exists
            header = next(reader, None)
            
            # Simple header check logic
            if header:
               first_cell = header[0].upper()
               if 'MCID' not in first_cell and 'mcid' not in first_cell:
                   # Not a header, reset file pointer (unless your file is guaranteed to have one)
                   # Based on your prompt, it has a header: MCID,Protein,Range,AALength,AA,AA_Length
                   pass 
            
            for row in reader:
                if not row: continue
                
                # Check for row length. We need at least 5 cols
                if len(row) < 5:
                    continue
                
                # Extract data based on: MCID, Protein, Range, AALength, AA, AA_Length
                mcid = row[0].strip()
                protein = row[1].strip()
                range_str = row[2].strip()
                
                try:
                    aa_length = int(row[3])
                except ValueError:
                    aa_length = 0
                    
                amino_acids = row[4].strip()
                
                batch.append((mcid, protein, range_str, aa_length, amino_acids))
                
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

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} sequences.'))
        cur.close()
        conn.close()
