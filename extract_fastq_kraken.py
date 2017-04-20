#!/usr/bin/envs python2.7
''' Script to extract fastq sequences mapping to taxid in kraken '''
import os
import argparse
import subprocess
import pandas as pd
import ncbiTaxonomyTree as nbt


def parse_arguments():
    ''' Parse command line arguments '''
    parser = argparse.ArgumentParser()
    
    # Add arguments
    parser.add_argument('--forward', '-f', required=True,
                        help='Forward read')
    parser.add_argument('--reverse', '-r',
                        help='If paired, reverse read')
    parser.add_argument('--tax_id', '-t', required=True,
                        help='Taxid to extract')
    parser.add_argument('--kraken', '-k', required=True,
                        help='Kraken result file')
    parser.add_argument('--names', '-n',
                        help='Name file used in the kraken-db, only required if \
                              --descendents is set')
    parser.add_argument('--nodes', '-p',
                        help='Node file used in the kraken-db, only required if \
                              --descendents is set')
    parser.add_argument('--descendents', action='store_true',
                        help='Extract sequences for the taxonomical ID and \
                              sequences in descendent groups. Requires --nodes \
                              and --names argument')
    parser.add_argument('--merge', action='store_true',
                        help='Write all extracted sequences to a single \
                              fastq-file.')
    parser.add_argument('--output', '-o',
                       help='Write fastq-files to a directory')

    args = parser.parse_args()

    if args.descendents:
        if args.names is None or args.nodes is None:
            parser.error('--descendents requires --names and --nodes.')

    return args


def extract_reads(taxid, taxid_sequences, reads, direction, merge, outdir):
    """ Extract fastq sequences based on headers """
    if merge:
        headers_path = os.path.join(outdir, taxid + '.list')
        with open(headers_path, 'w') as headers_file:
            for node_id in taxid_sequences.keys():
                for seq in taxid_sequences[node_id]:
                    headers_file.write(seq + '\n')
        seqtk(taxid, reads, headers_path, outdir)
    else:
        for node_id in taxid_sequences.keys():
            headers_path = os.path.join(outdir, str(node_id) + '.list')
            with open(headers_path, 'w') as headers_file:
                for seq in taxid_sequences[node_id]:
                    headers_file.write(seq + '\n')
            seqtk(node_id, reads, headers_path, outdir)

def seqtk(taxid, reads, headers_path, outdir):
    seqtk_args = ['seqtk', 'subseq', reads, headers_path]
    process = subprocess.Popen(seqtk_args, stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = process.communicate()
    fastq_path = os.path.join(outdir, str(taxid) + '.fastq')
    with open(fastq_path, 'w') as fastq_out:
        fastq_out.write(out)

def main():
    """ Main application """
    # Get command line arguments
    args = parse_arguments()
    
    # Create output directory
    if args.output == None:
        outdir = ''
    else:
        outdir = args.output
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

    print("\nLoad data")
    print("=========")
    # Import kraken result file
    print("Load kraken-report file")
    kraken_df = pd.read_csv(args.kraken, sep='\t', header=None,
            names=['Classified', 'SeqID', 'TaxID', 'SeqLength', 'LCAmapping'])
    
        
    if args.reverse:
        reverse = True
    else:
        reverse = False
 
    taxid = args.tax_id
    
    # Read Taxonomy tree 
    if args.descendents: # Use NCBI taxonomy to extract sequences from descendents
        print("Load NCBI taxonomy")
        tree = nbt.NcbiTaxonomyTree(nodes_filename=args.nodes, names_filename=args.names)

        print("\nFind Nodes and Sequences")
        print("========================")
        child_nodes = tree.getDescendants([int(taxid)])
    
        # Get sequences from nodes
        taxid_sequences = {} # Bin sequences to nodes
        nr_nodes = 0 # Nodes containing sequences
        tot_sequences = 0 # Total number of sequences to extract
        for child_taxid in child_nodes[int(taxid)]:
            nr_reads = len(list(kraken_df.loc[kraken_df['TaxID'] == child_taxid].SeqID))
            if nr_reads != 0:
                print("Node " + str(child_taxid) + " contains " + str(nr_reads) + ' sequences')
                taxid_sequences[child_taxid] = list(kraken_df.loc[kraken_df['TaxID'] == child_taxid].SeqID)
                nr_nodes += 1
                tot_sequences += nr_reads

    else: # Extract only sequences for the specific node
        print('\nFind Sequences')
        print('===============')
        taxid_sequences = {}
        nr_reads = len(list(kraken_df.loc[kraken_df['TaxID'] == int(taxid)].SeqID))
        if nr_reads != 0:
            print("Node " + taxid + " contains " + str(nr_reads) + ' sequences')
            taxid_sequences[int(taxid)] = list(kraken_df.loc[kraken_df['TaxID'] == int(taxid)].SeqID)
        nr_nodes = 1
        tot_sequences = nr_reads
        
    # Print results
    if nr_nodes == 1:
        print("\nFound " + str(tot_sequences) + " sequences to extract from " + str(len(taxid_sequences)) + " node\n")
    elif nr_nodes == 0:
        sys.exit("No sequences where found for that node")
    else:
        print("\nFound " + str(tot_sequences) + " sequences to extract from " + str(len(taxid_sequences)) + " different nodes\n")

    # Extract reads and write to new fastq-file
    print("Extract reads")
    print("=============")
    print("Extract forward reads")
    extract_reads(taxid, taxid_sequences, args.forward, 'forward', args.merge, outdir)

    if reverse:
        print("Extract reverse reads")
        extract_reads(taxid, taxid_sequences, args.reverse, 'reverse', args._merge, outdir)


if __name__ == '__main__':
    main()
