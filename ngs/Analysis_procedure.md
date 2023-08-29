## 这篇文章主要记录二代测序数据拆分及如何分析编辑效率
### 前期数据拆分

**1.获取测序文件的index与测序序列的之间的关系文件**

```
perl s0_get_barcode_pairs_id.pl D2A_S41_L001_R1_001.fastq.gz D2A_S41_L001_R2_001.fastq.gz > barcode_req_id
```

```
# s0_get_barcode_pairs_id.pl

#!/usr/bin/perl -w
use strict;
open R1,"zcat $ARGV[0]|" or die;
open R2,"zcat $ARGV[1]|" or die;

my %hash_barcode1;my %hash;my %hash_pairs;

while(<R1>){
        chomp;
        my @ss=split/\s/,$_;
        my $header=$ss[0];
        chomp(my $sequence=<R1>);
        chomp(my $comment=<R1>);
        chomp(my $quality=<R1>);
        $sequence =~ /GCTT(.+?)TGGAGTGAGTACGGTGTGC/; my $barcode1= $1;
        if (length($barcode1)==4){
                $hash_barcode1{$header} = $barcode1;
        }
}
# 这里面的序列长度和序列是可以自己切换修改的，根据自己的数据情况,替换的部位是上面及下面的sequence位置
my $header;my $pairs;
while(<R2>){
        chomp;
        my @ss=split/\s/,$_;
        $header=$ss[0];
        chomp(my $sequence=<R2>);
        chomp(my $comment=<R2>);
        chomp(my $quality=<R2>);
        $sequence =~ /CTGT(.+?)TGAGTTGGATGCTGGATGG/; my $barcode2= $1;
        if (length($barcode2)==4){
                $pairs = $hash_barcode1{$header}."_$barcode2";
                if (exists $hash_pairs{$pairs}){
                        $hash_pairs{$pairs} = $hash_pairs{$pairs}."\t$header";
                }else{
                        $hash_pairs{$pairs} = $header;
                }
        }
}
foreach my $key (keys %hash_pairs){
        print "$key\t$hash_pairs{$key}\n";
}
```
**2 根据reads拆分文库**

根据上面得到的文件`barcode_req_id`及`adapter_seq_list`文件，获取每个样品的测序数据ID：

```
mkdir barcode_out
cat adapter_seq_list |while read name bar;do grep $bar barcode_req_id >barcode_out/$name;done

```
adapter_seq_list:

![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/58fdbc64-f0af-4389-bc40-3f4801f413f8)

barcode_out:及里面内容

![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/7513a809-5cb2-4a9b-96d4-41da57055996)

之后根据样品的序列ID拿到每个样品的序列，并且一个样品一个序列文件：

```
#!/bin/bash
mkdir all_library
for file in barcode_out/*
do
    perl s1_get_r1_seq.pl $file ~/lzy/lzyngs/1-LZY_S1_L003_R1_001.fastq.gz
    perl s1_get_r2_seq.pl $file ~/lzy/lzyngs/1-LZY_S1_L003_R2_001.fastq.gz
done

```

这样就会得到一些数据文件，之后转化为自己文件命名的格式

```
cd all_library
mv GCGT_GCGT_R1.fastq 259_R1.fastq
mv GCGT_GTAG_R1.fastq A7_R1.fastq
mv GCGT_ACGC_R1.fastq VB7_R1.fastq
mv GCGT_GCTC_R1.fastq T10cr2-4_R1.fastq
mv GCGT_AGTC_R1.fastq T10cr4-2_R1.fastq
mv GCGT_GATG_R1.fastq T10_R1.fastq
```

### 1.二代测序数据
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/0345d56c-743a-4ae5-8e7d-4707d18da0f7)

根据样本拆分好的数据

## 基因编辑效率统计的两种方法

### 方法一：基于CRISPRoss2软件进行序列分析

分析前环境设置：

* 软件分析方法在服务器scb8190上面进行，在分析结果之前先激活conda环境`conda activate crispresso2_env`
* 路径介绍：示例路径为`/public1/home/scb8190/caojian/ngs/data_8_9/acc1`

因为需要实现批量处理，所以需要在运行下面代码获取测序数据文件名称

```
for i in `ls $1`; do echo $i >> acc1_list; done
sed -i 's/_R1_001.fastq.gz//g' acc1_list
sed -i 's/_R2_001.fastq.gz//g' acc1_list
sort file_list |uniq  > acc1_gene
```
上述代码需要一条一条分开执行

