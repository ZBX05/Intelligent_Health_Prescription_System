import torch
import numpy as np
from transformers import BertTokenizer
from sklearn.metrics import accuracy_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
import logging
import json
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
    
def read_text_list(data:Any,max_length:int=512) -> Any:
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
        if(len(data_dict["text"])>max_length):
            i=len(data_dict["text"])//max_length+1
            for j in range(i):
                text_list.append(data_dict["text"][j*max_length:(j+1)*max_length])
        else:
            text_list.append(data_dict["text"])
    return text_list

    
def read_labels_list(data:Any,max_length:int=512) -> Any:
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
        if(len(data_dict["labels"])>max_length):
            i=len(data_dict["labels"])//max_length+1
            for j in range(i):
                labels_list.append(data_dict["labels"][j*max_length:(j+1)*max_length])
        else:
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

def align_labels(tokenizer:BertTokenizer,text:str,labels:list,labels_to_ids:dict,bert_max_length:int,
                 labels_padding_value:int=-1) -> list:
    '''校准标签，labels_to_ids是标签向id的映射，labels是对应训练数据的标签'''
    tokenized_input=tokenizer(text,max_length=bert_max_length,truncation=True,return_tensors="pt")
    #中文分词不能直接用读取word_ids()结果的方式来对齐，这根本无法对齐，因为Bert分词器的中文分词是按字分和按词分两种方式的混合而不是一字一分
    #若不使用Bert，而是自己构建一字一分的词表则可以直接简单映射
    tokens=tokenizer.convert_ids_to_tokens(tokenized_input.input_ids[0])

    iter_tokens=iter(tokens)
    iter_labels=iter(labels)
    iter_text=iter(text.lower())
    token_labels=[]

    #分别获取迭代器中的第一个对象
    t=next(iter_tokens)
    ch_l=next(iter_labels)
    ch_t=next(iter_text)
    while True:
        #单个的字符token（比如中文字符），直接用labels_to_ids映射
        if(len(t)==1):
            while t!=ch_t:#对齐处理，token序列中的字符只可能比原文本少，不可能多于原文本
                try:
                    ch_l=next(iter_labels)
                    ch_t=next(iter_text)
                except StopIteration:
                    pass
            token_labels.append(labels_to_ids[ch_l])
            try:
                ch_l=next(iter_labels)
                ch_t=next(iter_text)
            except StopIteration:
                pass
        #特殊token"[CLS]"、"[SEP]"，添加padding_value，由于原文本和原标签中没有这类token，所以不用从其中取下一个字符和标签
        elif t in tokenizer.special_tokens_map.values() and t!='[UNK]':
            token_labels.append(labels_padding_value)
        #处理"[UNK]"
        elif t=='[UNK]':
            token_labels.append(labels_to_ids[ch_l])
            try:
                t=next(iter_tokens)
            except StopIteration:
                break
            #对齐，忽略被处理为未知的token中其余的字符
            if t not in tokenizer.special_tokens_map.values():
                while ch_t!=t[0]:
                    try:
                        ch_l=next(iter_labels)
                        ch_t=next(iter_text)
                    except StopIteration:
                        pass
            continue
        #处理其他长度大于1的token
        else:
            t_label=ch_l
            has_begin=False#
            t=t.replace('##','')
            ch_tt=ch_t
            while t[0]!=ch_t:#对齐处理，token序列中的字符只可能比原文本少，不可能多于原文本
                try:
                    ch_l=next(iter_labels)
                    ch_t=next(iter_text)
                except StopIteration:
                    pass
            for c in t:
                assert c==ch_t or ch_t not in tokenizer.vocab
                if t_label.find('B-')!=-1:#
                    has_begin=True#
                # if t_label!='O':
                if t_label!='O' and has_begin==False:#
                    t_label=ch_l
                try:
                    ch_t=next(iter_text)
                    ch_l=next(iter_labels)
                except StopIteration:
                    pass
            token_labels.append(labels_to_ids[t_label])
        #下一个token
        try:
            t=next(iter_tokens)
        except StopIteration:
            break
    
    assert len(token_labels)==len(tokens)

    return token_labels

