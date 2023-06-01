## 这篇文章想要记录一下二代测序数据分析的一些情况
### 1.二代测序数据
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/0345d56c-743a-4ae5-8e7d-4707d18da0f7)

根据样本拆分好的数据

### 2.服务器数据分析
* 本次分析在服务器pg3152，运行下面代码前先激活conda环境：`source activate /public3/home/pg3152/anaconda3/bin/envs/caocao`
* 路径介绍：这里写这篇记录的路径为`/public3/home/pg3152/caojian/ngs/test`
* 保存的测序文件在`/public3/home/pg3152/caojian/ngs/test/gene_ngs`
* 编辑位点的序列数据保存在`/public3/home/pg3152/caojian/ngs/test/gene_acc`
* 这里需要记住一点需要运行`bwa index acc1.fasta`生成索引文件，不然后续运行程序会报错
* 结果文件保存在`/public3/home/pg3152/caojian/ngs/test/result`

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
之后将得到的gene_list文件复制到result文件夹下，执行操作`cp -r gene_list ~/caojian/ngs/test/result`

2.2 **在result文件夹中创建bam文件夹**

运行下面的代码：

```
#!/bin/bash
awk -F "/" '{print "bwa mem -t 60 ~/caojian/ngs/test/gene_acc/acc1.fasta "$0"_R1_001.fastq.gz "$0"_R2_001.fastq.gz|samtools view -bS-q 20 |samtools sort -@ 60 > ./bam/"$NF"_sorted.bam"}' gene_list |head |bash -
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












