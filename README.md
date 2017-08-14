# LunchRoller

解决每日三大难题之中午吃什么。  

在你的电脑使用此脚本：  

1. 克隆repository
```bash
git clone https://github.com/cj24906zq/LunchRoller.git
```

2. 安装依赖包：`yaml`，`numpy` （或使用`virtualenv`）
```bash
cd LunchRoller
pip install -r requirements.txt
```

3. 运行`roll.py`，仅运行于`Python 2.7`下
```bash
python roll.py
```

4. (可选)在`~/bin/`中创建bash脚本
```bash
cd ~/bin/
vim roll
```
并输入
```bash
#! /bin/bash
python /PATH/TO/GIT/REPO/LunchRoller/roll.py $*
```
其中`/PATH/TO/GIT/REPO/`需替换成对应地址，从而可以实现在Console中直接运行`roll -arguments`  
  
  
额外配置：  
`-r`： 撤销上一次roll得的结果  
`-a candidate_abbr`： 弥补一次没roll的中饭，其中`candidate_abbr`  
```
    'Mc': '麦当劳',
    'cp': '土鸡星球',
    'MC': '市场创意',
    'p': '熊猫',
    'js': '就是沙拉',
    'cb': '转角烘焙店',
    'ch': '漆坡里'
```
`-v`： 查看本周的中饭记录  
`-s`： 查看上述备选的缩写  
`--add name1 --add name2 ...`，`--qty q1 --qty q2...`： 需配对使用，添加`name1`和`name2`到餐厅备择名单，并初始化本周到店次数为`q1`和`q2`  
`-c`： `candidates.yaml`的路径
