import xml.etree.ElementTree as ET
import csv
import os
import time

def parse_uniref_xml(xml_path, output_csv):
    """
    Parses a large UniRef50 XML file and extracts Pfam and DPCfam annotations.
    Outputs a CSV with columns:
    Uniref50_id, UniProtKB_ID, UniProtKB_accession, length, dpcfam_ids, dpcfam_ranges, pfam_ids, pfam_ranges
    """
    fieldnames = [
        'Uniref50_id', 'UniProtKB_ID', 'UniProtKB_accession', 'length',
        'dpcfam_ids', 'dpcfam_ranges', 'pfam_ids', 'pfam_ranges'
    ]
    
    start_time = time.time()
    count = 0
    
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # We use iterparse to stream the XML file memory-efficiently
        context = ET.iterparse(xml_path, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)
        
        current_entry = {}
        dpcfams = []
        pfams = []
        
        for event, elem in context:
            if event == 'end' and elem.tag.endswith('entry'):
                uniref_id = elem.get('id')
                
                # Extract basic info from representativeMember
                # Note: find() works because elem is a complete tree at 'end' event
                rep_ref = elem.find('.//representativeMember/dbReference')
                
                uniprot_id = ''
                accession = ''
                length = ''
                
                if rep_ref is not None:
                    uniprot_id = rep_ref.get('id')
                    for prop in rep_ref.findall('property'):
                        p_type = prop.get('type')
                        if p_type == 'UniProtKB accession':
                            accession = prop.get('value')
                        elif p_type == 'length':
                            length = prop.get('value')
                
                # Collect all dpcfam and pfam data for this entry
                dpcfam_ids = []
                dpcfam_ranges = []
                pfam_ids = []
                pfam_ranges = []

                for dpcfam in elem.findall('dpcfam'):
                    dpcfam_ids.append(dpcfam.get('metacluster'))
                    dpcfam_ranges.append(dpcfam.get('range'))
                
                for pfam in elem.findall('pfam'):
                    pfam_ids.append(pfam.get('family'))
                    pfam_ranges.append(pfam.get('range'))

                # Write a single row for the entry
                writer.writerow({
                    'Uniref50_id': uniref_id,
                    'UniProtKB_ID': uniprot_id,
                    'UniProtKB_accession': accession,
                    'length': length,
                    'dpcfam_ids': ';'.join(dpcfam_ids),
                    'dpcfam_ranges': ';'.join(dpcfam_ranges),
                    'pfam_ids': ';'.join(pfam_ids),
                    'pfam_ranges': ';'.join(pfam_ranges)
                })
                
                count += 1
                if count % 10000 == 0:
                    elapsed = time.time() - start_time
                    print(f"Processed {count} entries... (approx. {count / elapsed:.0f} entries/sec)", end='\r')
                
                # Clear the element to keep memory low
                elem.clear()
                root.clear()
                    
    print(f"\nFinished! Processed {count} entries in {time.time() - start_time:.2f}s.")
    print(f"Output saved to: {output_csv}")

if __name__ == "__main__":
    XML_FILE = "/u/mdmc/enyanduk/internship_areasciencepark/Data/dpcfam/dpcfam_standard/zenodo_unzipped_folders/Uniref50_XML/uniref50_annotated.xml"
    OUTPUT_CSV = "/u/mdmc/enyanduk/internship_areasciencepark/Dataframes/DPCFam/uniref50_dpcfam_pfam_mapping.csv"
    
    if os.path.exists(XML_FILE):
        parse_uniref_xml(XML_FILE, OUTPUT_CSV)
    else:
        print(f"Error: XML file not found at {XML_FILE}")
