from py2neo import Graph
from typing import Any
from functionsAndClasses import get_most_similar_string,has_alpha

def get_relation_type(short_entity_type:str,target_entity_type:str,diagnosis:bool=False) -> list:
    '''关系类型映射'''
    entity_type=[]
    if(short_entity_type=='dise'):
        entity_type.append('Disease')
        if(diagnosis):
            entity_type.append('Symptom')
    elif(short_entity_type=='body'):
        entity_type.append('Anatomy')
    elif(short_entity_type=='symp'):
        entity_type.append('Symptom')
    elif(short_entity_type=='drug'):
        entity_type.append('Drug')
    elif(short_entity_type=='chec'):
        entity_type.append('Test')
    elif(short_entity_type=='cure'):
        entity_type.append('Treatment')
        entity_type.append('Operation')
    relation_type=[e+'_'+target_entity_type for e in entity_type]
    return relation_type

# def get_property_type(short_entity_type:str) -> str:
#     '''实体属性类型映射'''
#     if(short_entity_type=='body'):
#         return 'anatomy'
#     elif(short_entity_type=='symp'):
#         return 'symptom'
#     else:
#         return 'symptom'

# def filter_entity_list(entity_list:list,entity_type_list:list,disease_dict:dict=None) -> list:
#     '''按照类型对实体进行过滤'''
#     filtered_entity_list=[]
#     for entity in entity_list:
#         if(entity[1] in entity_type_list and entity[1]!='dise'):
#             filtered_entity_list.append(entity)
#         elif(entity[1] in entity_type_list and entity[1]=='dise'):
#             if(disease_dict==None):
#                 filtered_entity_list.append(entity)
#             else:
#                 try:
#                     idx=disease_dict["lower"].index(entity[0])
#                     filtered_entity_list.append((disease_dict["normal"][idx],entity[1]))
#                 except ValueError:
#                     filtered_entity_list.append(entity)
#     return filtered_entity_list

def filter_entity_list(entity_list:list,entity_type_list:list,entity_dict:dict=None) -> list:
    '''按照类型对实体进行过滤'''
    '''entity_dict格式如下：
    {
        "entity_type_1(缩写的实体类别)":{"normal":[](列表),"lower":[]("normal"列表小写化后的新列表)},
        ...
    }'''
    filtered_entity_list=[]
    for entity in entity_list:
        if(entity[1] in entity_type_list and entity_dict==None):
            filtered_entity_list.append(entity)
        elif(entity[1] in entity_type_list and entity_dict!=None):
            if(has_alpha(entity[0])):
                try:
                    idx=entity_dict[entity[1]]["lower"].index(entity[0])
                    filtered_entity_list.append((entity_dict[entity[1]]["normal"][idx],entity[1]))
                except ValueError:
                    filtered_entity_list.append(entity)
            else:
                filtered_entity_list.append(entity)
    return filtered_entity_list

def get_disease_symptom_entity_list(entity_list:list,symptom_list:list) -> list:
    '''保留拥有disease和symptom双重定义的实体'''
    return [entity for entity in entity_list if(entity[1]=='body' or entity[0] in symptom_list)]
    # return list(set(entity_list) & set(symptom_list))

def get_disease_for_diagnosis(graph:Graph,entity_list:list) -> list:
    '''疾病诊断问题查询接口'''
    result=[]
    for e in entity_list:
        relation_type=get_relation_type(e[1],'Disease',diagnosis=True)
        for rel in relation_type:
            # property_type=get_property_type(e[1])
            # q="match (n:Disease) where '%s' in n.%s return n.name "%(e[0],property_type)
            q="match (e:%s{name:'%s'})-[rel:%s]->(n:Disease) return n.name "%(rel.split('_')[0],e[0],rel)
            result.append(graph.run(q).data())
    if(len(result)==0):
        return []
    result_final=[]
    for sub_result in result:
        result_final.extend(sub_result)
    result_sets=set([data_dict["n.name"] for data_dict in result_final])
    possible_disease=result_sets
    # for s in result_sets:
    #     possible_disease=possible_disease & s
    return list(possible_disease)
    # result_dict={}
    # for data_dict in result:
    #     name=data_dict["n.name"]
    #     try:
    #         result_dict[name]+=1
    #     except KeyError:
    #         result_dict[name]=1
    # max_one=list(result_dict.keys())[0]
    # for key in list(result_dict.keys()):
    #     if result_dict[key]>result_dict[max_one]:
    #         max_one=key
    # return max_one

