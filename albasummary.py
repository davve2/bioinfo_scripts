#!/usr/bin/env python
import pandas as pd
import sys
import numpy as np

# **** Import file ****
if len(sys.argv) != 2:
    sys.exit("Usage: python albasummary.py sequencing_summary.txt")
summary_file = sys.argv[1]
summary = pd.read_csv(summary_file, sep = '\t')

# **** Calculate some statistics ****
nr_reads = summary.shape[0]
mean_read_length = np.mean(summary['sequence_length_template'])
throughput_gb = sum(summary['sequence_length_template'])/1000000000
throughput = sum(summary['sequence_length_template'])
max_read_length = np.max(summary['sequence_length_template'])

# **** Print to screen ****
print("==== Albacore statistics =====")
print("Number of reads: %d" % (nr_reads))
print("Avg. read length: %.2fbp" % (mean_read_length))
print("Max read length: %dbp" % (max_read_length))
print("Throughput: %.8fGb" % (throughput_gb))
print("Throughput: %dbp" % (throughput))
