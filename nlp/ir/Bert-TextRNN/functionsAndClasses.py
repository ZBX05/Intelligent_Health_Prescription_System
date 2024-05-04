import torch
import numpy as np
from transformers import BertTokenizer
from sklearn.metrics import accuracy_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
import logging
import json
from typing import Any

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
    
def read_text_list(data:Any) -> Any:
    '''加载训练数据中所有语句'''
    text_list=[]
    if(isinstance(data,str)):
        try:
            fp=open(data,'r',encoding='utf-8',errors='ignore')
        except:
            logging.error(f'Unable to read {data}.')
            print(f'Unable to read {data}.')
            return None
        data_json=json.load(fp)
    elif(isinstance(data,list)):
        data_json=data
    else:
        logging.error(f'Data is provided in an illegal type.')
        print('Data is provided in an illegal type.')
        return None
    for data_dict in data_json:
        text_list.append(data_dict["text"])
    return text_list

    
def read_labels_list(data:Any) -> Any:
    '''加载训练数据中所有标签'''
    labels_list=[]
    if(isinstance(data,str)):
        try:
            fp=open(data,'r',encoding='utf-8',errors='ignore')
        except:
            logging.error(f'Unable to read {data}.')
            print(f'Unable to read {data}.')
            return None
        data_json=json.load(fp)
    elif(isinstance(data,list)):
        data_json=data
    else:
        logging.error(f'Data is provided in an illegal type.')
        print('Data is provided in an illegal type.')
        return None
    for data_dict in data_json:
        # labels_list.append({"label_4class":data_dict["label_4class"],"label_36class":data_dict["label_36class"]})
        labels_list.append(data_dict["label"])
    return labels_list

def train_val_test_split(text_list:list,label_list:list,proportion:str='8:1:1') -> dict:
    '''切分训练集、验证集，要求提供文本数据和对应的标签数据，以列表形式传入'''
    try:
        [train_str,val_str,test_str]=proportion.split(':')
        total=eval(train_str)+eval(val_str)+eval(test_str)
        train=eval(train_str)/total
        val=eval(val_str)/total
        test=eval(test_str)/total
        if(train>=1 or val>=1 or test>=1 or train<=0 or val<=0 or test<=0 or train+val+test!=1):
            raise Exception()
    except Exception:
        logging.warning('Data set spliting portion is illegal, using 0.8 .')
        print('Data set spliting portion is illegal, using 0.8 .')
        train,val,test=0.8,0.1,0.1
    train_text,rest_text,train_label,rest_label=train_test_split(text_list,label_list,train_size=train,random_state=42)
    val_text,test_text,val_label,test_label=train_test_split(rest_text,rest_label,train_size=float(val/(val+test)),random_state=42)
    data_dict={}
    data_dict["train"]=train_text,train_label
    data_dict["val"]=val_text,val_label
    data_dict["test"]=test_text,test_label
    return data_dict

# def trans_label(label:dict,labels_dict:dict) -> list:
#     '''将两级文字标签转换为数字标签'''
#     label_4class,label_36class=label["label_4class"],label["label_36class"]
#     label=labels_dict[label_4class][label_36class]
#     return label

def trans_label(label:dict,labels_dict:dict) -> int:
    return labels_dict[label]

class DataSequence(torch.utils.data.Dataset):
    '''加载训练数据'''
    def __init__(self,data:tuple,labels_dict:dict,bert_path:str,bert_max_length:int,ids_padding_value:int=-1) -> None:
        txt=data[0]
        lb=data[1]
        tokenizer=BertTokenizer.from_pretrained(bert_path)
        self.texts_ids=[tokenizer(str(i),max_length=bert_max_length,truncation=True,return_tensors="pt") for i in txt]
        self.labels=[trans_label(i,labels_dict) for i in lb]
        self.ids_padding_value=ids_padding_value
        self.bert_max_length=bert_max_length
    
    def __len__(self) -> int:
        return len(self.labels)
    
    def get_batch(self,idx:int) -> dict:
        return self.texts_ids[idx]
    
    def get_batch_label(self,idx:int) -> list:
        return self.labels[idx]
    
    def __getitem__(self,idx:int) -> tuple:
        batch_data_one=self.get_batch(idx)
        batch_label_one=self.get_batch_label(idx)
        return batch_data_one,batch_label_one
    
    def collate_fn(self,batch:Any) -> dict:
        data=[x[0] for x in batch]
        ids=[x["input_ids"][0].tolist() for x in data]
        labels=[x[1] for x in batch]

        batch_len=len(ids)
        max_len=max([len(id) for id in ids])
        batch_ids=np.ones((batch_len,max_len))*self.ids_padding_value
        # batch_padding_starts=[]
        for j in range(batch_len):
            batch_ids[j][:len(ids[j])]=ids[j]
            # batch_padding_starts.append(len(ids[j])%self.bert_max_length)
        batch_ids=torch.tensor(batch_ids,dtype=torch.long)
        # batch_padding_starts=torch.tensor(batch_padding_starts,dtype=torch.long)
        batch_labels=torch.tensor(labels,dtype=torch.long)
        batch_masks=batch_ids.gt(self.ids_padding_value)

        # return {"input_ids":batch_ids,"attention_mask":batch_masks,"labels":batch_labels,"padding_starts":batch_padding_starts}
        return {"input_ids":batch_ids,"attention_mask":batch_masks,"batch_labels":batch_labels}

def delete_attr(data_dict:dict) -> dict:
    labels=data_dict["batch_labels"].numpy()
    mask=data_dict["attention_mask"].numpy()
    input_ids=data_dict["input_ids"].numpy()
    index_list=[]
    for index in range(len(input_ids)):
        if len([idx for idx in input_ids[index] if idx>-1])==0:
            index_list.append(index)
    labels=np.delete(labels,index_list,axis=0)
    mask=np.delete(mask,index_list,axis=0)
    input_ids=np.delete(input_ids,index_list,axis=0)
    batch_ids=torch.tensor(input_ids,dtype=torch.long)
    batch_labels=torch.tensor(labels,dtype=torch.long)
    batch_masks=torch.tensor(mask,dtype=torch.long)
    return {"input_ids":batch_ids,"attention_mask":batch_masks,"labels":batch_labels}

def compute_scores(batch_preds:list,batch_tags:list) -> tuple:
    acc=0
    recall=0
    f1=0
    for idx in range(len(batch_preds)):
        acc+=accuracy_score(batch_preds[idx],batch_tags[idx])
        recall+=recall_score(batch_tags[idx],batch_preds[idx],average='micro')
        f1+=f1_score(batch_preds[idx],batch_tags[idx],average='micro')
    return acc/len(batch_tags),recall/len(batch_tags),f1/len(batch_tags)