### albasummary.py  
Summarize basecalling data from the sequencing_summary.txt file produced by
albacore.

### change_headers_kraken.py  
Change headers in fasta files to fit with kraken-build. Use NCBI-genome-download
to download the genomes and use the assembly summary file from refseq to change
to correct headers.

### extract_fastq_kraken.py
Extract sequences that map to a specific taxonomic id.  

**Usage**
```
usage: extract_fastq_kraken.py [-h] --forward FORWARD [--reverse REVERSE]
                               --tax_id TAX_ID --kraken KRAKEN [--names NAMES]
                               [--nodes NODES] [--descendents] [--merge]
                               [--output OUTPUT]
```
Using `--descendents` will also extract all sequences within in this clade.  
This requires the path to the names.dmp and nodes.dmp file used to build the
kraken database. The `--merge` command will write all sequences to one fastq-file.
To extract unclassified reads, use `--tax_id 0`.  

**Requirements**
* seqtk
* pandas
* [ncbiTaxonomyTree](https://github.com/frallain/NCBI_taxonomy_tree)

### iterate_pilon.py
Script to run pilon iteratively.

### albacore_live_wrapper.py
Run albacore basecalling when a new directory with reads is created.
