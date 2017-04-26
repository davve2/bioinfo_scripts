from __future__ import print_function
import time
import sys

# Follow a file like tail -f.
# http://stackoverflow.com/questions/5419888/reading-from-a-frequently-updated-fileimport time
def follow(sequence_summary):
    sequence_summary.seek(0,2)
    while True:
        line = sequence_summary.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

if __name__ == '__main__':
    sequence_summary = open(sys.argv[1], 'r')
    loglines = follow(sequence_summary)
    for lines in loglines:
        print(lines, end='\r')
        sys.stdout.flush()
