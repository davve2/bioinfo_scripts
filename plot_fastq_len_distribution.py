import sys
from Bio import SeqIO
import matplotlib.pyplot as plt
import numpy as np

# Check number of arguments
if len(sys.argv) != 3:
    print("Usage: python plot_fastq_len_distibution.py <fastq-file> <output.png>")
    sys.exit()

fastq_path = sys.argv[1]
output_path = sys.argv[2]
# Parse fastq file
records = SeqIO.parse(fastq_path, "fastq")

# Loop over records and store read lengths to a list
read_lengths = []
_500 = 0
_500_1k = 0
_1k_5k = 0
_5k_10k = 0
_10k_50k = 0
_50k_100k = 0
_100k_500k = 0
_500k_1m = 0
_1m = 0

for record in records:
    read_length = len(record.seq)
    read_lengths.append(read_length)
    if read_length < 500:
        _500 += 1
    elif read_length >= 500 and read_length < 1000:
        _500_1k += 1
    elif read_length >= 1000 and read_length < 5000:
        _1k_5k += 1
    elif read_length >= 5000 and read_length < 10000:
        _5k_10k += 1
    elif read_length >= 10000 and read_length < 50000:
        _10k_50k += 1
    elif read_length >= 50000 and read_length < 100000:
        _50k_100k  += 1
    elif read_length >= 100000 and read_length < 500000:
        _100k_500k += 1
    elif read_length >= 500000 and read_length < 1000000:
        _500k_1m += 1
    elif read_length > 1000000:
        _1m += 1

read_bars = (_500, _500_1k, _1k_5k, _5k_10k, _10k_50k, _50k_100k, _100k_500k, _500k_1m, _1m)
index = np.arange(9)
plt.bar(index, read_bars)
# Print some statistics
print("Read length Distribution")
print("========================")
print("< 500bp: " + str(_500))
print("500bp - 1000bp: " + str(_500_1k))
print("1kb - 5kb: " + str(_1k_5k))
print("5kb - 10kb: " + str(_5k_10k))
print("10kb - 50kb: " + str(_10k_50k))
print("50kb - 100kb: " + str(_50k_100k))
print("100kb - 500kb: " + str(_100k_500k))
print("500kb - 1mb: " + str(_500k_1m))
print(">1mb: " + str(_1m))

plt.xticks(index, ("< 500bp", "500bp - 1000bp", "1k - 5k", "5k - 10k", "10k - 50k", "50k - 100k", "100k - 500k", "500k - 1m", "> 1m"), rotation="vertical")
plt.xlabel("Read length")
plt.ylabel("Number of reads")
plt.title("Read length Distribution: \n" + fastq_path)
plt.tight_layout()
plt.grid(False)

# Plot the read length distribution
#plt.hist(read_lengths, 50, facecolor="green")
#plt.title("Read Length Distribution: \n" + fastq_path)
#plt.xlabel("Read Length")
#plt.ylabel("Frequency")
#plt.grid(False)

# Display the plot
#plt.show()

plt.savefig(output_path)
