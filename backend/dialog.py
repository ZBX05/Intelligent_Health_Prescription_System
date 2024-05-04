import os
import random
from py2neo import Graph
from parse import Parser
from query import Query
from generate import Generator

class Dialog:
    def __init__(self,graph:Graph,too_long:int) -> None:
        self.graph=graph
        self.config_dir=os.getcwd()+'\\backend\\config\\config.cfg'
        self.disease_list_dir=os.getcwd()+'\\backend\\config\\disease.txt'
        self.symptom_list_dir=os.getcwd()+'\\backend\\config\\symptom.txt'
        self.anatomy_list_dir=os.getcwd()+'\\backend\\config\\anatomy.txt'
        self.drug_list_dir=os.getcwd()+'\\backend\\config\\drug.txt'
        self.check_list_dir=os.getcwd()+'\\backend\\config\\test.txt'
        self.cure_list_dir=[os.getcwd()+'\\backend\\config\\treatment.txt',os.getcwd()+'\\backend\\config\\operation.txt',
                            os.getcwd()+'\\backend\\config\\sport.txt']
        self.cure_list_dir,self.check_list_dir
        self.unknown='非常抱歉，您的问题超出了我的知识范围。请继续就其他方面进行提问或试着使用更清晰、更规范的语言描述问题。'
        self.parser=Parser(self.config_dir)
        self.query=Query(self.graph,self.disease_list_dir,self.symptom_list_dir,self.anatomy_list_dir,self.drug_list_dir,
                         self.cure_list_dir,self.check_list_dir)
        self.generator=Generator(self.unknown,too_long)
        self.mode='usr'
    
    def change_mode(self,mode:str='usr') -> None:
        if(mode!='usr' and mode!='dev'):
            raise ValueError(f'Invalid mode {mode}!')
        self.parser.set_mode(mode)
        self.mode=mode
    
    def respond(self,question_input:str) -> dict:
        parser_output=self.parser(question_input)
        query_data=self.query(parser_output)
        # return query_data
        entity_list=parser_output["ner_result"]["predictions_as_entity_list"]
        question_code=parser_output["ir_result"]["prediction"]
        generator_text=self.generator(entity_list,query_data,question_code)
        # generator_text=''
        if(self.mode=='usr'):
            return {"generator_text":generator_text}
        else:
            return {"parser_output":parser_output,"query_data":query_data,"generator_text":generator_text}
    
    def __call__(self,question_input:str,mode:str=None) -> dict:
        if(mode is not None):
            self.change_mode(mode)
            return self.respond(question_input)
        else:
            self.change_mode('usr')
            return self.respond(question_input)

def get_dialog(dialog:list|Dialog) -> Dialog:
    if(isinstance(dialog,Dialog)):
        return dialog
    elif(isinstance(dialog,list)):
        return dialog[random.randint(0,len(dialog)-1)]
    else:
        raise TypeError
    
if __name__=='__main__':
    graph=Graph(
            host='127.0.0.1',
            user='usr',
            password='medicalgraph2024'
            )
    dialog=Dialog(graph,2)
    # print(dialog('我是一名1型糖尿病患者，最近出现了胰岛素抵抗，去医院检查发现心血管有异常，报告还没出，想问一下这是什么情况？'))
    # print(dialog('我是一名1型糖尿病患者，目前有蛋白尿症状，检测出轻微肾小管损伤，想问一下这是什么病？'))
    print(dialog('糖尿病、CKD应该去哪家医院就诊')["generator_text"])
    # print(dialog('西格列汀有什么后果？','dev'))
    # print(dialog('我出现了心悸，糖尿，这是什么病？')["generator_text"])