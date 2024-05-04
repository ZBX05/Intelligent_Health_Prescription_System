import torch
from torch.utils.data import DataLoader
from torch import Tensor
from torch import nn
from d2l import torch as d2l
from transformers import BertModel,BertConfig,BertPreTrainedModel
from tqdm import tqdm
from torch.nn.utils.rnn import pad_sequence
from TorchCRF import CRF
from typing import Any
from functionsAndClasses import *
import logging
import NERConfig

class NERModel(torch.nn.Module):
    def __init__(self,NERConfig:NERConfig) -> None:
        super(NERModel,self).__init__()
        self.clip_grad=NERConfig.clip_grad
        self.num_labels=NERConfig.num_labels
        self.config=BertConfig.from_pretrained(NERConfig.bert_path)
        self.bert=BertModel.from_pretrained(NERConfig.bert_path,config=self.config)
        # self.bert=BertModel(self.config)
        self.dropout=nn.Dropout(NERConfig.hidden_dropout)
        self.bi_gru=nn.GRU(
            input_size=NERConfig.gru_embedding_size,
            hidden_size=NERConfig.hidden_size,
            batch_first=True,
            num_layers=2,
            dropout=NERConfig.gru_dropout,
            bidirectional=True
        )
        self.classifier=nn.Linear(NERConfig.hidden_size*2,self.num_labels)
        self.crf=CRF(self.num_labels)
        self.labels_padding_value=NERConfig.labels_padding_value
        self.ids_padding_value=NERConfig.ids_padding_value
    
    def forward(self,input_ids:Tensor,token_type_ids:Tensor=None,attention_mask:Tensor=None,labels:Tensor=None,
                position_ids:Tensor=None,inputs_embeds:Tensor=None,head_mask:Tensor=None,
                padding_starts:Tensor=None) -> tuple:
        # input_ids,input_token_starts=input_data---
        # input_ids=input_data
        outputs=self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids,
                            head_mask=head_mask,
                            inputs_embeds=inputs_embeds)
        sequence_output=outputs[0]
        #去除[CLS]标签等位置，获得与label对齐的pre_label表示
        origin_sequence_output=[layer[1:idx-1] for layer,idx in zip(sequence_output,padding_starts)]
        # origin_sequence_output=[layer[starts.nonzero().squeeze(1)]
        #                             for layer, starts in zip(sequence_output,input_token_starts)]

        #将sequence_output的pred_label维度padding到最大长度
        padded_sequence_output=pad_sequence(origin_sequence_output,batch_first=True,padding_value=self.ids_padding_value)
        if labels is not None:
            labels=[label[1:idx-1] for label,idx in zip(labels,padding_starts)]
            padded_labels=pad_sequence(labels,batch_first=True,padding_value=self.labels_padding_value)
        #dropout
        padded_sequence_output=self.dropout(padded_sequence_output)
        #输入到BiGRU        
        gru_output,_=self.bi_gru(padded_sequence_output)
        #BiGRU结果输入至线性分类器层进行分类
        classifier_output=self.classifier(gru_output)
        outputs=(classifier_output,)

        #输入CRF层
        if labels is not None:
            loss_mask=padded_labels.gt(self.labels_padding_value)
            loss=self.crf(classifier_output,padded_labels,loss_mask)*(-1)
            outputs=(loss,)+outputs
        return outputs

def train_epoch(train_loader:DataLoader,model:Any,optimizer:Any,scheduler:Any) -> float:
    '''对模型进行一次迭代的训练'''
    device=try_all_gpus()
    train_loss=0
    model.train()
    for train_data_dict in tqdm(train_loader):
        train_data_dict=delete_attr(train_data_dict)
        train_label=train_data_dict["batch_labels"].to(device[0])
        mask=train_data_dict["attention_mask"].to(device[0])
        input_ids=train_data_dict["input_ids"].to(device[0])
        padding_starts=train_data_dict["padding_starts"].to(device[0])
        
        optimizer.zero_grad()
        loss,_=model(input_ids=input_ids,attention_mask=mask,labels=train_label,padding_starts=padding_starts)
        # loss,logits=model(input_ids,attention_mask=mask,labels=label_clean,padding_starts=padding_starts)
        #获取最大概率值指向的实体类别，该预测值就是预测结果
        # predictions=logits.argmax(dim=2)
        #计算准确率
        # acc=(predictions.squeeze(1)==label_clean).float().mean()
        # train_acc.append(acc.item())
        # for l in loss:
        #     train_loss.append(l.item())
        train_loss+=loss.sum().item()
        #反向传播
        loss.sum().backward()
        if(isinstance(model,NERModel)):
            max_norm=model.clip_grad
        elif(isinstance(model,nn.DataParallel)):
            max_norm=model.module.clip_grad
        nn.utils.clip_grad_norm_(parameters=model.parameters(), max_norm=max_norm)
        #参数更新
        optimizer.step()
        scheduler.step()
    return float(train_loss)/len(train_loader)

