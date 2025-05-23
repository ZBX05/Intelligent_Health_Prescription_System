from typing import Any
from torch import Tensor
from torch import nn
from transformers import BertModel,BertConfig
from torch.utils.data import DataLoader
import torch.nn.functional as F
from tqdm import tqdm
from functionsAndClasses import *
from math import inf
import IRConfig

class BertTextCNN(nn.Module):
    def __init__(self,IRConfig:IRConfig,activation:Any) -> None:
        super(BertTextCNN,self).__init__()
        self.clip_grad=IRConfig.clip_grad
        self.num_labels=IRConfig.num_labels
        self.config=BertConfig.from_pretrained(IRConfig.bert_path)
        self.bert=BertModel.from_pretrained(IRConfig.bert_path,config=self.config)
        self.convs=nn.ModuleList(
            [nn.Conv2d(in_channels=1,out_channels=IRConfig.num_filters,kernel_size=(k,IRConfig.embedding_size),stride=IRConfig.stride) 
             for k in IRConfig.filter_sizes]
        )
        self.activation=activation
        self.dropout=nn.Dropout(IRConfig.dropout)
        self.classifier=nn.Linear(IRConfig.num_filters*len(IRConfig.filter_sizes),IRConfig.num_labels)
        self.ids_padding_value=IRConfig.ids_padding_value
    
    def conv_pool(self,X:Tensor,conv:nn.Conv2d) -> Tensor:
        X=conv(X)  # shape [batch_size, out_channels, x.shape[1] - conv.kernel_size[0] + 1, 1]
        X=self.activation(X)
        X=X.squeeze(3)  # shape [batch_size, out_channels, x.shape[1] - conv.kernel_size[0] + 1]
        size=X.size(2)
        X=F.max_pool1d(X,size)   # shape[batch+size, out_channels, 1]
        X=X.squeeze(2)  # shape[batch+size, out_channels]
        return X
    
    def forward(self,input_ids:Tensor,token_type_ids:Tensor=None,attention_mask:Tensor=None,position_ids:Tensor=None,
                inputs_embeds:Tensor=None,head_mask:Tensor=None) -> Tensor:
        outputs=self.bert(input_ids,
                          attention_mask=attention_mask,
                          token_type_ids=token_type_ids,
                          position_ids=position_ids,
                          inputs_embeds=inputs_embeds,
                          head_mask=head_mask)
        sequence_output=outputs[0].unsqueeze(1)
        conv_output=torch.cat([self.conv_pool(sequence_output,conv) for conv in self.convs], 1)
        dropout_output=self.dropout(conv_output)
        classifier_output=self.classifier(dropout_output)
        return classifier_output
    
def train_epoch(train_loader:DataLoader,model:Any,optimizer:Any,scheduler:Any,loss:Any) -> float:
    '''对模型进行一次迭代的训练'''
    device=try_all_gpus()
    train_loss=0
    model.train()
    for train_data_dict in tqdm(train_loader):
        train_data_dict=delete_attr(train_data_dict)
        train_labels=train_data_dict["labels"].to(device[0])
        mask=train_data_dict["attention_mask"].to(device[0])
        input_ids=train_data_dict["input_ids"].to(device[0])

        optimizer.zero_grad()
        outputs=model(input_ids=input_ids,attention_mask=mask)
        l=loss(outputs,train_labels)
        train_loss+=l.sum().item()
        l.sum().backward()
        if(isinstance(model,BertTextCNN)):
            max_norm=model.clip_grad
        elif(isinstance(model,nn.DataParallel)):
            max_norm=model.module.clip_grad
        nn.utils.clip_grad_norm_(model.parameters(),max_norm)
        optimizer.step()
        scheduler.step()
    return float(train_loss)/len(train_loader)

def evaluate(data_loader:DataLoader,model:Any,loss:Any) -> dict:
    '''评估模型'''
    device=try_all_gpus()
    batch_loss=0
    matrics={}
    model.eval()
    batch_preds=[]
    batch_labels=[]
    with torch.no_grad():
        for data_dict in tqdm(data_loader):
            data_dict=delete_attr(data_dict)
            labels=data_dict["labels"].to(device[0])
            mask=data_dict["attention_mask"].to(device[0])
            input_ids=data_dict["input_ids"].to(device[0])
            
            outputs=model(input_ids=input_ids,attention_mask=mask)
            l=loss(outputs,labels)
            labels=labels.to('cpu').numpy()
            batch_preds.extend([[label] for label in outputs.argmax(dim=1).tolist()])
            batch_labels.extend([[idx] for idx in labels])
            batch_loss+=l.sum().item()
    assert len(batch_preds)==len(batch_labels)
    batch_acc,batch_recall,batch_f1=compute_scores(batch_preds,batch_labels)
    matrics["loss"]=float(batch_loss)/len(data_loader)
    matrics["accuracy"]=batch_acc
    matrics["recall"]=batch_recall
    matrics["f1"]=batch_f1
    return matrics

