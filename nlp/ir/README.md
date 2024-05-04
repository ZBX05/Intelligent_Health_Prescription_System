# 问句意图识别子任务  

## 目录结构  

```text
ir                                      #问句意图识别子任务根目录
    |- Bert-TextCNN
    |- Bert-TextRCNN
    |- Bert-TextRNN
    |- Bert-TextRNN-Att
    |- data
        |- KUAKE-QIC                    #KUAKE-QIC原始数据文件
        *.json                          #数据文件
        processDataCMID.ipynb           #数据筛选、处理
        processDataKUAKE.ipynb          #数据筛选、处理

每一个实验的目录结构都近似相同，说明如下：
xxxxx                                   #某实验
    |- experiment                       #实验结果
        TrainLog.log                    #实验训练数据
    |- log
        TrainLog.log                    #训练日志文件
    execute.py                          #测试、训练功能的运行接口
    functionsAndClasses.py              #辅助函数（类）
    IRConfig.py                         #定义超参数变量
    main.py                             #程序运行文件
    model.py                            #模型定义、训练函数、验证函数
```
