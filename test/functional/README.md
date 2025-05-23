# 功能测试  

此部分主要针对系统完成已有功能的能力进行测试，涉及功能测试的功能如下：  

* 医疗对话  
* 知识图谱展示  
* 知识图谱展示（搜索结点）  

## 测试计划  

* 采用Selenium进行测试；
* 针对医疗对话功能的测试目前计划人工构造100条问题，测试对话功能的准确性；  
* 针对知识图谱展示功能的测试目前计划使用压力测试工具，通过多次登录账号-触发知识图谱展示功能-退出账号的测试计划测试系统展示知识图谱这一功能是否能够稳定运行；  
* 针对知识图谱展示（搜索结点）功能的测试目前计划人工构造包含100条测试数据的测试集，测试知识图谱的完备程度。

**注意** 测试结果中，部分标记过程使用手动标记的方法。  

## 目录结构  

```text  
functional                              #功能测试根目录
    |- dialog                           #医疗对话功能测试
        dialogTest.py                   #测试脚本
        run.ipynb                       #测试脚本执行文件
        dialog.csv                      #测试数据
        result.csv                      #原始测试结果
        marked.csv                      #进行准确性标记后的结果
        final.csv                       #最终测试结果
    |- graph                            #知识图谱展示功能测试
        graphTest.py                    #测试脚本
        run.ipynb                       #测试脚本执行文件
        result.csv                      #测试结果
    |- node                             #知识图谱展示（搜索结点）功能测试
        nodeTest.py                     #测试脚本
        run.ipynb                       #测试脚本执行文件
        node.csv                        #测试数据
        result.csv                      #测试结果
```
