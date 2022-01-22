# VOC 格式数据集转 YOLO v5 脚本

## 使用方法

```bash

usage: voc_to_yolo.py [-h] --input INPUT --output OUTPUT

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    Directory location of your VOC, where JPEGImage and Annotations located, assumed train_list.txt and val_list.txt exist
  --output OUTPUT  Directory location you want your output yolo dataset
```

### 输入目录:

目录结构:

```bash
❯ ls
Annotations  JPEGImages  train_list.txt  val_list.txt
```

### 示例指令

    python3 voc_to_yolo.py --input VOC2007 --output yolo


### 输出目录

选择一空白文件夹,在执行指令后将产生如下文件:

    ❯ ls
    dataset.yaml  images  labels  yolo_train_list.txt  yolo_val_list.txt

其中 dataset.yaml 为 yolo v5 所需配置文件,yolo_train_list.txt 和 yolo_val_list.txt 是根据VOC划分数据集生成的对应目录.

dataset.yaml中,path地址需要更改为**相对 yolo 源码代码根目录的地址 或 绝对地址**

