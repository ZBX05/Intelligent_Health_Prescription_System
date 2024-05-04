import torch
import numpy as np
from transformers import BertTokenizerFast
from sklearn.metrics import accuracy_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
import logging
import json
from vocabulary import Vocabulary
import NERConfig
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
        labels_list.append(data_dict["labels"])
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

def get_labels_relation_with_ids(labels_list:list) -> tuple:
    '''将标签与id互相映射'''
    label_list=[]
    for labels in labels_list:
        for label in labels:
            label_list.append(label)
    unique_labels=set(label_list)
    labels_to_ids={k: v for v, k in enumerate(sorted(unique_labels))}
    ids_to_labels={v: k for v, k in enumerate(sorted(unique_labels))}
    return labels_to_ids,ids_to_labels

def align_labels(labels:list,labels_to_ids:dict) -> list:
    ''' 校准标签，labels_to_ids是标签向id的映射，labels是对应训练数据的标签'''
    token_labels=[labels_to_ids[label] for label in labels]
    return token_labels

# def align_labels(vocab:Vocabulary,text:str,labels:list,labels_to_ids:dict,labels_padding_value:int=-1,
#                  label_all_tokens=True) -> list:
#         ''' 校准标签，labels_to_ids是标签向id的映射，labels是对应训练数据的标签'''
#         word_ids=vocab.word_ids(text)
#         previous_word_idx=None
#         # padding_value=labels_to_ids["O"]
#         padding_value=labels_padding_value
#         label_ids=[]
#         for word_idx in word_ids:
#             if word_idx is None:
#                 label_ids.append(padding_value)
#             elif word_idx!=previous_word_idx:
#                 try:
#                   label_ids.append(labels_to_ids[labels[word_idx]])
#                 except:
#                   label_ids.append(padding_value)     
#             else:
#                 label_ids.append(labels_to_ids[labels[word_idx]] if label_all_tokens else padding_value)
#             previous_word_idx=word_idx      
#         return label_ids

class DataSequence(torch.utils.data.Dataset):
    '''加载训练数据'''
    def __init__(self,data:tuple,labels_to_ids:dict,vocab:Vocabulary,labels_padding_value:int=-1) -> None:
        lb=data[1]
        txt=data[0]
        self.texts=[vocab.word_ids(i)[0] for i in txt]
        # 对齐标签
        self.labels=[align_labels(label,labels_to_ids) for label in lb]
        self.labels_padding_value=labels_padding_value

    def __len__(self) -> int:
        return len(self.labels)

    def get_batch_data(self,idx:int) -> dict:
        return self.texts[idx]

    def get_batch_labels(self,idx:int) -> torch.LongTensor:
        return torch.LongTensor(self.labels[idx])

    def __getitem__(self,idx:int) -> tuple:
        batch_data_one=self.get_batch_data(idx)
        batch_labels_one=self.get_batch_labels(idx)
        return batch_data_one,batch_labels_one
    
    def collate_fn(self,batch:Any) -> dict:
        ids=[x[0] for x in batch]
        labels=[x[1].tolist() for x in batch]
        batch_len=len(ids)
        max_len=max([len(id) for id in ids])
        batch_ids=np.zeros((batch_len,max_len))
        batch_labels=np.ones((batch_len,max_len),dtype=np.uint8)*self.labels_padding_value
        batch_padding_starts=[]
        for j in range(batch_len):
            batch_ids[j][:len(ids[j])]=ids[j]
            batch_labels[j][:len(labels[j])]=labels[j]
            batch_padding_starts.append(len(ids[j]))
        
        #转换为tensor
        batch_ids=torch.tensor(batch_ids,dtype=torch.long)
        #batch_masks=torch.tensor(batch_masks,dtype=torch.long)
        batch_padding_starts=torch.tensor(batch_padding_starts,dtype=torch.long)
        batch_labels=torch.tensor(batch_labels,dtype=torch.long)
        # batch_masks=batch_ids.gt(-1)

        return {"input_ids":batch_ids,"padding_starts":batch_padding_starts,"batch_labels":batch_labels}     

def compute_scores(batch_preds:list,batch_tags:list) ->tuple:
    acc=0
    recall=0
    f1=0
    for idx in range(len(batch_preds)):
        acc+=accuracy_score(batch_preds[idx],batch_tags[idx])
        recall+=recall_score(batch_tags[idx],batch_preds[idx],average='macro')
        f1+=f1_score(batch_preds[idx],batch_tags[idx],average='macro')
    return acc/len(batch_tags),recall/len(batch_tags),f1/len(batch_tags)
