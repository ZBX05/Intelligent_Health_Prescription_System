# 自然语言处理模块  

预训练模型应存放的路径：./model/pytorch_model.bin  
获取ner模型权重后应将权重文件按以下路径保存：./model/ner/model_state.pth  
获取ir模型权重后应将权重文件按以下路径保存：./model/ir/model_state.pth  

## 目录结构  

```text
nlp                                     #自然语言处理模块根目录
    |- data                             #数据
        |- 中文NER处理后数据
        |- 中文NER未处理数据
    |- ir                               #问句意图识别子任务
    |- ner                              #问句命名实体识别子任务
    |- model                            
        bert_config.json
        config.json                     #Bert预训练模型超参数
        vocab.txt                       #分词词表
```  
