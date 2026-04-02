# DPCfam's MetaClusters' seed data - version 1.0
This package contains DPCfam's Metaclusters **seed** data.
Data is presented in XML format with the respective XML schema. 

We used DPCfam software version 1.0 to analyze UniRef50 v.2017_07. As a result, the DPCfam MetaCluster 1.0 dataset has been produced.
The comparison with Pfam *ground truth* used Pfam v. 31 and the respective official Pfam annotation of UniProt v.2019_08.

For each MetaCluster we report some measures regarding intrinsic properties of the MC based on its seed sequences:
- Number of seed sequences
- Average amino-acidic length of seed sequences
- Standard Deviation of the former
- Fraction of amino-acids in a Low Complexity region  ( LC )
- Fraction of amino-acids in a Coiled Coil region ( CC )
- Fraction of amino-acids in a Disordered region ( DIS )
- Average number of TransMembrane regions ( TM )

For each Metacluster we report some measures to compare the MC with its Pfam *ground truth*, if any:
- Dominant Pfam Architecture ( DA ) [UNK if no DA has been found]
- Percent of sequences in the MC matching the DA
- Average overlap of the former sequences with the DA
- Label describing qualitatively the overlap of the MC with its DA, which can be: equivalent, reduced, extended or shifted

Note that in very few cases the DA of a MC is not computable ( NA ).

Finally, for each MetaCluster we report the respective seed sequences.
Each seed sequence is written as:
- Uniprot unique identifier of the original protein sequence, together with the start and end position of the subsequence collected as seed sequence
- amino-acidic seed sequence 


# Parsing and parsed files
We provide a bash parser to transform from XML format to a set of tables (written as SSV, space separated values files) and fasta files.
AWK is needed.
To convert XML to SSV tables and fasta files, run the bash script parse.sh as

    ./parse.sh
    
This will generate, in the same folder of the data, the subfolders

     mc_info_from_xml 
     mc_info_from_xml/MC_fasta 

where parsed files will be located.

## MCs fasta files
For each MC, the parser generates a FASTA file in *mc_info_from_xml/MC_fasta*. The fasta file of MetaCluster XXX is named as MCXXX.fasta and contains the *unaligned* seed sequences of MC XXX. Each sequence is named after the original protein identifier specifying start and end position of the seed subregion in the MC, as follows:

`>Protein_uniprot_ID|start_position-end_position`

## SSV tables
In the folder *mc_info_from_xml* the parser will generate the following SSV tables:

* **mclist.txt** lists the indexes (XXX) of all MCs listed in the original XML file


* **sequence_information.txt** lists for each MC the following measures:
	- column 1: MC index
	- column 2: number of sequences in the MC's seed
	- column 3: average length of the MC's seed regions
	- column 4: standard deviation of the length of the MC's seed regions


* **pfam_comparison.txt** lists for each MC the comparison with Pfam *ground truth*:
	- column 1: MC index
	- column 2: MC's Dominant Pfam Architecture ( DA ) [UNK if no DA has been found]
	- column 3: percent of sequences in the MC matching the DA
	- column 4: average overlap of the former sequences with the DA
	- column 5: label describing qualitatively the overlap of the MC with its DA, which can be: equivalent, reduced, extended or shifted

	Note that in very few cases the DA of an MC is not computable ( NA ).


* **lcregions.txt**  lists for each MC the fraction of amino-acids in a Low Complexity region, as:
	- column 1: MC index
	- column 2: LC fraction


* **ccregions.txt**  lists for each MC the fraction of the amino-acids in a Coiled Coil region, as:
	- column 1: MC index
	- column 2: CC fraction 


* **disregions.txt**  lists for each MC the fraction of amino-acids in a Disordered region, as:
	- column 1: MC index
	- column 2: DIS fraction 


* **tmregions.txt**  lists for each MC the average number of TransMembrane regions, as:
	- column 1: MC index
	- column 2: average TM



# References
Further information about how MCs have been built, analyzed and compared with Pfam are reported in 
- Russo, Elena Tea. "Unsupervised protein family classification by Density Peak clustering." (2020), PhD Thesis, `http://hdl.handle.net/20.500.11767/116345`
