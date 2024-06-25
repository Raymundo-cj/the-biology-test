
----------
## 1.数据下载方式
### 1.1 派森诺数据
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/629f5396-8623-42f0-b6fb-3fd4b656017f)

```
# 下载软件
https://genescloud.oss-cn-shanghai.aliyuncs.com/soft/public/oss/oss-browser-win64-v1.14.2.zip
# 在本地安装
```
之后可以通过提取码进行数据下载
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/8693841c-903f-4fa6-ad0e-1b95220a8e1e)


![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/d39a8099-9b88-4e68-961c-aaf4272aeec4)

### 1.2 吉因加数据

![](./images/1718612768515.png)![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/3fc32d8e-8949-461a-b71c-d07769f5474e)
直接通过链接在浏览器下载即可。

### 1.3 诺瀚数据
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/ce1938e5-f996-497a-9ff6-b0cdc9062a51)

批量处理需要下载华为云软件

```
https://support.huaweicloud.com/intl/en-us/browsertg-obs/obs_03_1003.html
```
粘贴相应的提取码就可以提取到数据。

**数据下载到本地后如何上传服务器**
用xshell登陆服务器，在xshell上面有上传文件的图标，点击图标就可以上传文件，如图所示：（或者用paracloud自带的文件传输软件Winspc同样可以进行文件传输操作）

![xftp界面展示](./images/1718623756537.png)
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/9fc86273-f216-4fe1-8684-95fb56ccab7d)

```
#一般情况下得到的文件为一个压缩包
#在本地解压后会得到一些测序数据文件，将这些文件上传到服务器，以下是操作步骤
cd ~/NGS_caojian
mkdir name_your_file # 这个自己写一个具有区分度的名称（英文）
cd name_your_file
mkdir raw_file
# 构建好文件后将fq.gz的数据传输到raw_file这个文件夹里面
```

### 2.数据质控及接头去除

在目录`name_your_file`下面进行操作：

```
# 第一步运行这段命令
bash caojian/script_file/run_clean.sh # 会生成一个run_clear.sh的文件

# 第二步提交任务
sbatch run_clear.sh # 可以用squeue进行查看
```
通过上述两个步骤就完成了数据的质控及去接头

### 3.生成bam文件
首先需要书写一个fasta文件，里面包含了自己的reference序列

```
# 编写reference文件
vim wt.fa # 或者在本地写完上传也可以

```
按照以下格式书写批量处理脚本`run_bam.sh`
```
vim run_bam.sh
```
之后将下面内容写进保存即可
```
#!/bin/bash
bash ~/caojian/script_file/get_bam.sh -f wt.fa -a r1.fq.gz -b r2.fq.gz
...
...
...
echo "finished"
```
上述文件可以在Excel中完成，之后运行脚本

```
sbatch run_bam.sh
#运行结束即可得到结果
```
### 4.计算编辑效率

首先需要在Excel中输入自己的编辑类型及相关参数，格式如下：

| 文件名称      | sgRNA                      | 编辑类型 | 参考序列                                                                                                                          | 预期序列    |
| ------------- | -------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| 6-4-60150-100 | tgactttgtcacagcccaagatagtt | cas9     | acactgaattcacccccactgaaaaagatgagtatgcctgccgtgtgaaccatgtgactttgtcacagcccaagatagttaagtggggtaagtcttacattcttttgtaagctgctgaaagttgtgtat |             |
| 6-4-60150-101 | tgactttgtcacagcccaagatagtt | PE       | acactgaattcacccccactgaaaaagatgagtatgcctgccgtgtgaaccatgtgactttgtcacagcccaagatagttaagtggggtaagtcttacattcttttgtaagctgctgaaagttgtgtat | aaaaaaaaaaa |
```
cd ~/NGS_caojian/name_your_file/cut_fasta 
# 进入这个文件夹
```
将Excel表格内容保存为`sample_target_sequence.txt`,并且上传到服务器中，目录`cut_fasta`文件夹中

之后运行下面这段代码
```
bash ~/caojian/script_file/get_crispross2.sh
```
会生成一个`run_crispresso2.sh`文件，之后提交任务
```
sbatch run_crispresso2.sh
```
运行结束会在当前目录下生成结果文件夹，有两个文件夹，一个为`cas9`一个为`result`，分别保存了cas9及PE的编辑效率分析结果文件。

**想要查看cas9编辑效率需要这样操作：**
```
cd cas9
# 计算编辑效率   222.csv为输出文件，可以改成任何你想命名的文件
python ~/yumeixia/script/count_effciency_from_crispresso2.py ./ 222.csv
# 对文件进行排序
sort -V 222.csv
# 查看最后文件的结果
cat 222.csv
```
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/9abbd8c6-6b4b-4608-9479-6fca4ab5ab1c)


* 第一列表示样本的名字
* 第二列表示编辑效率
* 第三列表示输入reads条数
* 第四列表示比对上reads条数
* 第五列表示未编辑reads条数
* 第六列表示编辑reads条数

**查看PE编辑效率需要以下操作**


```
cd result
# 计算编辑效率   222.csv为输出文件，可以改成任何你想命名的文件
python ~//caojian/script_file/get_result.py ./ 222.csv
# 对文件进行排序
sort -V 222.csv
# 查看最后文件的结果
cat 222.csv
```
![image](https://github.com/Raymundo-cj/the-biology-test/assets/64938817/6d7a564a-e609-454c-bacf-f5c0feb4d8cd)

* 第一列表示reads数
* 第二列表示编辑数量
* 第三列表示副产物数量
