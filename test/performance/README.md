# 性能测试  

此部分主要针对系统性能进行测试，采用的测试软件为Jmeter进行涉及性能测试的功能如下：  

* 登录  
* 医疗对话  
* 知识图谱展示  
* 知识图谱展示（搜索结点）  
* 历史记录  

## 测试计划  

* 采用Apache JMeter进行测试；
* 针对每一功能构造基于HTTP请求的测试计划；
* 测试结果分别保存于每一功能的目录下。

## 目录结构  

```text  
performance                             #压力测试根目录
    |- dialog                           #医疗对话功能压力测试
    |- graph                            #知识图谱展示功能压力测试
    |- history                          #历史记录功能压力测试
    |- login                            #登录功能压力测试
    |- node                             #知识图谱展示（搜索结点）功能压力测试
    register.ipynb                      #该脚本用于向MySQL数据库批量插入测试账号数据
    user.csv                            #测试账号的邮箱、密码数据

#各功能目录结构示例：
performance
    |- function                         #某功能压力测试目录
        |- report                       #测试工具生成的测试报告目录
            |- *                        #前端文件存放目录
            statistic.json              #测试数据
            index.html                  #测试报告
        *.jmx                           #测试计划文件
        jmeter.log                      #测试程序的运行日志
        result.csv                      #测试结果
        test.bat                        #运行该批处理程序即可开始测试

```  
