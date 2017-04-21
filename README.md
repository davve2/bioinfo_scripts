### albasummary.py  
Summarize basecalling data from the sequencing_summary.txt file produced by
albacore.

### change_headers_kraken.py  
Change headers in fasta files to fit with kraken-build. Use NCBI-genome-download
to download the genomes and use the assembly summary file from refseq to change
to correct headers.

### extract_fastq_kraken.py
Extract sequences that map to a specific taxonomic id.  

*Usage*
```
usage: extract_fastq_kraken.py [-h] --forward FORWARD [--reverse REVERSE]
                               --tax_id TAX_ID --kraken KRAKEN [--names NAMES]
                               [--nodes NODES] [--descendents] [--merge]
                               [--output OUTPUT]
```
Using `--descendents` will also grab all sequences within in this clade.  
This requires the path to the names.dmp and nodes.dmp file used to build the
kraken database. `--merge` will write all sequences for 

**Requirements**