def train(train_data:tuple,val_data:tuple,model:BertTextCNN,optimizer:Any,scheduler:Any,loss:Any,num_epochs:int,
          batch_size:int,labels_dict:dict,IRConfig:IRConfig) -> None:
    '''训练模型'''
    logging.info('--------Start Training--------')
    print('--------Start Training--------')
    train_dataset=DataSequence(train_data,labels_dict,IRConfig.bert_path,IRConfig.bert_max_length,IRConfig.ids_padding_value)
    val_dataset=DataSequence(val_data,labels_dict,IRConfig.bert_path,IRConfig.bert_max_length,IRConfig.ids_padding_value)
    train_loader=DataLoader(train_dataset,num_workers=IRConfig.num_workers,batch_size=batch_size,collate_fn=train_dataset.collate_fn,
                            shuffle=True)
    val_loader=DataLoader(val_dataset,num_workers=IRConfig.num_workers,batch_size=batch_size,collate_fn=val_dataset.collate_fn)
    train_loss=[]
    val_loss=[]
    val_acc=[]
    device=try_all_gpus()
    model.to(device[0])
    # model.to('cuda')
    # model=nn.DataParallel(model,device_ids=device)#
    # model.cuda(device[0])
    best_val_acc=0.0
    best_loss=inf
    patience_counter=0
    for epoch in range(num_epochs):
        epoch_train_loss=train_epoch(train_loader,model,optimizer,scheduler,loss)
        train_loss.append(epoch_train_loss)
        val_dict=evaluate(val_loader,model,loss)
        val_loss.append(val_dict["loss"])
        val_acc.append(val_dict["accuracy"])
        logging.info(f'Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f}')
        print(f'Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f}')
        #根据f1分数早停
        improve_acc=val_acc[-1]-best_val_acc
        if(improve_acc>1e-5):
            best_val_acc=val_acc[-1]
            if(isinstance(model,nn.DataParallel)):
                torch.save(model.module,IRConfig.saving_model_dir)
            elif(isinstance(model,BertTextCNN)):
                torch.save(model,IRConfig.saving_model_dir)
            # model.save_pretrained(NERConfig.saving_model_path)
            logging.info('--------Save best model!--------')
            print('--------Save best model!--------')
        #     if(improve_f1<IRConfig.patience):
        #         patience_counter+=1
        #     else:
        #         patience_counter=0
        # else:
        #     patience_counter+=1
        if(val_loss[-1]<best_loss):
            best_loss=val_loss[-1]
            patience_counter=0
        else:
            patience_counter+=1
        if(patience_counter>=IRConfig.patience_num and epoch>IRConfig.min_num_epochs):
            logging.info(f'Early stopping at epoch {epoch+1}.\n\
Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f}\nBest Accuracy: {best_val_acc:.3f}')
            print(f'Early stopping at epoch {epoch+1}.\n\
Epochs: {epoch+1} | Train Loss: {train_loss[-1]:.3f} | Validate Loss: {val_loss[-1]:.3f} | \
Validate Accuracy: {val_acc[-1]:.3f}\nBest F1: {best_val_acc:.3f}')
            # d2l.plot(list(range(1,num_epochs+1)),[train_loss,val_loss,val_acc,val_recall,val_f1],xlabel='epoch',
            #          ylabel='loss and scores',legend=['train_loss','val_loss','val_acc','val_recall','val_f1'],
            #          fmts=('-','r-','r--','r-.','r:'))
            break
    logging.info('Training Finished!')
    print('Training Finished!')
    # d2l.plot(list(range(1,num_epochs+1)),[train_loss,val_loss,val_acc,val_recall,val_f1],xlabel='epoch',
    #          ylabel='loss and scores',legend=['train_loss','val_loss','val_acc','val_recall','val_f1'],
    #          fmts=('-','r-','r--','r-.','r:'))
        