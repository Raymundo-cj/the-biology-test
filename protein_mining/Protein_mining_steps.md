## 这个文档是在整理蛋白挖掘的步骤及注意的事项（备忘录）

本次挖掘基于已经发表了的pAgo进行宏基因组的挖掘工作，已经发表的pAgo蛋白数量为269

### 1.宏基因组数据的预处理
由于blast在遇到大片段重复的序列时会报错，所以需要过滤掉<200aa和大片段重复序列，同时因为数据量大需要将序列进行拆分

```
#经过过滤得到长度大于200aa的蛋白质用于后续分析
perl find_protein_length_200.pl metagenome.pep.fasta metagenome.pep.length200.fasta 
#删除具有大片段重复的序列，得到没有大片段重复的蛋白质数据
python delete_repeat_fasta2.py metagenome.pep.length200.fasta filter.list
sed 's/>//' filter.list > filter_sed.list  #删除这个文件中的“>”符号，以免在后续步骤中出现错误
grep ">" metagenome.pep.length200.fasta |sed 's/>//'|cat - filter_sed.list |sort|uniq -u >metagenome.pep.filter.list
# '|'的意思是管道符号，以上一条命令的输出作为本次命令的输入

#grep命令：能使用正则表达式搜索文本，并把匹配的行打印出来；

# sed命令：是一种流编辑器，它一次处理一行内容，在处理时，把当前处理的行存储在临时缓存区中，又被称为模式空间，接着用sed命令处理缓冲区中的内容，处理完成后，把缓冲区的内容送往屏幕。在本次代码中sed表示删除了前一步提取的fasta文件序列号list文件里面的“>”号；

# cat命令：是Linux下的一个文本输出命令，通常是用于观看某个文件的内容主要有三大功能：1）一次显示整个文件；2）从键盘创建文件；3）将几个文件合并为一个文件；

# sort命令：在这里表示安装默认情况将输入的文本排序；

# uniq命令：在这里表示只显示出现一次内容的行（不允许重复行出现）

perl /public1/home/scb8190/git_hub/CRISPR/extract_unfind_fa.pl metagenome.pep.length200.fasta metagenome.pep.filter.list metagenome.pep.filter.fasta  #从原始数据库中根据筛选的序列号找到其对应的fasta序列。
```

对数据进行分批，这里也是采用了Perl命令

```
#!/bin/bash
perl fasta-splitter.pl --n-parts 9 /public1/home/scb8190/caojian/Ago/metagenome2/metagenome2.pep.filter.fasta
```
## 2.数据的正式处理

### 2.1.1 psi-blast(蛋白序列比对)方法一

```
#!/bin/bash
#SBATCH -p amd_256
#SBATCH -N 1
#SBATCH -n 64
psiblast -query /public1/home/scb8190/caojian/Ago/metagenome2/fasta_file/metagenome2.pep.filter.part-1.fasta -evalue 1e-7 -inclusion_ethresh .002 -db /public1/home/scb8190/caojian/Ago/PIWI/pAgo_PIWI.pep -num_iterations 3 -seg yes -outfmt '7 std qseq sseq stitle' -out metagenome_pAgo_PIWI_1.output -max_target_seqs 500 &
wait
echo "finish"
```
这不完成跳到下面一步**步骤2.2 **

### 2.1.2 MMseq（蛋白序列比对）

```
mmseqs createdb /public1/home/scb8190/yumeixia/Ago/PIWI/database/pAgo_PIWI.fasta pAgo_DB 
#将我们已经知道的序列生成为一个对比库
mmseqs createdb ~/shared_public_data/metagenome_data/split_12_repeat_filter/metagenome.pep_1_filter.fasta metagenome.pep_1_DB
mmseqs search metagenome.pep_1_DB pAgo_DB result_1_DB 1.tmp --start-sens 4 --sens-steps 4 -s 7 -e 1e-6
mmseqs convertalis metagenome.pep_1_DB pAgo_DB result_1_DB  mmseqs_1_results.txt
```
这里得到TXT文件之后需要在这些TXT文件中提取蛋白序列号：

```
#!/bin/bash
#SBATCH -p amd_256
#SBATCH -N 1
#SBATCH -n 64
awk '{print $1}' mmseqs_2_results.txt | sort|uniq  > mmseq_2_result.list &
wait
echo 'finished'
```
之后则根据序列号拿到fasta文件，同时也要对fasta文件进行蛋白序列去冗余即“cd-hit”，然后根据去冗余的序列再次得到蛋白的氨基酸序列号，以便进行下一步分析。


这里进行结束直接跳到**步骤2.5**

### 2.2 提取比对后序列号

```
#!/bin/bash
#SBATCH -p amd_256
#SBATCH -N 1
#SBATCH -n 64
sed '/#/d' metagenome_pAgo_PIWI_1.output|awk '{print $1}'|sort|uniq >metagenome2_pAgo_PIWI_1.list &
wait
echo "finished"
```
### 2.3 提取比对后的序列

```
#!/bin/bash
seqtk subseq  ~/shared_public_data/metagenome_data/meta2/metagenome2.pep.fasta metagenome2_pAgo_PIWI_1.list >metagenome2_pAgo_PIWI_1.fasta &
wait
echo "finished"
```

### 2.4 序列合并去重并得到序列号

```
cat *.fasta > Ago_result.fasta
cd-hit -i Ago_result.fasta -o Ago_result_hit.fasta  -c 1 -d 0 #对序列进行去冗余操作
grep '>' Ago_result_hit.fasta|sed 's/>//'|awk '{print $1}' > Ago_result_hit.list # 去冗余就蛋白序列号的获取
```
### 2.5 进行蛋白质注释

```
sort Ago_psi_result_hit.txt ../MMseq/MMseq_Ago_result_hit.txt|uniq >../putative_Ago.list  #将MMseq和psi-blast两者得到的序列名称做一个交集！！！
perl /public1/home/scb8190/git_hub/CRISPR/extract_unfind_fa.pl metagenome.pep.length200.fasta putative_Ago.list putative_Ago.fasta
hmmscan --domtblout putative_Ago.dbl --tblout putative_Ago.tbl --noali -E 1e-2 --cpu 30 /public1/home/scb8190/Test/CRISPR/Pfam/Pfam-A.full.uniprot.hmm putative_Ago.fasta
```
### 2.6 提取Piwi domain

```
grep 'Piwi' putative_Ago.dbl|awk '{print $4}'|sort|uniq >domain_result.list
seqtk subseq ~/shared_public_data/metagenome_data/split_12_repeat_filter/metagenome.pep_filter.fasta domain_result.list >domain_result.fasta
```
### 2.7 序列比对及进化树构建

```
mafft --maxiterate 1000 --thread 50 --localpair domain_result.fasta  >domain_result_mf.fasta
```

使用mafft命令 [详细介绍mafft的网站](https://www.cnblogs.com/zhanmaomao/p/12115957.html)

进化树法构建

```
iqtree -s domain_result_mf.fasta -m MFP -B 1000 -T 30  -alrt 1000
```
建树完成后所提取的文件 domain_result_mf.fasta 再导入[itol](https://iqtree.org)这个网站进行可视化

