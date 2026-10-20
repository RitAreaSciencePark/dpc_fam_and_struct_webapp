"""Check the teaching data and existing app, without implementing the exercises."""
import os
import sys

from _environment import ROOT, environment


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    os.environ.update(environment())
    sys.path.insert(0, str(ROOT))
    import django
    django.setup()
    from django.db import connection
    from django.test import Client

    with connection.cursor() as cursor:
        cursor.execute('SELECT version FROM workshop_dataset_info')
        require(cursor.fetchall() == [(1,)], 'Unexpected dataset version')
        for table, key in [('dpcfam_mcs_properties', 'mcid'), ('dpcstruct_mcs_properties', 'mc_id')]:
            cursor.execute(f'SELECT count(*) FROM {table}')
            require(cursor.fetchone()[0] == 40, f'Expected 40 clusters in {table}')
            cursor.execute(f'SELECT count(*) FROM {table} WHERE {key} IN (%s, %s, %s)', ('MC1', 'MC3', 'MC15'))
            require(cursor.fetchone()[0] == 3, 'Missing example IDs')
        cursor.execute('SELECT count(*) FROM dpcstruct_mcs_properties WHERE plddt >= 80 AND mc_size >= 10')
        require(cursor.fetchone()[0] > 10, 'Need more than 10 matching structural records')
        cursor.execute('SELECT count(*) FROM dpcstruct_mcs_properties WHERE plddt IS NULL')
        require(cursor.fetchone()[0] > 0, 'Missing nullable confidence example')
        for table, protein_column in [
            ('dpcfam_mcs_sequences', 'protein_id'),
            ('dpcstruct_mcs_sequences', 'protein_id'),
            ('dpc_uniref50_pfam', 'uniref50_id'),
        ]:
            cursor.execute(f'SELECT count(*) FROM {table} WHERE {protein_column} = %s', ('WSDEMO0001',))
            require(cursor.fetchone()[0] == 130, f'Expected 130 demo mappings in {table}')
            cursor.execute(f'SELECT count(*) FROM {table} WHERE {protein_column} = %s', ('WSEMPTY0001',))
            require(cursor.fetchone()[0] == 0, f'Expected no mappings for WSEMPTY0001 in {table}')
        # Check synthetic sequence lengths and coordinates, not biological validity.
        cursor.execute('SELECT count(*) FROM dpcfam_mcs_sequences WHERE length(aa_seq) <> seq_length')
        require(cursor.fetchone()[0] == 0, 'Sequence lengths do not match')
        cursor.execute('SELECT count(*) FROM dpc_uniprot_proteins WHERE protein_id = %s', ('WSMISSING',))
        require(cursor.fetchone()[0] == 0, 'Missing-protein example must remain absent')

    client = Client(HTTP_HOST='127.0.0.1', HTTP_ACCEPT='application/json')
    for path in ['/api/', '/api/dpcfam/mcs/MC1/', '/api/dpcstruct/mcs/MC5/']:
        require(client.get(path).status_code == 200, f'Existing endpoint failed: {path}')
    first = client.get('/api/dpcfam/mcs/MC1/members/?page_size=3').json()
    require(len(first['results']) == 3 and first['next'], 'Pagination needs three results and a next page')
    require(client.get(first['next']).status_code == 200, 'Next pagination page failed')
    require(client.get('/api/dpcfam/mcs/MC999999/').status_code == 404, 'Unknown ID must return 404')
    require(client.post('/api/dpcfam/mcs/MC1/', data={}, content_type='application/json').status_code == 405,
            'Existing endpoint must remain read-only')
    for path in ['/', '/dpcfam/', '/dpcfam/mcs/MC1/', '/dpcstruct/', '/dpcstruct/mcs/MC5/',
                 '/protein/WSDEMO0001/', '/protein/WSEMPTY0001/', '/pfam/PF00001/']:
        require(client.get(path).status_code == 200, f'Web page failed: {path}')
    print('Verified: schema, sample IDs, mappings, filter cases, pagination, existing APIs, and core web pages.')
    print('The three /api/workshop/ exercise endpoints are still for students to implement.')


if __name__ == '__main__':
    main()
