import os
import sys
from Bio import SeqIO

seqDir = sys.argv[1]
assemblySummary = sys.argv[2]

seqFiles = [x for x in os.listdir(seqDir)]

assemblyDict = {}
with open(assemblySummary) as assemblyFile:
    for line in assemblyFile:
        line = line.split("\t")
        key = line[0]
        if key not in assemblyDict:
            assemblyDict[key] = line

for file in seqFiles:
    assemblyName, ext = os.path.splitext(file)
    if ext == '.fna':
        records = SeqIO.parse(seqDir + file, "fasta")
        for record in records:
            assemblyKey = 'GCF_' + assemblyName.split("_")[1]
            try:
                taxid = assemblyDict[assemblyKey][5]
                name = assemblyDict[assemblyKey][7]
                assemblyStatus = assemblyDict[assemblyKey][10]
                id = record.id.split("|")[0]
                record.id = id + "|kraken:taxid|" + taxid + " " + name + ", " + assemblyStatus
                SeqIO.write(record, seqDir + file, 'fasta')
            except:
                print(assemblyKey)
                pass

