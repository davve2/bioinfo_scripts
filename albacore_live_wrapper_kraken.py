#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import fnmatch
import re
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher(FileSystemEventHandler):

    def __init__(self, args, names, tax, class_number):
        FileSystemEventHandler.__init__(self)
        self.tax = tax
        self.names = names
        self.class_number = class_number
        self.queue = []
        self.nr_dirs = 0
        self.species = {}
        self.args = args
    
    def on_any_event(self, event):
        if event.is_directory:
            if event.event_type == 'created':
                self.add_to_queue(event.src_path)

    def add_to_queue(self, dir):
        self.queue.append(dir)

        if len(self.queue) == 1:
            return 0
        else:
            print("Run albacore on %s" % self.queue[0])
            output = os.path.join(self.args.output, str(self.nr_dirs) + '_basecalled')
            cmd = ['read_fast5_basecaller.py', '-i', self.queue[0], '-t', args.threads,
                   '-s', output, '-f', args.flowcell, '-k', args.kit]
            start = time.time()
            process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
            process.communicate()
            print("Basecalling completed in %ds for %s" % (time.time() - start, self.queue[0]))
            for root, dirnames, filenames in os.walk(output):
                for filename in fnmatch.filter(filenames, '*.fastq'):
                    # From here we ca do what we want with the fastq files
                    fastq_file = os.path.join(root, filename)
                    name, ext = os.path.splitext(filename)
                    kraken_file = name + '.kraken'
                    kraken_file = os.path.join(root, kraken_file)
                    barcode = root.split('/')[-1]
                    print("Run kraken on %s" % fastq_file)
                    cmd = ['kraken', '--db', '/mnt/powervault/emihag/data/references/minikraken_db',
                           '--threads', '16', '--fastq-input', fastq_file]
                    kraken_output = open(kraken_file, 'w')
                    process = subprocess.Popen(cmd, stdout=kraken_output, stderr=subprocess.PIPE)
                    process.wait()
                    kraken_output.close()
                    with open(kraken_file, 'r') as kraken_result:
                        for line in kraken_result:
                            result_line = re.split(r'\t', line)
                            if len(result_line) > 2:
                                txid = int(result_line[2])
                            if txid == 0 or txid == 1:
                                txid = None
                            if txid is not None:
                                family = self.get_class_name(txid, 'species')
                                if barcode in self.species:
                                    if family in self.species[barcode]:
                                        self.species[barcode][family] += 1
                                    else:
                                        self.species[barcode][family] = 1
                                else:
                                    self.species[barcode] = {family: 1}
            print(self.species)
            del self.queue[0]
            self.nr_dirs += 1

            
    
    def get_current_class(self, txid):
        return self.tax[txid][1]

    def get_class_name(self, txid, class_name='species'):
        level = self.get_current_class(txid)
        if txid == 131567:
            level = 'cellular organism'
        if self.class_number[level] > self.class_number[class_name]:
            return False
        elif self.class_number[level] == self.class_number[class_name]:
            return self.names[txid]

        while level != class_name:
            level = self.tax[txid][1]
            name = self.names[txid]
            txid = self.tax[txid][0]

        return name

def parse_arguments():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--watch', '-w', help='Output directory for MinKnow',
                        required=True)
    parser.add_argument('--output', '-o', help='Save basecalled directories here',
                        required=True)
    parser.add_argument('--threads', '-t', help='Threads to run albacore with',
                        required=True)
    parser.add_argument('--flowcell', '-f', help='Flowcell version',
                        required=True)
    parser.add_argument('--kit', '-k', help='Sequencing kit',
                        required=True)
    parser.add_argument('--barcoding', '-b', action='store_true', help='Demultiplex')
    parser.add_argument('--db', '-d', help='Kraken Database')

    args = parser.parse_args()

    return args

if __name__ == '__main__':

    args = parse_arguments()

    if not os.path.isdir(args.watch):
        sys.exit("The directory to watch does not exist")

    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    species = {None:0}
    class_number = {'no rank':0,
                    'subspecies':1,
                    'species':2,
                    'genus':3,
                    'family':4,
                    'order':5,
                    'class':6,
                    'phylum':7,
                    'superkingdom':8,
                    'cellular organism':9}

    print('Loading taxonomy data')
    taxonomy_path = os.path.join(args.db, 'taxonomy/nodes.dmp')
    tax = {}
    with open(taxonomy_path, 'r') as taxonomy_file:
        for line in taxonomy_file:
            line = line.split("|")
            txid = int(line[0])
            parent = int(line[1].strip("\t"))
            level = line[2].strip("\t")
            tax[txid] = [parent, level]
    
    print(tax[299583])
    
    names_path = os.path.join(args.db, 'taxonomy/names.dmp')
    names = {}
    with open(names_path, 'r') as name_file:
        for line in name_file:
            line = line.split("|")
            line = [item.strip() for item in line]
            if line[3] == 'scientific name':
                txid = int(line[0])
                names[txid] = line[1]
    print('The taxonomy data has been loaded')

    observer = Observer()
    watcher = Watcher(args, names, tax, class_number)
    observer.schedule(watcher, args.watch)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Check for new folder in directory

# Add folder to queue

# Run albacore on first folder in queue

# Output results to folder with same name as input, but add basecalled

# Remove folder from queue
