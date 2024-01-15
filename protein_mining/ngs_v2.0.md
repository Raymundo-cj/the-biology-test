# 二代测序数据的两种分析方法

### 运行环境介绍
1.并行服务器scb8190
2.文件运行路径：`/public1/home/scb8190/caojian/ngs/`
3.激活环境命令：
```
source ~/.bashrc1
source activate base
# 在base环境下可以使用本次分析的软件minimap2和samtools这两个软件
conda activate cutadaptenv
# 有接头序列需要切除时执行这段命令
```
## 方法一、可视化分析

### 1.切除接头序列

首先需要激活cutadapter软件的环境`conda activate cutadaptenv` ,之后执行下面的命令将测序数据的接头去掉
```
#!/bin/bash
for i in `cat name_sor.list`
do
 cutadapt -g CTGCAAGGCGATTAAGTTGGGTA -G GCAGTGAGCGCAACGCAATT -e 0.1 -O 5 -m 30 -o '../cut_fq_file/'$i'_R1_cut.fq.gz' -p '../cut_fq_file/'$i'_R2_cut.fq.gz' $i'_raw_1.fq.gz' $i'_raw_2.fq.gz'
done
echo "finished!"
```
1）这里的`-g` 后面的序列对应5'的测序接头，`-G`则对应3'的测序接头，可以根据自己实际序列进行修改；
2）`-o`和`-p`参数则为输出序列的名称；
3）后面两个`fq.gz`则分别对应测序数据的5'和3'。
### 2.利用minimap2软件将测序数据与原始序列进行比对

```
#!/bin/bash
for i in `cat name_list`
do
 minimap2 -t 64 -ax sr wh_1.fasta '/public1/home/scb8190/caojian/ngs/data_lys/lys_date/00.mergeRawFq/cut_fq_file/'$i'_R1_cut.fq.gz' '/public1/home/scb8190/caojian/ngs/data_lys/lys_date/00.mergeRawFq/cut_fq_file/'$i'_R2_cut.fq.gz' >$i'.sam'
done
echo "finished"
```
1）`sr` 后面对应自己的原始序列；
2）`fq.gz`则分别对应切除接头的5'和3'序列；
3）运行结束或生成`sam`文件，不能直接查看，需要转化为`bam`文件。

### 3.将`sam`转化为`bam`

```
#!/bin/bash
for i in `cat name_list`
do
 samtools view -bS -q 30 $i'.sam'|samtools sort -@ 16 > $i'.bam'       
 samtools index $i'.bam'
done
echo "finished"
```
将上述结果的`bam`和`bam.bai`文件同时下载到本地，就可以在IGV中进行可视化了。

## 方法二、编辑效率分析




