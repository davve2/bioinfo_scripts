""" Script to run pilon iteratively to correct genome assemblies """
import os
import argparse
import logging
import subprocess


def parse_arguments():
    """ Parse command line arguments """
    # Create parser
    parser = argparse.ArgumentParser(description='Run pilon many times')
    
    # Add arguments
    parser.add_argument('--draft_seq', '-d', required=True,
                        help='Draft sequence to correct')
    parser.add_argument('--forward', '-f', required=True,
                        help='Reads to use for correction')
    parser.add_argument('--reverse', '-r',
                        help='Reverse read for correction')
    parser.add_argument('--output', '-o', required=True,
                        help='Output directory')
    parser.add_argument('--iterations', '-i', required=True,
                        help='How many times to run pilon')
    parser.add_argument('--threads', '-t', required=True,
                        help='Threads to use')
    parser.add_argument('--pilon', '-p', required=True,
                        help='Path to pilon.jar')
    # Parse arguments
    args = parser.parse_args()

    return args

def run_bwa(reference_genome, forward_read, reverse_read, threads, output, i):
    """ Run bwa to align reads to reference genome """
    # Index ref genome
    print('Align reads with BWA MEM')
    bwa_index_args = ['bwa', 'index', reference_genome]
    process = subprocess.Popen(bwa_index_args, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = process.communicate()
    
    # Align reads to reference genome
    bwa_mem_args = ['bwa', 'mem', '-t', threads, '-x', 'ont2d', reference_genome, forward_read, reverse_read] 
    process = subprocess.Popen(bwa_mem_args, stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE)
    out, err = process.communicate()

    # Write alignment to file
    sam_file = os.path.join(output, 'bwa_mem_' + str(i + 1) + '.sam')
    with open(sam_file, 'w') as bwa_mem_out:
        bwa_mem_out.write(out)
    
    return sam_file

def run_samtools(sam_file, threads, output, i):
    """ Sort and convert to BAM using samtools """

    # Conver the SAM-file to a BAM-file
    print('Convert SAM-file to BAM-file')
    bam_file = os.path.join(output, 'bwa_mem_' + str(i + 1) + '.bam')
    samtools_view_args = ['samtools', 'view', '-@', threads, '-bS', '-o',
                          bam_file, sam_file]
    process = subprocess.Popen(samtools_view_args, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = process.communicate()
    
    # Sort and return the BAM-fil
    print('Sort BAM-file')
    bam_sorted_file = os.path.join(output, 'bwa_mem_' + str(i + 1) + '.sorted.bam')
    samtools_sort_args = ['samtools', 'sort', bam_file, '-o', bam_sorted_file]
    process = subprocess.Popen(samtools_sort_args, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = process.communicate()

    # Index sorted BAM-file
    samtools_index_args = ['samtools', 'index', bam_sorted_file]
    process = subprocess.Popen(samtools_index_args, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = process.communicate()

    return bam_sorted_file

def run_pilon(bam_sorted_file, reference_genome, pilon_output, threads, pilon_path):
    """ Run Pilon """
    print('Run Pilon')
    pilon_args = ['java', '-Xmx16G', '-jar', pilon_path, '--genome', reference_genome,
                  '--frags', bam_sorted_file, '--threads', threads, '--output',
                  pilon_output]
    process = subprocess.Popen(pilon_args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
    out, err = process.communicate()
    print(out)
    with open(pilon_output + '.log', 'w') as pilon_log:
        pilon_log.write(out)

def main():
    """ Main Application """
    # Get arguments
    args = parse_arguments()
    
    logging.basicConfig(filename='logging.log', level=logging.DEBUG)
    
    output = args.output
    reference_genome = args.draft_seq
    if args.reverse:
        reverse_read = args.reverse
    else:
        reverse_read = ""
    forward_read = args.forward
    threads = args.threads
    iterations = args.iterations
    pilon_path = args.pilon
    logging.info('OUTPUT DIRECTORY:' + output)
    logging.info('READS: ' + forward_read + ', ' + reverse_read) 
    logging.info('THREADS: ' + threads)
    logging.info('ITERATIONS: ' + iterations)

    # Set pilon output
    pilon_output = os.path.join(output, 'pilon_1')
    os.mkdir(output)

    logging.info('START CORRECTION')
    for i in range(int(iterations)):
        # Log
        logging.info('ITERATION: ' + str(i + 1))
        logging.info('REFERENCE GENOME: ' + reference_genome)
        logging.info('PILON OUTPUT: ' + pilon_output)
        sam_file = run_bwa(reference_genome, forward_read, reverse_read, threads, output, i)
        bam_sorted_file = run_samtools(sam_file, threads, output, i)
        run_pilon(bam_sorted_file, reference_genome, pilon_output, threads, pilon_path)

        # Set pilon output to new reference
        reference_genome = os.path.join(output, 'pilon_' + str(i + 1) + '.fasta')
        pilon_output = os.path.join(output, 'pilon_' + str(i + 2))

if __name__ == '__main__':
    main()
