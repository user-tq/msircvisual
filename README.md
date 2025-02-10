本脚本的大量代码来自于 mantis2 ，感谢 mantis2 的作者。

另外也感谢达安基因，这个图片是对他们展示结果的复刻，但他们的分析代码是非开源的。

## 依赖

```
numPy
pysam
matplotlib
scipy
pandas
```

## 运行方式

### 1. tumor-normal 绘图

```
python msircvisual.py  -t tumor.bam \
-n normal.bam  -b source/msi.bed  -o test/test.png --genome /mnt/store/pipeline/snakemake/somatic_pipeline/source/Homo_sapiens/GATK/GRCh37/Sequence/WholeGenomeFasta/human_g1k_v37_decoy.fasta
```

### 2. 单样本绘图(带有基线)

- 获取基线

```
python get_rc_distribution_baseline.py  -n  *.normal.bam \
-b source/msi.bed \
--genome human_g1k_v37_decoy.fasta \
-o source/msircvisual_baseline.txt
```

- 运行 msircvisual.py

```
python msircvisual.py  -bsl source/msircvisual_baseline.txt  -t tumor.bam -b source/msi.bed -o test/test.png --genome human_g1k_v37_decoy.fasta
```

### 3. 单样本绘图(无基线)

```
python msircvisual.py  -t tumor.bam -b source/msi.bed -o test/test.png --genome human_g1k_v37_decoy.fasta
```

### bed 文件要求

bed 文件的第四列需要注意：

需包含 repeating k-mer 与 repeat count 以及 repeat name，用括号括起来，例如：(T)28[MONO-27]

```
2	39564893	39564921	(T)28[MONO-27]
```

demo 见 [msibed](./source/msi.bed)

## 结果展示

![ouput](./test/test.png)

## 参数

msircvisual.py

- normal：正常样本的 bam 文件
- baseline：基线的 tsv 文件，
- tumor：tumor 样本的 bam 文件，必须
- bedfile：bed 文件，必须
- output：输出的 png 文件，必须
- mrn：最大的重复次数，超过这个次数将不被统计，默认 60
- mrq：最小的平均质量值，参考 mantis2
- mlq：最小的平均 locus 质量值，参考 mantis2
- mrl：最小的读长，参考 mantis2
- threads：线程数
- genome：参考基因组文件
- debug_output：是否打印 debug 信息，参考 mantis2

## 其它

关于 Mann-Whitney U 检验的获取 p 值的部分，或许存在一些统计上的不严谨，抱歉我确实不擅长这些。
