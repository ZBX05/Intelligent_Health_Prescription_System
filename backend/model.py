import torch
from torch import Tensor
import torch.nn as nn
from transformers import BertModel,BertConfig
from TorchCRF import CRF
import torch.nn.functional as F
import math
from typing import Any
from torch.nn.utils.rnn import pad_sequence

class NERModel(nn.Module):
    '''问句文本命名实体识别模型'''
    def __init__(self,bert_path:str,gru_embedding_size:int,hidden_size:int,num_labels:int,hidden_dropout:float,gru_dropout:float,
                 labels_padding_value:int,ids_padding_value:int) -> None:
        super(NERModel,self).__init__()
        self.num_labels=num_labels
        self.config=BertConfig.from_pretrained(bert_path)
        self.bert=BertModel.from_pretrained(bert_path,config=self.config)
        self.dropout=nn.Dropout(hidden_dropout)
        self.bi_gru=nn.GRU(
            input_size=gru_embedding_size,
            hidden_size=hidden_size,
            batch_first=True,
            num_layers=2,
            dropout=gru_dropout,
            bidirectional=True
        )
        self.classifier=nn.Linear(hidden_size*2,self.num_labels)
        self.crf=CRF(self.num_labels)
        self.labels_padding_value=labels_padding_value
        self.ids_padding_value=ids_padding_value
    
    def forward(self,input_ids:Tensor,token_type_ids:Tensor=None,attention_mask:Tensor=None,labels:Tensor=None,
                position_ids:Tensor=None,inputs_embeds:Tensor=None,head_mask:Tensor=None,
                padding_starts:Tensor=None) -> tuple:
        outputs=self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask,
                            inputs_embeds=inputs_embeds)
        sequence_output=outputs[0]
        origin_sequence_output=[layer[1:idx-1] for layer,idx in zip(sequence_output,padding_starts)]
        padded_sequence_output=pad_sequence(origin_sequence_output,batch_first=True,padding_value=self.ids_padding_value)
        if labels is not None:
            labels=[label[1:idx-1] for label,idx in zip(labels,padding_starts)]
            padded_labels=pad_sequence(labels,batch_first=True,padding_value=self.labels_padding_value)
        padded_sequence_output=self.dropout(padded_sequence_output)     
        gru_output,_=self.bi_gru(padded_sequence_output)
        classifier_output=self.classifier(gru_output)
        outputs=(classifier_output,)

        if labels is not None:
            loss_mask=padded_labels.gt(self.labels_padding_value)
            loss=self.crf(classifier_output,padded_labels,loss_mask)*(-1)
            outputs=(loss,)+outputs
        return outputs

class DotProductAttention(nn.Module):
    def __init__(self,dropout:float) -> None:
        super(DotProductAttention,self).__init__()
        self.dropout=nn.Dropout(dropout)
    
    def forward(self,queries:Tensor,keys:Tensor,values:Tensor) -> Tensor:
        d=queries.shape[-1]
        scores=torch.matmul(queries,keys.permute(0,2,1))/math.sqrt(d)
        # self.attention_weights=masked_softmax(scores,valid_lens)
        self.attention_weights=F.softmax(scores,dim=-1)
        return torch.matmul(self.dropout(self.attention_weights),values)

class SelfAttention(nn.Module):
    def __init__(self,size:int,dropout:float) -> None:
        super(SelfAttention,self).__init__()
        self.W_q=nn.Linear(size,size)
        self.W_k=nn.Linear(size,size)
        self.W_v=nn.Linear(size,size)
        self.attention=DotProductAttention(dropout)

    def forward(self,queries:Tensor,keys:Tensor,values:Tensor) -> Tensor:
        queries=self.W_q(queries)
        keys=self.W_k(keys)
        values=self.W_v(values)
        attention=self.attention(queries,keys,values)
        return F.max_pool1d(attention.permute(0,2,1),attention.permute(0,2,1).shape[-1]).squeeze()
        # return torch.sum(self.attention(queries,keys,values),dim=1)

class IRModel(nn.Module):
    '''问句文本意图识别模型'''
    def __init__(self,bert_path:str,gru_embedding_size:int,hidden_size:int,num_labels:int,gru_dropout:float,attention_dropout:float,
                 ids_padding_value:int,activation:Any) -> None:
        super(IRModel,self).__init__()
        self.num_labels=num_labels
        self.activation=activation
        self.config=BertConfig.from_pretrained(bert_path)
        self.bert=BertModel.from_pretrained(bert_path,config=self.config)
        self.bi_gru=nn.GRU(
            input_size=gru_embedding_size,
            hidden_size=hidden_size,
            batch_first=True,
            num_layers=2,
            dropout=gru_dropout,
            bidirectional=True
        )
        self.att=SelfAttention(hidden_size*2,attention_dropout)
        self.classifier=nn.Linear(hidden_size*2,num_labels)
        self.ids_padding_value=ids_padding_value
    
    def forward(self,input_ids:Tensor,token_type_ids:Tensor=None,attention_mask:Tensor=None,position_ids:Tensor=None,
                inputs_embeds:Tensor=None,head_mask:Tensor=None) -> Tensor:
        outputs=self.bert(input_ids,
                          attention_mask=attention_mask,
                          token_type_ids=token_type_ids,
                          position_ids=position_ids,
                          inputs_embeds=inputs_embeds,
                          head_mask=head_mask)
        sequence_output=outputs[0]
        gru_output,_=self.bi_gru(sequence_output)
        classifier_input=self.activation(self.att(gru_output,gru_output,gru_output))
        classifier_output=self.classifier(classifier_input)
        return classifier_output