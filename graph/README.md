# 知识图谱构建模块  

## 目录说明  

```text
graph                                       #知识图谱构建模块根目录
    |- data                                 #数据
        |- diakg                            #瑞金医院糖尿病数据
            1.json
            ...
            41.jon
        |- extractedData
            extracted.json                  #经过抽取的疾病数据
        |- spiderData
            sport.json                      #从39健康网爬取的运动数据
            knowledge.json                  #从39健康网疾病百科爬取的疾病数据
    |- dict                                 #外部词典（主要用于分词）
        baidu_stopwords.txt
        sport_dict.txt
        stopwords.txt
        THUOCL_medical.txt
    |- log
        |- buildMedicalGraphLog.log         #构建知识图谱脚本程序的debug日志
    |- txt                                  #知识图谱构建过程生成的词典
        ade.txt
        ...
        treatment.txt
    关系.png
    实体.png
    addData.py                              #向知识图谱中添加运动数据
    buildMedicalGraph.py                    #构建知识图谱的脚本程序
    knowledgeSpider.py                      #爬取疾病数据的爬虫脚本
    knowledgeExtraction.py                  #爬取并抽取疾病数据
    manuallyCorrect.py                      #对个别错误数据进行手动矫正
    sportSpider.py                          #爬取运动数据的爬虫脚本
```  