# def align_labels(tokenizer:BertTokenizerFast,text:str,labels:list,labels_to_ids:dict,bert_max_length:int,labels_padding_value:int=-1,
#                  label_all_tokens=True) -> list:
#         ''' 校准标签，labels_to_ids是标签向id的映射，labels是对应训练数据的标签'''
#         tokenized_input=tokenizer(text,padding='max_length',max_length=bert_max_length,truncation=True,return_tensors="pt")
#         word_ids=tokenized_input.word_ids()
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
    def __init__(self,data:tuple,labels_to_ids:dict,bert_path:str,bert_max_length:int,labels_padding_value:int=-1) -> None:
        lb=data[1]
        txt=data[0]
        tokenizer=BertTokenizer.from_pretrained(bert_path)
        self.texts=[tokenizer(str(i),max_length=bert_max_length,truncation=True,return_tensors="pt") for i in txt]
        # 对齐标签
        self.labels=[align_labels(tokenizer,i,j,labels_to_ids,bert_max_length,labels_padding_value) for i,j in zip(txt, lb)]
        self.bert_max_length=bert_max_length
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
        data=[x[0] for x in batch]
        ids=[x["input_ids"][0].tolist() for x in data]
        #labels也需要tolist()，因为是List[torch.LongTensor]，这是无法直接转换成Tensor的，需要先变成List[List[]]
        labels=[x[1].tolist() for x in batch]
        #一个batch有多大
        batch_len=len(ids)
        #同一批次中最大长度，但不能超过设定给bert tokenizer的max length，若超过则在之后进行截断
        max_len=max([len(id) for id in ids])
        batch_ids,batch_masks=np.zeros((batch_len,max_len)),np.zeros((batch_len,max_len),dtype=np.uint8)
        batch_labels=np.ones((batch_len,max_len),dtype=np.uint8)*self.labels_padding_value
        batch_padding_starts=[]
        #对于每一条数据进行处理
        for j in range(batch_len):
            # cur_len=len(ids[j])
            # if(cur_len<=max_len):
            #     batch_ids[j][:cur_len]=ids[j]
            #     # batch_masks[j][:cur_len]=1
            #     batch_padding_starts.append(cur_len)
            #     batch_labels[j][:cur_len]=labels[j][:cur_len]
            # else:
            #     batch_ids[j][:max_len-1]=ids[j][:max_len-1]
            #     # batch_masks[j][:]=1
            #     batch_padding_starts.append(0)#表示不用padding
            #     batch_labels[j][:max_len-1]=labels[j][:max_len-1]
            batch_ids[j][:len(ids[j])]=ids[j]
            # batch_masks[j][:len(ids[j])]=1
            batch_padding_starts.append(len(ids[j])%self.bert_max_length)
            batch_labels[j][:len(ids[j])]=labels[j][:len(ids[j])]
        #转换为tensor
        batch_ids=torch.tensor(batch_ids,dtype=torch.long)
        # batch_masks=torch.tensor(batch_masks,dtype=torch.long)
        batch_padding_starts=torch.tensor(batch_padding_starts,dtype=torch.long)
        batch_labels=torch.tensor(batch_labels,dtype=torch.long)
        batch_masks=batch_ids.gt(self.labels_padding_value)

        # batch_data, batch_label_starts = batch_data.to(self.device), batch_label_starts.to(self.device)
        # batch_labels = batch_labels.to(self.device)
        return {"input_ids":batch_ids,"attention_mask":batch_masks,"padding_starts":batch_padding_starts,"batch_labels":batch_labels}

def delete_attr(data_dict:dict) -> dict:
    label=data_dict["batch_labels"].numpy()
    mask=data_dict["attention_mask"].numpy()
    input_ids=data_dict["input_ids"].numpy()
    padding_starts=data_dict["padding_starts"].numpy()
    index_list=[]
    for index in range(len(label)):
        if len([idx for idx in label[index] if idx>-1])==0:
            index_list.append(index)
    label=np.delete(label,index_list,axis=0)
    mask=np.delete(mask,index_list,axis=0)
    padding_starts=np.delete(padding_starts,index_list,axis=0)
    input_ids=np.delete(input_ids,index_list,axis=0)
    batch_ids=torch.tensor(input_ids,dtype=torch.long)
    batch_padding_starts=torch.tensor(padding_starts,dtype=torch.long)
    batch_labels=torch.tensor(label,dtype=torch.long)
    batch_masks=torch.tensor(mask,dtype=torch.long)
    return {"input_ids":batch_ids,"attention_mask":batch_masks,"padding_starts":batch_padding_starts,"batch_labels":batch_labels}

def compute_scores(batch_preds:list,batch_tags:list) ->tuple:
    acc=0
    recall=0
    f1=0
    for idx in range(len(batch_preds)):
        acc+=accuracy_score(batch_preds[idx],batch_tags[idx])
        recall+=recall_score(batch_tags[idx],batch_preds[idx],average='macro')
        f1+=f1_score(batch_preds[idx],batch_tags[idx],average='macro')
    return acc/len(batch_tags),recall/len(batch_tags),f1/len(batch_tags)
