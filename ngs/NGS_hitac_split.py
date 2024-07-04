import os
import sys
from Bio import SeqIO
import gzip

r1 = sys.argv[1]
r2 = sys.argv[2]
tn5_barcode = sys.argv[3]


def input_barcode(barcode_dir, open_barcode_f, barcode_file):
    with open(barcode_file, 'r') as barcode:
        os.makedirs('split_data', exist_ok=True)
        for line in barcode:
            fields = line.split()
            barcode_key = fields[1] + fields[2]
            barcode_dir[barcode_key] = fields[0]
            open_barcode_f[f'{fields[1]}{fields[2]}_1'] = open(f'split_data/{fields[0]}_1.fq', 'w')
            open_barcode_f[f'{fields[1]}{fields[2]}_2'] = open(f'split_data/{fields[0]}_2.fq', 'w')


def split_data(read1, read2, barcode_dir, open_barcode_f):
    print('\n\nSpliting data started.')
    if read1.endswith('.gz'):
        file1_open = gzip.open
    else:
        file1_open = open
    if read2.endswith('.gz'):
        file2_open = gzip.open
    else:
        file2_open = open

    barcode_num = 0
    with file1_open(read1, 'rt') as file1, file2_open(read2, 'rt') as file2:
        for r1_record, r2_record in zip(SeqIO.parse(file1, 'fastq'), SeqIO.parse(file2, 'fastq')):
            r1name = r1_record.id
            r1seq = str(r1_record.seq)
            r1_line3 = "+"  # Assuming this is always '+'
            r1quality = r1_record.format('fastq').split('\n')[3]

            r2name = r2_record.id
            r2seq = str(r2_record.seq)
            r2_line3 = "+"
            r2quality = r2_record.format('fastq').split('\n')[3]

            barcode_num += 1

            if r1seq[:8] + r2seq[:8] in barcode_dir:
                # 写入第一个reads信息
                open_barcode_f[f"{r1seq[:8]}{r2seq[:8]}_1"].write(f"@{r1name}\n{r1seq[27:]}\n{r1_line3}\n{r1quality[27:]}\n")
                # 写入第二个reads信息
                open_barcode_f[f"{r1seq[:8]}{r2seq[:8]}_2"].write(f"@{r2name}\n{r2seq[27:]}\n{r2_line3}\n{r2quality[27:]}\n")

    print(f"Total barcodes processed: {barcode_num}")


def main():
    barcode, open_barcode_file = {}, {}
    input_barcode(barcode, open_barcode_file, tn5_barcode)
    split_data(r1, r2, barcode, open_barcode_file)


if __name__ == '__main__':
    main()

