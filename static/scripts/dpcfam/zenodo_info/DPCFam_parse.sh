#!/bin/bash
#PBS -l nodes=1:ppn=5
#PBS -q thin
#PBS -l walltime=40:00:00
#PBS -N dpcfam_XML
### Output files
#PBS -e dpcfam_XML.err
#PBS -o dpcfam_XML.log

#cd /u/area/evillegas/scratch/dpcfam_v1.1/package

export LC_NUMERIC="en_US.UTF-8"

mkdir mc_info_from_xml/
mkdir mc_info_from_xml/MC_fasta/

awk -f MCxml_to_tables.awk metaclusters_dpcfam.xml