def evaluate(data_loader:DataLoader,model:Any) -> dict:
    '''评估模型'''
    device=try_all_gpus()
    batch_loss=0
    matrics={}
    model.eval()
    batch_preds=[]
    batch_labels=[]
    if(isinstance(model,NERModel)):
        labels_padding_value=model.labels_padding_value
    elif(isinstance(model,nn.DataParallel)):
        labels_padding_value=model.module.labels_padding_value
    with torch.no_grad():
        for data_dict in tqdm(data_loader):
            data_dict=delete_attr(data_dict)
            labels=data_dict["batch_labels"].to(device[0])
            mask=data_dict["attention_mask"].to(device[0])
            input_ids=data_dict["input_ids"].to(device[0])
            padding_starts=data_dict["padding_starts"].to(device[0])

            padded_labels=pad_sequence([label[1:idx-1] for label,idx in zip(labels,padding_starts)],batch_first=True,padding_value=labels_padding_value)
            label_mask=padded_labels.gt(labels_padding_value)

            loss,logits=model(input_ids=input_ids,attention_mask=mask,labels=labels,padding_starts=padding_starts)
            
            # (batch_size, max_len - padding_label_len)
            if(isinstance(model,NERModel)):
                batch_output=model.crf.viterbi_decode(logits,mask=label_mask)
            elif(isinstance(model,nn.DataParallel)):
                batch_output=model.module.crf.viterbi_decode(logits,mask=label_mask)
            # batch_output=logits.argmax(dim=2)
            # (batch_size, max_len)
            labels=labels.to('cpu').numpy()
            batch_preds.extend([[idx for idx in indices] for indices in batch_output])
            # (batch_size, max_len - padding_label_len)
            batch_labels.extend([[idx for idx in indices if idx>labels_padding_value] for indices in labels])

            batch_loss+=loss.sum().item()
    assert len(batch_labels)==len(batch_preds)
    batch_acc,batch_recall,batch_f1=compute_scores(batch_preds,batch_labels)
    matrics["loss"]=float(batch_loss)/len(data_loader)
    matrics["accuracy"]=batch_acc
    matrics["recall"]=batch_recall
    matrics["f1"]=batch_f1
    return matrics


def train(train_data:tuple,val_data:tuple,model:NERModel,optimizer:Any,scheduler:Any,num_epochs:int,
          batch_size:int,labels_to_ids:dict,NERConfig:NERConfig) -> None:
    '''训练模型'''
    logging.info('--------Start Training--------')
    print('--------Start Training--------')
    train_dataset=DataSequence(train_data,labels_to_ids,NERConfig.bert_path,NERConfig.bert_max_length,NERConfig.labels_padding_value)
    val_dataset=DataSequence(val_data,labels_to_ids,NERConfig.bert_path,NERConfig.bert_max_length,NERConfig.labels_padding_value)
    train_loader=DataLoader(train_dataset,num_workers=NERConfig.num_workers,batch_size=batch_size,collate_fn=train_dataset.collate_fn,
                            shuffle=True)
    val_loader=DataLoader(val_dataset,num_workers=NERConfig.num_workers,batch_size=batch_size,collate_fn=val_dataset.collate_fn)
    train_loss=[]
    val_loss=[]
    val_acc=[]
    val_recall=[]
    val_f1=[]
    device=try_all_gpus()
    model.to(device[0])
    #model=nn.DataParallel(model,device_ids=device)#
    #model.cuda(device[0])
    best_val_f1=0.0
    patience_counter=0
    for epoch in range(num_epochs):
        epoch_train_loss=train_epoch(train_loader,model,optimizer,scheduler)
        train_loss.append(epoch_train_loss)
        val_dict=evaluate(val_loader,model)
        val_loss.append(val_dict["loss"])
        val_acc.append(val_dict["accuracy"])
        val_recall.append(val_dict["recall"])
        val_f1.append(val_dict["f1"])
        logging.info(f'Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f} | Validate Recall: {val_recall[-1]:.3f} | Validate F1: {val_f1[-1]:.3f}')
        print(f'Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f} | Validate Recall: {val_recall[-1]:.3f} | Validate F1: {val_f1[-1]:.3f}')
        #根据f1分数早停
        improve_f1=val_f1[-1]-best_val_f1
        if(improve_f1>1e-5):
            best_val_f1=val_f1[-1]
            if(isinstance(model,nn.DataParallel)):
                torch.save(model.module,NERConfig.saving_model_dir)
            elif(isinstance(model,NERModel)):
                torch.save(model,NERConfig.saving_model_dir)
            # model.save_pretrained(NERConfig.saving_model_path)
            logging.info('--------Save best model!--------')
            print('--------Save best model!--------')
            if(improve_f1<NERConfig.patience):
                patience_counter+=1
            else:
                patience_counter=0
        else:
            patience_counter+=1
        if(patience_counter>=NERConfig.patience_num and epoch>NERConfig.min_num_epochs):
            logging.info(f'Early stopping at epoch {epoch+1}.\n\
Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f} | Validate Recall: {val_recall[-1]:.3f} | Validate F1: {val_f1[-1]:.3f} \n\
Best F1: {best_val_f1:.3f}')
            print(f'Early stopping at epoch {epoch+1}.\n\
Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f} | Validate Recall: {val_recall[-1]:.3f} | Validate F1: {val_f1[-1]:.3f} \n\
Best F1: {best_val_f1:.3f}')
            # d2l.plot(list(range(1,num_epochs+1)),[train_loss,val_loss,val_acc,val_recall,val_f1],xlabel='epoch',
            #          ylabel='loss and scores',legend=['train_loss','val_loss','val_acc','val_recall','val_f1'],
            #          fmts=('-','r-','r--','r-.','r:'))
            break
    logging.info('Training Finished!')
    print('Training Finished!')
    # d2l.plot(list(range(1,num_epochs+1)),[train_loss,val_loss,val_acc,val_recall,val_f1],xlabel='epoch',
    #          ylabel='loss and scores',legend=['train_loss','val_loss','val_acc','val_recall','val_f1'],
    #          fmts=('-','r-','r--','r-.','r:'))