def get_reason(graph:Graph,entity_list:list) -> list:
    '''病因查询接口'''
    result=[]
    for e in entity_list:
        q="match (n:Disease{name:'%s'}) return n.reason "%(e[0])
        result.extend(graph.run(q).data())
    return [data_dict["n.reason"] for data_dict in result]

def get_cure(graph:Graph,entity_list:list) -> dict:
    '''治疗方案查询接口'''
    result_1=[]
    result_2=[]
    result_3=[]
    result_4=[]
    for e in entity_list:
        q=["match (n:Treatment)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Treatment_Disease',e[0]),
           "match (n:Operation)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Operation_Disease',e[0]),
           "match (n:Drug)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Drug_Disease',e[0]),
           "match (n:Sport)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Sport_Suitable_Disease',e[0])]
        result_1.append(graph.run(q[0]).data())
        result_2.append(graph.run(q[1]).data())
        result_3.append(graph.run(q[2]).data())
        result_4.append(graph.run(q[3]).data())
    return {"treatment":[list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result_1],
            "operation":[list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result_2],
            "drug":[list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result_3],
            "sport":[list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result_4]}

def get_test(graph:Graph,entity_list:list) -> list:
    '''检查项目查询接口'''
    result=[]
    for e in entity_list:
        q="match (n:Test)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Test_Disease',e[0])
        result.append(graph.run(q).data())
    return [list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result]

def get_departement(graph:Graph,entity_list:list) -> list:
    '''挂号科室查询接口'''
    result=[]
    for e in entity_list:
        q="match (n:Department)-[rel:%s]->(e:Disease{name:'%s'}) return n.name "%('Department_Disease',e[0])
        result.append(graph.run(q).data())
    return [list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result]

def get_symptom(graph:Graph,entity_list:list) -> dict:
    '''症状查询接口'''
    result=[]
    result_=[]
    for e in entity_list:
        q="match (n:Symptom)-[rel:Symptom_Disease]->(m:Disease{name:'%s'}) return n.name"%(e[0])
        result.append(graph.run(q).data())
        q="match (n:Disease{name:'%s'}) return n.infectivity,n.period"%(e[0])
        result_.extend(graph.run(q).data())
    return {"symptom":[list(set([data_dict["n.name"] for data_dict in sub_result])) for sub_result in result],
            "infectivity":[data_dict["n.infectivity"] for data_dict in result_],
            "period":[data_dict["n.period"] for data_dict in result_]}

def get_disease(graph:Graph,entity_list:list) -> list:
    '''非疾病诊断问题的疾病查询接口'''
    result=[]
    for e in entity_list:
        relation_type=get_relation_type(e[1],'Disease')
        entity_result=[]
        for rel in relation_type:
            q="match (e:%s{name:'%s'})-[rel:%s]->(n:Disease) return n.name "%(rel.split('_')[0],e[0],rel)
            entity_result.extend(graph.run(q).data())
        result.append((entity_result))
    return [list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result]

def get_ade(graph:Graph,entity_list:list) -> list:
    '''药物不良反应查询接口'''
    result=[]
    for e in entity_list:
        q="match (n:ADE)-[rel:%s]->(e:Drug{name:'%s'}) return n.name "%('ADE_Drug',e[0])
        result.append(graph.run(q).data())
    return [list(set([data_dict["n.name"] for data_dict in sub_result]))  for sub_result in result]

class Query:
    def __init__(self,graph:Graph,disease_list_dir:str,symptom_list_dir:str,anatomy_list_dir:str,drug_list_dir:str,cure_list_dir:list,
                 check_list_dir) -> None:
        '''cure_list_dir格式如下：
        [
            "treatment路径",
            "operation路径",
            "sport路径"
        ]
        '''
        self.graph=graph
        self.disease_dict={}
        self.symptom_dict={}
        self.anatomy_dict={}
        self.drug_dict={}
        self.cure_dict={}
        self.check_dict={}
        #disease
        with open(disease_list_dir,'r',encoding='utf-8') as fp:
            self.disease_list=[dise.strip() for dise in fp.readlines()]
        self.disease_dict["normal"]=self.disease_list
        self.disease_dict["lower"]=[dise.lower() for dise in self.disease_dict["normal"]]
        #symptom
        with open(symptom_list_dir,'r',encoding='utf-8') as fp:
            self.symptom_list=[symp.strip() for symp in fp.readlines()]
        self.symptom_dict["normal"]=self.symptom_list
        self.symptom_dict["lower"]=[symp.lower() for symp in self.symptom_dict["normal"]]
        #anatomy
        with open(anatomy_list_dir,'r',encoding='utf-8') as fp:
            self.anatomy_list=[anat.strip() for anat in fp.readlines()]
        self.anatomy_dict["normal"]=self.anatomy_list
        self.anatomy_dict["lower"]=[anat.lower() for anat in self.anatomy_dict["normal"]]
        #drug
        with open(drug_list_dir,'r',encoding='utf-8') as fp:
            self.drug_list=[drug.strip() for drug in fp.readlines()]
        self.drug_dict["normal"]=self.drug_list
        self.drug_dict["lower"]=[drug.lower() for drug in self.drug_dict["normal"]]
        #cure
        self.cure_list=[]
        for dir in cure_list_dir:
            with open(dir,'r',encoding='utf-8') as fp:
                self.cure_list+=[cure.strip() for cure in fp.readlines()]
        self.cure_list+=self.drug_list
        self.cure_dict["normal"]=self.cure_list
        self.cure_dict["lower"]=[cure.lower() for cure in self.drug_dict["normal"]]
        #check
        with open(check_list_dir,'r',encoding='utf-8') as fp:
            self.check_list=[check.strip() for check in fp.readlines()]
        self.check_dict["normal"]=self.check_list
        self.check_dict["lower"]=[check.lower() for check in self.drug_dict["normal"]]
    
    def query(self,parser_output:dict) -> Any:
        question_code=parser_output["ir_result"]["prediction"]
        entity_list=parser_output["ner_result"]["predictions_as_entity_list"]
        if(question_code==1):
            entity_list=filter_entity_list(entity_list,['body','symp','dise'],{"body":self.anatomy_dict,"symp":self.symptom_dict,
                                                                               "dise":self.disease_dict})
            entity_list=get_disease_symptom_entity_list(entity_list,self.symptom_list)
            if(len(entity_list)==0):
                return None
            entity_list_=[]
            for e in entity_list:
                if(e[1]=='body'):
                    entity_list_.append((get_most_similar_string(e[0],self.anatomy_list),e[1]))
                else:
                    entity_list_.append((get_most_similar_string(e[0],self.symptom_list),e[1]))
            return get_disease_for_diagnosis(self.graph,entity_list)
        elif(question_code==2):
            entity_list=filter_entity_list(entity_list,['dise'],{"dise":self.disease_dict})
            if(len(entity_list)==0):
                return []
            return get_reason(self.graph,entity_list)
        elif(question_code==3):
            entity_list=filter_entity_list(entity_list,['dise'],{"dise":self.disease_dict})
            if(len(entity_list)==0):
                return {}
            return get_cure(self.graph,entity_list)
        elif(question_code==4):
            entity_list=filter_entity_list(entity_list,['dise'],{"dise":self.disease_dict})
            if(len(entity_list)==0):
                return []
            return {"test":get_test(self.graph,entity_list),"department":get_departement(self.graph,entity_list)}
        elif(question_code==6):
            entity_list=filter_entity_list(entity_list,['dise'],{"dise":self.disease_dict})
            if(len(entity_list)==0):
                return []
            return get_symptom(self.graph,entity_list)
        elif(question_code==7):
            entity_list=filter_entity_list(entity_list,['cure','drug'],{"cure":self.cure_dict,"drug":self.drug_dict})
            if(len(entity_list)==0):
                return []
            return get_disease(self.graph,entity_list)
        elif(question_code==8):
            entity_list=filter_entity_list(entity_list,['drug'],{"drug":self.drug_dict})
            if(len(entity_list)==0):
                return []
            return get_ade(self.graph,entity_list)
        elif(question_code==0):
            entity_list=filter_entity_list(entity_list,['chec'],{"chec":self.check_dict})
            if(len(entity_list)==0):
                return []
            return get_disease(self.graph,entity_list)
        else:
            return []
        
    def __call__(self,parser_output:dict) -> Any:
        return self.query(parser_output)