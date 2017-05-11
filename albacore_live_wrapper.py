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

    def __init__(self, ):
        FileSystemEventHandler.__init__(self, args)
        self.queue = []
        self.nr_dirs = 0
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
            cmd = ['read_fast5_basecaller.py', '-i', self.queue[0], '-t', self.args.threads,
                   '-s', output, '-f', self.args.flowcell, '-k', self.args.kit, '--barcoding']
            if self.args.barcoding:
                cmd.append('--barcoding')
            start = time.time()
            process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
            process.communicate()
            print("Basecalling completed in %ds for %s" % (time.time() - start, self.queue[0]))
            del self.queue[0]
            self.nr_dirs += 1

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

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    
    args = parse_arguments()

    if not os.path.isdir(args.watch):
        sys.exit("The directory to watch does not exist")
    
    if not os.path.isdir(args.output):
        print("Create output directory")
        os.mkdir(args.output)

    observer = Observer()
    watcher = Watcher(args)
    observer.schedule(watcher, args.watch)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
