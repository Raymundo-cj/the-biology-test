# how to analyse the NGS data
## 1.data splite
we use `fastq-multx` to splite data
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



