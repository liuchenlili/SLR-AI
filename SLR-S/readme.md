**一、创建python 虚拟环境。**

```
conda create -n pytorch python=3.8.10
```

(ps.   pytorch >=1.10.1  <2.0 **GPU版本**)

**二、安装第三方库**

```
pip install -r requirements.txt
```

(版本号可以不完全一致, 可以先运行 缺少哪个安装那些)

**三、运行前端**

```
streamlit run app.py
```

**四、训练和测试**

选择模型 提供 R3D ，R2+1D， LSTM+Resnet等

可以在train.py  第144行 去注释和取消注释

```
# path
data_path = "../SLR_Dataset/CSL_Isolated/color_video_25000"
label_path = '../SLR_Dataset/CSL_Isolated/dictionary.txt'
```

需要修改train.py的路径

日志文件产生在logs文件夹里

**五、文件说明**

data 存放 上传的视频等必要数据

logs 日志文件夹

video 存放中转的抽帧图像

weight 存放的训练的权重

app.py 前端的主要代码

dataset.py  手语数据集的dataset类代码

model.py  模型的代码

predication.py  预测单个视频

real.py 实时识别主要代码

demo.py  实时识别的demo(无前端)

test,py 测试代码（混淆矩阵 和 准确率）

tool.py  工具类代码

train,py 训练代码

**说明**
要训练的话，要改数据集路径