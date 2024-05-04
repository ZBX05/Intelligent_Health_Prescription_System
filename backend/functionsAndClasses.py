import torch
from torch import nn
from model import NERModel,IRModel
from configparser import ConfigParser
from py_stringmatching import BagDistance
from typing import Any
import json
import flask
import secrets

class APPConfig(flask.Config):
    DEBUG=False
    TESTING=False
    SECRET_KEY=secrets.token_hex(16)
    SESSION_TYPE='filesystem'
    SESSION_PERMANENT=False
    SESSION_USE_SIGNER=False
    SESSION_COOKIE_NAME='unique_session_cookie'
    SESSION_FILE_MODE=384
    SESSION_KEY_PREFIX='session'
    SESSION_FILE_DIR='/session'
    MAX_COOKIE_SIZE=8192

#对话程序使用
class Config:
    def __init__(self,config_dir:str) -> None:
        self.config=ConfigParser()
        self.config.read(config_dir,encoding='utf8')
        self.bert_path=self.config.get('paths_and_dirs','bert_path')
        self.ner_gru_embedding_size=eval(self.config.get('ner_parameters','ner_gru_embedding_size'))
        self.ner_hidden_size=eval(self.config.get('ner_parameters','ner_hidden_size'))
        self.ner_num_labels=eval(self.config.get('ner_parameters','ner_num_labels'))
        self.ner_hidden_dropout=eval(self.config.get('ner_parameters','ner_hidden_dropout'))
        self.ner_gru_dropout=eval(self.config.get('ner_parameters','ner_gru_dropout'))
        self.ner_labels_padding_value=eval(self.config.get('ner_parameters','ner_labels_padding_value'))
        self.ner_ids_padding_value=eval(self.config.get('ner_parameters','ner_ids_padding_value'))
        self.ner_model_state_dir=self.config.get('paths_and_dirs','ner_model_state_dir')
        self.ir_gru_embedding_size=eval(self.config.get('ir_parameters','ir_gru_embedding_size'))
        self.ir_hidden_size=eval(self.config.get('ir_parameters','ir_hidden_size'))
        self.ir_num_labels=eval(self.config.get('ir_parameters','ir_num_labels'))
        self.ir_gru_dropout=eval(self.config.get('ir_parameters','ir_gru_dropout'))
        self.ir_attention_dropout=eval(self.config.get('ir_parameters','ir_attention_dropout'))
        self.ir_ids_padding_value=eval(self.config.get('ir_parameters','ir_ids_padding_value'))
        self.ir_model_state_dir=self.config.get('paths_and_dirs','ir_model_state_dir')
        labels_to_ids=json.loads(self.config.get('dicts','labels_to_ids'))
        self.ids_to_labels={_id: _label for _label,_id in list(labels_to_ids.items())}
        labels_dict=json.loads(self.config.get('dicts','labels_dict'))
        self.intentions_dict={_id: _label for _label,_id in list(labels_dict.items())}
        self.ner_max_length=eval(self.config.get('ner_parameters','ner_max_length'))
        self.ir_max_length=eval(self.config.get('ir_parameters','ir_max_length'))
        
    def get_config(self) -> ConfigParser:
        return self.config

#web应用程序使用
class WebConfig:
    def __init__(self,config_dir:str) -> None:
        self.config=ConfigParser()
        self.config.read(config_dir,encoding='utf8')
        self.sql_host=self.config.get('sql','host')
        self.sql_port=eval(self.config.get('sql','port'))
        self.sql_user=self.config.get('sql','user')
        self.sql_password=self.config.get('sql','password')
        self.sql_db=self.config.get('sql','db')
        self.graph_host=self.config.get('graph','host')
        self.graph_browser_port=eval(self.config.get('graph','browser_port'))
        self.graph_browser_protocol=self.config.get('graph','browser_protocol')
        self.graph_user=self.config.get('graph','user')
        self.graph_password=self.config.get('graph','password')
        self.app_host=self.config.get('app','host')
        self.app_port=eval(self.config.get('app','port'))
        self.app_admin=self.config.get('app','admin')
        self.app_cert_dir=self.config.get('app','cert_dir')
        self.app_key_dir=self.config.get('app','key_dir')
        self.app_service_num=eval(self.config.get('app','service_num'))
        self.app_data_num=eval(self.config.get('app','data_num'))
        self.dialog_too_long=eval(self.config.get('dialog','too_long'))

    def get_config(self) -> ConfigParser:
        return self.config

def try_gpu(i:int=0) -> torch.device:
    '''按照指定编号返回拥有CUDA核心的GPU，如果没有则返回CPU'''
    if torch.cuda.device_count() >= 1:
        return torch.device(f'cuda:{i}')
    else:
        return torch.device('cpu')
    
def try_all_gpus() -> list:
    '''返回全部拥有CUDA核心的GPU，如果没有则返回CPU'''
    if torch.cuda.device_count() >=1:
        return [torch.device(f'cuda:{i}') for i in range(torch.cuda.device_count())]
    else:
        return [torch.device('cpu')]

def create_ner_model(model_state_dir:str,bert_path:str,gru_embedding_size:int,hidden_size:int,num_labels:int,hidden_dropout:float,
                   gru_dropout:float,labels_padding_value:int,ids_padding_value:int) -> NERModel:
    '''创建问题命名实体识别模型'''
    try:
        ner_model=NERModel(bert_path,gru_embedding_size,hidden_size,num_labels,hidden_dropout,gru_dropout,labels_padding_value,
                           ids_padding_value)
    except Exception as e:
        raise e
    ner_model.load_state_dict(torch.load(model_state_dir,torch.device('cpu')))
    return ner_model