针对测序数据来说，可能存在index未去除干净的情况发生，所以可以根据自己测序数据的情况看是否需要清除并自己进行一次测序数据过滤

```
#!/bin/bash
for i in `cat acc1_gene`
do
cutadapt -g CTGCAAGGCGATTAAGTTGGGTA -G GCAGTGAGCGCAACGCAATT -e 0.1 -O 5 -m 50 -o $i'_R1_cut.fq.gz' -p $i'_R2_cut.fq.gz' $i'_R1.fq.gz' $i'_R2.fq.gz'
done
```

* -g:测序数据R1端的index
* -G:测序数据R2端的index
* -o及-p：输出文件名称
* 其余为输入文件名称

上面完成后就可以用软件分析编辑效率了，自己分析的是prime editing编辑效率，如果需要分析其他类型编辑效率，请在[参考文档](https://github.com/pinellolab/CRISPResso2)中查找参数含义！
分析prime editing例子

```
#!/bin/bash
for i in `cat acc1_gene`
do
CRISPResso --fastq_r1 $i'_R1_cut.fq.gz' --fastq_r2 $i'_R2_cut.fq.gz' -qwc 50-123 --amplicon_seq ATTCCTGTGGGTGTTATAGCTGTGGAGACACAGACCATGATGCAGCTCATCCCTGCTGATCCAGGTCAACTTGATTCCCATGAGCGATCTGTTCCTCGGGCTGGACAAGTGTGGTTCCCAGATTCTGCAACCAAGACAGCTCAGGCATTATTAGACTTCAACCGTGAAGGATTGCCTCTGTTCATCCT --prime_editing_pegRNA_spacer_seq TTCCTCGGGCTGGACAAGTG --prime_editing_pegRNA_extension_seq AATCTGGGAACCCCACTTGTCCAGCCCGA --prime_editing_nicking_guide_seq CAAGTTGACCTGGATCAGCA --prime_editing_pegRNA_scaffold_seq GTTTAAGAGCTATGCTGGAAACAGCATAGCAAGTTTAAATAAGGCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC --write_cleaned_report --place_report_in_output_folder
done
```

* --fastq_r1：R1序列 --fastq_r2 ：R2序列
* -qwc ：统计编辑副产物窗口
* --amplificon_seq ：目标序列
*  --prime_editing_pegRNA_spacer_seq ：不含PAM的spacer
*  --prime_editing_pegRNA_extension_seq ：RTT及PBS
*  --prime_editing_nicking_guide_seq ：如果有nicking序列需要添加这段序列，没有可以不加
*  --prime_editing_pegRNA_scaffold_seq ：scaffold序列
*  --write_cleaned_report --place_report_in_output_folder：限制输出格式的参数，需要添加，不同的编辑类型输出格式会有出入，需要根据[参考文档](https://github.com/pinellolab/CRISPResso2)进行选择

后续的结果会以网页的格式展示出来，直接统计编辑效率及副产物占比，若需要查看其他输出文件，请根据参考文档自行查看。



### 方法二：实验室前期用于base editing分析的方法

* 本次分析在服务器pg3152，运行下面代码前先激活conda环境：`source activate /public3/home/pg3152/anaconda3/bin/envs/caocao`
* 路径介绍：这里写这篇记录的路径为`/public3/home/pg3152/caojian/ngs_test/ngs`
* 保存的测序文件在`/public3/home/pg3152/caojian/ngs_test/ngs/test/gene_ngs`
* 编辑位点的序列数据保存在`/public3/home/pg3152/caojian/ngs_test/ngs/test/gene_acc`
* 这里需要记住一点需要运行`bwa index acc1.fasta`生成索引文件，不然后续运行程序会报错
* 结果文件保存在`/public3/home/pg3152/caojian/ngs_test/ngs/test/result`

2.1 因为需要做到批量处理，需要在测序文件`cd gene_ngs`中运行以下一段代码：

```
for i in $(ls $1)
do 
echo $(realpath $i) >> file_list 
done

sed -i 's/_R1_001.fastq.gz//g' file_list
sed -i 's/_R2_001.fastq.gz//g' file_list
sort file_list |uniq  > gene_list
```
之后将得到的gene_list文件复制到result文件夹下，执行操作`cp -r gene_list ~/ngs_test/ngs/test/result`

2.2 **在result文件夹中创建bam文件夹**

运行下面的代码：

```
#!/bin/bash
awk -F "/" '{print "bwa mem -t 60 ~/caojian/ngs_test/ngs/test/gene_acc/acc1.fasta "$0"_R1_001.fastq.gz "$0"_R2_001.fastq.gz|samtools view -bS-q 20 |samtools sort -@ 60 > ./bam/"$NF"_sorted.bam"}' gene_list |head |bash -
echo "finished"
```
会在result文件中得到bam文件

![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/1259f2e5-5c82-4acd-8f55-6a938d83c884)


2.3 **从bam文件中得到每个位置碱基的个数**

之后在bam文件中运行上面批处理的代码，得到bam文件的批量处理路径`acc1_bam_list`，将这个文件复制到result文件目录下，在这个目录执行这命令
```
#!/bin/bash
awk -F "/" '{print "bam-readcount -w 1 -f ~/caojian/ngs/test/gene_acc/acc1.fasta "$0" |awk '\''BEGIN{FS=OFS=\"\t\"}{split($6,A,\":\");split($7,C,\":\");split($8,G,\":\");split($9,T,\":\");print $1,$2,$3,$4,\"A:\"A[2],\"C:\"C[2],\"G:\"G[2],\"T:\"T[2]}'\'' > ./baw_count/"$NF"_out"}' acc1_bam_list | bash -
echo "finished"
```
得到的文件就是每个位置碱基的数量文件。

![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/0cc5ffe3-1339-4fc3-9e6f-1b2a50bb3ac6)


2.4 **从碱基数文件得到碱基占比文件**

同样执行一次批处理的代码，得到`bam_count`这个文件，后续需要需要执行代码如下：

```
#!/bin/bash
awk -F "/" '{print "perl r4_change_format.pl "$0" > ./baw_percent/"$NF"_percent"}' bam_count | bash -
echo "finished"
```
执行结束就能拿到每个位置碱基占比的文件了，之后将文件下载至本地进行分析即可。

![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/ccf1b364-cbb4-4c53-83ce-e283f29b4e68)

这一步出现的perl文件，代码如下：

```
#!/usr/bin/perl -w
use strict;

open F,$ARGV[0] or die;

print "Chr\tPosition\tRef\tDepth\tA\tC\tG\tT\n";
while(<F>){
	chomp;
	my @ss = split/\t/,$_;
	my @aa = split/:/,$ss[4];my $a_precent = $aa[1]/$ss[3];
	my @cc = split/:/,$ss[5];my $c_precent = $cc[1]/$ss[3];
	my @gg = split/:/,$ss[6];my $g_precent = $gg[1]/$ss[3];
	my @tt = split/:/,$ss[7];my $t_precent = $tt[1]/$ss[3];
	print "$ss[0]\t$ss[1]\t$ss[2]\t$ss[3]\t$a_precent\t$c_precent\t$g_precent\t$t_precent\n";
}
```
### 3.本地处理

下面这段python代码是为了筛选在某一个比例下碱基的占比：
```
import pathlib

p1 = pathlib.Path("t1").rglob("*sorted.bam_out_percent")
for fi in p1:
    with open("t2/"+str(fi.name)+"_fliter.txt","w") as fo:
        fi = open(str(fi.absolute()),"r")
        next(fi)
        fi = fi.readlines()
        for lines in fi:
            line = lines.strip().split("\t")
            value_list = [float(x) for x in line[4:8]]
            key_list = ["A","C","G","T"]
            dic = dict(zip(key_list,value_list))
            for k,v in dic.items():
                if v >=0.005 and k != line[2]:
                    fo.write(line[0]+"\t"+line[1]+"\t"+line[2]+"\t"+str(v)+"\t"+k+'\n')
```
针对上面得到的文件，可以简单画图图形：

```
import matplotlib.pyplot as plt

data = []
with open('ACC1-1_S1_L001_sorted.bam_out_percent_fliter.txt', 'r') as f:
    for line in f:
        line = line.strip().split('\t')
        data.append(line)
# 提取X轴和Y轴数据
x = [float(d[1]) for d in data]
y = [float(d[3]) for d in data]
# 提取X轴标签
xticks = [f"{d[2]}\n{d[4]}\n{d[1]}" for d in data]
# 绘制图形
fig, ax = plt.subplots()
plt.xticks(rotation=45)
bars=ax.bar(x, y, tick_label=xticks)
for bar in bars:
    height = bar.get_height()
    ax.annotate(f"{height:.4f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), 
                textcoords="offset points",
                ha='center', va='bottom',rotation=90) 

    plt.show()
```

