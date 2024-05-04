# 后端模块  

## 目录说明  

**注意：** 如果想要使用HTTPS协议，则应该先确定拥有SSL证书及密钥并通过backend/config目录下的web_config.cfg文件设置这两个文件的路径，之后在frontend/js目录下的common.js更改网络通信协议类型，全部设置完毕后再对应用程序进行调整。  
**目前网络应用程序使用的是HTTPS协议，使用作者自签发的SSL证书，证书和对应的密钥并未上传至仓库。**

```text
backend                             #后端模块根目录
    |- config                       #存放配置文件以及其他需要加载的文件
        config.cfg                  #配置文件，记录参数等变量
        anatomy.txt                 #anatomy词表
        symptom.txt                 #symptom词表
        web_config.cfg              #Web应用程序配置文件
    functionsAndClasses.py          #辅助函数（类）
    parse.py                        #问句解析子模块，主要进行问句解析（命名实体识别、意图识别）
    model.py                        #模型类定义
    query.py                        #查询子模块
    generate.py                     #回答文本生成子模块
    dialog.py                       #后端上层接口类定义
    sql.py                          #数据库子模块，提供访问关系型数据库的软件接口
    web.py                          #Web应用程序代码
    run.py                          #运行系统
```  