def create_ir_model(model_state_dir:str,bert_path:str,gru_embedding_size:int,hidden_size:int,num_labels:int,gru_dropout:float,
                    attention_dropout:float,ids_padding_value:int) -> IRModel:
    '''创建问题意图识别模型'''
    activation=nn.ReLU()
    try:
        ir_model=IRModel(bert_path,gru_embedding_size,hidden_size,num_labels,gru_dropout,attention_dropout,ids_padding_value,
                         activation)
    except Exception as e:
        raise e
    ir_model.load_state_dict(torch.load(model_state_dir,torch.device('cpu')))
    return ir_model

def create_ner_model_from_config(config:Config) -> NERModel:
    '''创建问题命名实体识别模型'''
    bert_path=config.bert_path
    gru_embedding_size=config.ner_gru_embedding_size
    hidden_size=config.ner_hidden_size
    num_labels=config.ner_num_labels
    hidden_dropout=config.ner_hidden_dropout
    gru_dropout=config.ner_gru_dropout
    labels_padding_value=config.ner_labels_padding_value
    ids_padding_value=config.ner_ids_padding_value
    model_state_dir=config.ner_model_state_dir
    return create_ner_model(model_state_dir,bert_path,gru_embedding_size,hidden_size,num_labels,hidden_dropout,gru_dropout,
                            labels_padding_value,ids_padding_value)

def create_ir_model_from_config(config:Config) -> IRModel:
    '''创建问题意图识别模型'''
    bert_path=config.bert_path
    gru_embedding_size=config.ir_gru_embedding_size
    hidden_size=config.ir_hidden_size
    num_labels=config.ir_num_labels
    gru_dropout=config.ir_gru_dropout
    attention_dropout=config.ir_attention_dropout
    ids_padding_value=config.ir_ids_padding_value
    model_state_dir=config.ir_model_state_dir
    return create_ir_model(model_state_dir,bert_path,gru_embedding_size,hidden_size,num_labels,gru_dropout,attention_dropout,
                           ids_padding_value)

def has_alpha(word:str) -> bool:
    alphabet=set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    for char in word:
        if(char in alphabet):
            return True
    return False

def is_sub_string(string:str,traget_string:str) -> tuple:
    '''判断某一字符串是否为另一字符串的子串'''
    if(string in traget_string):
        return abs(len(traget_string)-len(string)),True
    return None,False

def get_most_similar_string(string:str,target_list:list) -> str:
    '''获取最相似的字符串'''
    most_similar=[]
    for s in target_list:
        if(string==s):
            return string
        s_1=is_sub_string(string,s)
        if(s_1[1]):
            most_similar.append((s_1[0],s))
        else:
            s_2=is_sub_string(s,string)
            if(s_2[1]):
                most_similar.append((s_2[0],s))
    bag=BagDistance()
    if(len(most_similar)!=0):
        most_similar=sorted(most_similar,reverse=True)
        return most_similar[0][1]
    else:
        score=[]
        for s in target_list:
            score.append((bag.get_sim_score(s,string),s))
        return sorted(score,reverse=True)[0][1]
    
def check_email_format(email:str) -> bool:
    if(email.find('@')==-1):
        return False
    suffix=email.split('@')[1].strip()
    if(suffix==''):
        return False
    suffix_list=suffix.split('.')
    for s in suffix_list:
        if(s==''):
            return False
    return True

def check_password_format(password:str,password_again:str) -> tuple:
    if(len(password)<8):
        return False,'密码过短！'
    if(len(password)>20):
        return False,'密码过长！'
    legal=set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*_@&')
    for char in password:
        if(char not in legal):
            return False,"密码中出现非法字符！"
    if(password!=password_again):
        return False,'两次输入的密码不相同！'
    return True,None

def register_check(form:dict) -> tuple:
    email=form["email"]
    password=form["password"]
    password_again=form["password_again"]
    if(not check_email_format(email)):
        return False,'邮箱格式错误！'
    result=check_password_format(password,password_again)
    if(not result[0]):
        return False,result[1]
    return True,email,password

def read_node(token:str,data:dict) -> dict:
    id=data[f"id({token})"]
    try:
        label=data[f"labels({token})"][0]
    except:
        label='unknown'
    name=data[f"{token}.name"]
    return {"id":id,"label":label,"name":name}

def read_relation(data:dict) -> dict:
    source=data["id(m)"]
    target=data["id(n)"]
    name=data["r.name"]
    return {"source":source,"target":target,"name":name}

def read_graph_data(data_list:list):
    ids=[]
    nodes=[]
    links=[]
    for data in data_list:
        m=read_node('m',data)
        n=read_node('n',data)
        if(m["id"] not in ids):
            nodes.append(m)
            ids.append(m["id"])
        if(n["id"] not in ids):
            nodes.append(n)
            ids.append(n["id"])
        links.append(read_relation(data))
    return {"nodes":nodes,"links":links}

def read_single_graph_data(data_list:list):
    ids=[]
    nodes=[]
    for data in data_list:
        n=read_node('n',data)
        if(n["id"] not in ids):
            nodes.append(n)
            ids.append(n["id"])
    return {"nodes":nodes,"links":[]}


if __name__ == '__main__':
    with open('f:/system/graph/txt/anatomy.txt','r',encoding='utf-8') as fp:
            anatomy_list=[anat.strip() for anat in fp.readlines()]
    print(get_most_similar_string('足部',anatomy_list))