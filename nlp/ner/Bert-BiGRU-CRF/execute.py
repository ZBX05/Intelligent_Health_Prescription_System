from model import *
from functionsAndClasses import *
from transformers.optimization import get_cosine_schedule_with_warmup
from typing import Any
import NERConfig
import logging

def run(data:dict,NERConfig:NERConfig) -> None:
    #获取标签与实体之间的相互映射关系
    # labels_to_ids,ids_to_labels=get_labels_relation_with_ids(data_labels)
    labels_to_ids=NERConfig.labels_to_ids
    train_data=data["train"]
    val_data=data["val"]
    # NERConfig.num_labels=len(labels_to_ids)
    #定义优化器、调度器
    model=NERModel(NERConfig)
    #全部微调
    if NERConfig.full_fine_tuning:
        # model.named_parameters(): [bert, bilstm, classifier, crf]
        bert_optimizer=list(model.bert.named_parameters())
        gru_optimizer=list(model.bi_gru.named_parameters())
        classifier_optimizer=list(model.classifier.named_parameters())
        no_decay=['bias','LayerNorm.bias','LayerNorm.weight']
        optimizer_grouped_parameters=[
            {'params':[p for n, p in bert_optimizer if not any(nd in n for nd in no_decay)],
             'weight_decay':NERConfig.weight_decay},
            {'params':[p for n, p in bert_optimizer if any(nd in n for nd in no_decay)],
             'weight_decay':0.0},
            {'params':[p for n, p in gru_optimizer if not any(nd in n for nd in no_decay)],
             'lr':NERConfig.learning_rate*5,'weight_decay':NERConfig.weight_decay},
            {'params': [p for n, p in gru_optimizer if any(nd in n for nd in no_decay)],
             'lr':NERConfig.learning_rate*5,'weight_decay':0.0},
            {'params':[p for n, p in classifier_optimizer if not any(nd in n for nd in no_decay)],
             'lr':NERConfig.learning_rate*5,'weight_decay':NERConfig.weight_decay},
            {'params':[p for n, p in classifier_optimizer if any(nd in n for nd in no_decay)],
             'lr':NERConfig.learning_rate*5,'weight_decay':0.0},
            {'params':model.crf.parameters(),'lr':NERConfig.learning_rate*5}
        ]
    #只微调线性分类器
    else:
        param_optimizer=list(model.classifier.named_parameters())
        optimizer_grouped_parameters=[{'params': [p for n,p in param_optimizer]}]
    optimizer=torch.optim.AdamW(params=optimizer_grouped_parameters,lr=NERConfig.learning_rate,weight_decay=NERConfig.weight_decay)
    # optimizer=AdamW(optimizer_grouped_parameters,lr=NERConfig.learning_rate,weight_decay=NERConfig.weight_decay,correct_bias=False)
    train_steps_per_epoch=len(train_data[0]) // NERConfig.batch_size
    scheduler=get_cosine_schedule_with_warmup(optimizer,num_warmup_steps=(NERConfig.num_epochs//10)*train_steps_per_epoch,
                                                num_training_steps=NERConfig.num_epochs*train_steps_per_epoch)
    train(train_data=train_data,val_data=val_data,model=model,optimizer=optimizer,scheduler=scheduler,
          num_epochs=NERConfig.num_epochs,batch_size=NERConfig.batch_size,labels_to_ids=labels_to_ids,NERConfig=NERConfig)

def test(data:dict,NERConfig:NERConfig) -> None:
    test_data=data["test"]
    labels_to_ids=NERConfig.labels_to_ids
    test_dataset=DataSequence(test_data,labels_to_ids,NERConfig.bert_path,NERConfig.bert_max_length,NERConfig.labels_padding_value)
    test_loader=DataLoader(test_dataset,NERConfig.batch_size,shuffle=False,collate_fn=test_dataset.collate_fn)
    if(NERConfig.saving_model_dir is not None):
        logging.info(f'-------Loading Model From {NERConfig.saving_model_dir}--------')
        print(f'-------Loading Model From {NERConfig.saving_model_dir}--------')
        # model=NERModel.from_pretrained(NERConfig.saving_model_path)
        model=torch.load(NERConfig.saving_model_dir)
        logging.info('-------Model Loaded--------')
        print('-------Model Loaded--------')
    else:
        logging.error('-------No Model--------')
        print('-------No Model--------')
        return
    data=evaluate(test_loader,model)
    loss=data["loss"]
    acc=data["accuracy"]
    recall=data["recall"]
    f1=data["f1"]
    logging.info(f'Test Loss: {loss} | Test Accuracy: {acc} | Test Recall: {recall} | Test F1: {f1}')
    print(f'Test Loss: {loss} | Test Accuracy: {acc} | Test Recall: {recall} | Test F1: {f1}')
    logging.info('Testing finished.')
    print('Testing finished.')

def save_model_state(saving_model_dir:str,saving_model_state_dir:str):
    model=torch.load(saving_model_dir,map_location='cuda:0')
    torch.save(model.state_dict(),saving_model_state_dir)