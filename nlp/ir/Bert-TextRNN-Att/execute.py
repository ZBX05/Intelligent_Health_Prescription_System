from model import *
from functionsAndClasses import *
from transformers.optimization import get_cosine_schedule_with_warmup,get_linear_schedule_with_warmup
from typing import Any
import IRConfig
import logging

def run(data:dict,IRConfig:IRConfig) -> None:
    labels_dict=IRConfig.labels_dict
    train_data=data["train"]
    val_data=data["val"]
    # IRConfig.num_labels=len(labels_to_ids)
    #定义优化器、调度器
    model=IRModel(IRConfig,nn.ReLU())
    if IRConfig.full_fine_tuning:
        bert_optimizer=list(model.bert.named_parameters())
        gru_optimizer=list(model.bi_gru.named_parameters())
        attention_optimizer=list(model.att.named_parameters())
        classifier_optimizer=list(model.classifier.named_parameters())
        # classifier_2_optimizer=list(model.classifier_2.named_parameters())
        no_decay=['bias','LayerNorm.bias','LayerNorm.weight']
        optimizer_grouped_parameters=[
            {'params':[p for n, p in bert_optimizer if not any(nd in n for nd in no_decay)],
             'weight_decay':IRConfig.weight_decay},
            {'params':[p for n, p in bert_optimizer if any(nd in n for nd in no_decay)],
             'weight_decay':0.0},
            {'params':[p for n, p in gru_optimizer if not any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':IRConfig.weight_decay},
            {'params': [p for n, p in gru_optimizer if any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':0.0},
            {'params':[p for n, p in classifier_optimizer if not any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':IRConfig.weight_decay},
            {'params': [p for n, p in classifier_optimizer if any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':0.0},
            {'params':[p for n, p in attention_optimizer if not any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':IRConfig.weight_decay},
            {'params': [p for n, p in attention_optimizer if any(nd in n for nd in no_decay)],
             'lr':IRConfig.learning_rate*5,'weight_decay':0.0},
            # {'params':[p for n, p in classifier_2_optimizer if any(nd in n for nd in no_decay)],
            #  'lr':IRConfig.learning_rate*5,'weight_decay':0.0},
            # {'params': model.att.w,'lr':IRConfig.learning_rate*5}
        ]
    else:
        classifier_1_optimizer=list(model.classifier_1.named_parameters())
        # classifier_2_optimizer=list(model.classifier_2.named_parameters())
        optimizer_grouped_parameters=[{'params': [p for n,p in classifier_1_optimizer]},
                                    #   {'params':[p for n,p in classifier_2_optimizer]},
                                      {'params': model.w}]
    optimizer=torch.optim.AdamW(params=optimizer_grouped_parameters,lr=IRConfig.learning_rate,weight_decay=IRConfig.weight_decay)
    train_steps_per_epoch=len(train_data[0])//IRConfig.batch_size
    scheduler=get_cosine_schedule_with_warmup(optimizer,num_warmup_steps=(IRConfig.num_epochs//10)*train_steps_per_epoch,
                                                num_training_steps=IRConfig.num_epochs*train_steps_per_epoch)
    loss=nn.CrossEntropyLoss(reduction='none')
    train(train_data=train_data,val_data=val_data,model=model,optimizer=optimizer,scheduler=scheduler,loss=loss,
          num_epochs=IRConfig.num_epochs,batch_size=IRConfig.batch_size,labels_dict=labels_dict,IRConfig=IRConfig)

def test(data:dict,IRConfig:IRConfig) -> None:
    test_data=data["test"]
    labels_dict=IRConfig.labels_dict
    test_dataset=DataSequence(test_data,labels_dict,IRConfig.bert_path,IRConfig.bert_max_length,IRConfig.ids_padding_value)
    test_loader=DataLoader(test_dataset,IRConfig.batch_size,shuffle=False,collate_fn=test_dataset.collate_fn)
    if(IRConfig.saving_model_dir is not None):
        logging.info(f'-------Loading Model From {IRConfig.saving_model_dir}--------')
        print(f'-------Loading Model From {IRConfig.saving_model_dir}--------')
        # model=IRModel.from_pretrained(IRConfig.saving_model_path)
        model=torch.load(IRConfig.saving_model_dir)
        logging.info('-------Model Loaded--------')
        print('-------Model Loaded--------')
    else:
        logging.error('-------No Model--------')
        print('-------No Model--------')
        return
    loss=nn.CrossEntropyLoss(reduction='none')
    data=evaluate(test_loader,model,loss)
    loss=data["loss"]
    acc=data["accuracy"]
    recall=data["recall"]
    f1=data["f1"]
    logging.info(f'Test Loss: {loss} | Test Accuracy: {acc}')
    print(f'Test Loss: {loss} | Test Accuracy: {acc}')
    logging.info('Testing finished.')
    print('Testing finished.')

def save_model_state(saving_model_dir:str,saving_model_state_dir:str):
    model=torch.load(saving_model_dir,map_location='cuda:0')
    torch.save(model.state_dict(),saving_model_state_dir)