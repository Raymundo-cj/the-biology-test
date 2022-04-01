## 生物信息学习笔记（一）

### 转录组生信数据分析
### 一、相关软件安装
1.1 Linux下安装anaconda
有两种安装方法：
1）通过Xftp和Xshell操作，在anaconda官网上面选择适合自己系统的版本，我这里是2021版Linux-X86-64位系统[下载链接](https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh)

2）通过Linux系统直接下载

```
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh 
```

1.2 镜像配置

```
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda
conda config --set show_channel_urls yes
```

这里使用的镜像是清华镜像

1.3 kingfisher工具下载
- Kingfisher是一个高通量测序数据下载工具，用户提供Run accessions或者BioProject accessions，即可在ENA、SRA、Amazon AWS以及Google Cloud等数据库中下载目标数据。Kingfisher会尝试从一系列的数据源进行数据下载，直到某个源能够work。

- 此外，还能根据用户的需求将下载数据直接输出为SRA、Fastq、Fasta或Gzip等格式，非常方便，不需要自己再对SRA数据通过fasterq-dump进行拆分转换

```
conda create -c conda-forge -c bioconda -n kingfisher pigz python extern curl sra-tools pandas requests aria2
#创建虚拟环境
conda activate kingfisher  
#使用conda activate不能成功激活环境时可以尝试使用：source activate kingfisher
pip install bird_tool_utils'>='0.2.17
git clone https://github.com/wwood/kingfisher-download
cd kingfisher-download/bin
export PATH=$PWD:$PATH
#配置环境变量
kingfisher -h  
#弹出帮助文档即安装成功
```

### 二、数据下载

```
kingfisher get -r SRP267791 -m ena-ascp ena-ftp prefetch aws-http
#-r Run number(s) to download/extract e.g. ERR1739691
#-p BioProject IDs number(s) to download/extract from e.g. PRJNA621514 or SRP260223
# -m ena-ascp、ena-ftp、prefetch、aws-http、aws-cp、gcp-cp
# --download-threads 线程数
```

- **-r**参数,只想下载某个确定的SRA数据,提供SRR Number即可，如 SRR12042866;
- **-p**参数，批量下载某个BioProject中的所有数据，提供BioProject Number，如PRJNA640275或SRP267791。

> ena-ascp,调用Aspera从ENA中下载.fastq.gz数据

> ena-ftp，调用curl从ENA中下载.fastq.gz数据

> prefetch，调用prefetch从NCBI SRA数据库中下载SRA数据，然后默认使用fasterq-dump对其进行拆分转换

> aws-http，调用aria2c从AWS Open Data Program中下载SRA数据，然后默认使用fasterq-dump对其进行拆分转换

> 也就是说，如果是用的ENA源 直接下载的就是fastq，如果用的SRA或其他，那就是下载SRA数据  然后kingfisher再自动调用fasterq-dump转换成fastq

SRA格式转换成fastq格式，调用fasterq-dump

```
kingfisher extract --sra SRR1574780.sra -t 20 -f fastq.gz
#-f,指定转换输出的文件格式，支持fastq,fastq.gz,fasta,fasta.gz
#-t，指定线程数
```


参考网址

[全外显子教程](https://mp.weixin.qq.com/s/y6NB8CPH73QGb17OsU9xPQ)

[kingfisher 公共测序数据 SRA/Fastq 下载神器](https://mp.weixin.qq.com/s?__biz=MzI3NzQ3MTcxMg==&mid=2247489784&idx=1&sn=c8fb03d42ed7f2b425d7ed38e64ee408&chksm=eb649077dc131961be2c52e46d8706074bc2f8d3f522971a6f5182a8893a65ea9349c43ca518&scene=21#wechat_redirect)

