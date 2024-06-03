# how to analyse the NGS data
## 1.data splite
we use `fastq-multx` to splite data [fastq-multx](https://github.com/brwnj/fastq-multx/tree/master)
### Build
```
git clone https://github.com/brwnj/fastq-multx
cd fastq-multx
make
```
### Parameter
```
-o, 输出文件，一个输入文件一个输出文件流，格式： %.R1.fq.gz， %为barcode对应的样本名
-m, barcod允许的主要错配个数，一般设置为0， 默认1
-B, barcode文件，允许单端和双端barcode
-n, 打印barcode序列
-b, 从序列的5'端碱基开始匹配barcode
-e, 从序列3'端开始匹配序列
-q, 控制barcode碱基的最小phred quality值，默认为0，不控制
-d, 控制匹配的最佳barcode位置和此佳barcode位置的位置，两个匹配距离不能超过2个碱基
```
### Example Usage
barcode file
```
itaq1	ATCACG-TCTAAT
itaq2	CGATGT-TCTAAT
itaq3	TTAGGC-TCTAAT
itaq4	TGACCA-TCTAAT
itaq5	ACAGTG-TCTAAT
itaq6	GCCAAT-TCTAAT
itaq7	CAGATC-TCTAAT
```
output file
```
mkdir fastq_multx_output-1
./fastq-multx/fastq-multx -B barcode.txt -m 1 -b itaq.1.fastq itaq.2.fastq -o %.R1.fastq -o %.R2.fastq
 
# 因为桥式PCR测序过程中双端序列方向不一定一致，因此需要颠倒两测序文件进行二次拆分
mkdir fastq_multx_output-2
./fastq-multx/fastq-multx -B barcode.txt -m 1 -b itaq.2.fastq itaq.1.fastq -o %.R1.fastq -o %.R2.fastq
 
# 合并两次拆分的结果
mkdir fastq_multx_output
for i in `ls fastq_multx_output-1/itaq*.R1.fastq`; do a=${i/.R1.fastq/}; a=${a/fastq_multx_output-1\//}; echo "$a"; done > sample.list
for i in `cat sample.list`; do echo "cat fastq_multx_output-1/$i.R1.fastq fastq_multx_output-2/$i.R2.fastq > ./fastq_multx_output/$i.R1.fastq"; done > command.combine.R1.list
for i in `cat sample.list`; do echo "cat fastq_multx_output-1/$i.R2.fastq fastq_multx_output-2/$i.R1.fastq > ./fastq_multx_output/$i.R2.fastq"; done > command.combine.R2.list
sh command.combine.R1.list
sh command.combine.R2.list
```
## 2.fastq and adapter cuting
we use `fastp`and`cutadapt` ,these can instell by conda

1) `fastp` parameter

```
#!/bin/bash
for i in `cat list`
do
 fastp  -i $i'_R1.fq.gz' -I $i'_R2.fq.gz' -o '../clean_file/'$i'_R1_clean.fq.gz' -O '../clean_file/'$i'_R2_clean.fq.gz'
done
echo "finished!"
```
2) `cutadapt` parameter

```
#!/bin/bash
for i in `cat list`
do
 cutadapt -g CTGCAAGGCGATTAAGTTGGGTA -G GCAGTGAGCGCAACGCAATT -e 0.1 -O 5 -m 30 -o '../cut_fasta/'$i'_R1_cut.fq.gz' -p '../cut_fasta/'$i'_R2_cut.fq.gz' $i'_R1_clean.fq.gz' $i'_R2_clean.fq.gz'
done
echo "finished!"
```
## 3.CRISPRoss2
[CRISPRoss2](https://github.com/pinellolab/CRISPResso2)
### 3.1 ues oo2 analyse cas9

```
#!/bin/bash
for i in `cat cas_list`
do
 CRISPResso --fastq_r1 $i'_R1_cut.fq.gz' --fastq_r2 $i'_R2_cut.fq.gz' \
 --amplicon_seq CCAAAGGACCCCAGTCACTCCAGCCTGTTGGCTGCCGCTCACTTTGATGTCTGCAGGCCAGATGAGGGCTCCAGATGGCACATTGTCAGAGGGACACACTGTGGCCCCTGTGCCCAGCCCTGGGCTCTCTGTACATGAAGCAACTCC \
 --guide_seq GATGTCTGCAGGCCAGATGA \
 -w 10 --write_cleaned_report --place_report_in_output_folder --output_folder ../cas_file/
done
```

```
--quantification_window_size：cas9 would be set to 1, Cpf1 this parameter would be set to 1, For base editors, this could be set to -17.
--quantification_window_center：Defines the size (in bp) of the quantification window extending from the position specified.
```
### 3.2 use oo2 analyse PE
针对点突的PE编辑类型
```
#!/bin/bash
for i in `cat acc1_name`
do
CRISPResso --fastq_r1 $i'_R1_cut.fq.gz' --fastq_r2 $i'_R2_cut.fq.gz' -qwc 50-123 --amplicon_seq ATTCCTGTGGGTGTTATAGCTGTGGAGACACAGACCATGATGCAGCTCATCCCTGCTGATCCAGGTCAACTTGATTCCCATGAGCGATCTGTTCCTCGGGCTGGACAAGTGTGGTTCCCAGATTCTGCAACCAAGACAGCTCAGGCATTATTAGACTTCAACCGTGAAGGATTGCCTCTGTTCATCCT --prime_editing_pegRNA_spacer_seq TTCCTCGGGCTGGACAAGTG --prime_editing_pegRNA_extension_seq AATCTGGGAACCCCACTTGTCCAGCCCGA --prime_editing_pegRNA_scaffold_seq GTTTAAGAGCTATGCTGGAAACAGCATAGCAAGTTTAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC --write_cleaned_report --place_report_in_output_folder
done
```
针对插入缺失的编辑类型
```
#!/bin/bash
for i in `cat 1_list`
do
  CRISPResso --fastq_r1 $i'_R1_cut.fq.gz' --fastq_r2 $i'_R2_cut.fq.gz' \
  --amplicon_seq CCAAAGGACCCCAGTCACTCCAGCCTGTTGGCTGCCGCTCACTTTGATGTCTGCAGGCCAGATGAGGGCTCCAGATGGCACATTGTCAGAGGGACACACTGTGGCCCCTGTGCCCAGCCCTGGGCTCTCTGTACATGAAGCAACTCC \
  --guide_seq GATGTCTGCAGGCCAGATGA \
  --expected_hdr_amplicon_seq CCAAAGGACCCCAGTCACTCCAGCCTGTTGGCTGCCGCTCACTTTGATGTCTGCAGGCCAGAATGGGAAGCTTCGAATGTCCTGCCTGGCTGTGGCTTCTCCTGTCCCTGCAAGCTTGGTCGGGGCTCCAGATGGCACATTGTCAGAGGGACACACTGTGGCCCCTGTGCCCAGCCCTGGGCTCTCTGTACATGAAGCAACTCC \
  --discard_indel_reads -w 10 --write_cleaned_report --place_report_in_output_folder --output_folder ../hdr_file/
done
echo "finished"
```
## view the result
use `bwa` and `samtools`

```
bwa index $refence_input
bwa mem -t 8 $refence_input $R1'_clean.fq.gz' $R2'_clean.fq.gz' |samtools view -bS -q 20 -|samtools sort -@ 60 - > $R1'.sorted.bam'
samtools index $R1'.sorted.bam'
```




