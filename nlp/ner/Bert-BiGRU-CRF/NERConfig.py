import os

#服务器
# bert_path='/home/noitom-server/PycharmProjects/pythonProject/Intelligent-Health-System/nlp/model'
# saving_model_dir='/home/noitom-server/PycharmProjects/pythonProject/Intelligent-Health-System/nlp/ner/Bert-BiGRU-CRF/model/model.pth'
# data_dir='/home/noitom-server/PycharmProjects/pythonProject/Intelligent-Health-System/nlp/ner/data/ccks_2017_2018_mmc.json'
# train_log_dir='/home/noitom-server/PycharmProjects/pythonProject/Intelligent-Health-System/nlp/ner/Bert-BiGRU-CRF/log/TrainLog.log'
#本地补充测试
# bert_path='f:\\system\\nlp\\model'
# saving_model_dir='f:\\system\\experiment\\ner\\Bert-BiGRU-CRF\\model\\model.pth'
# test_log_dir='f:\\system\\experiment\\ner\\Bert-BiGRU-CRF\\log\\TestLog.log'
# data_dir='f:\\system\\experiment\\ner\\data\\ccks_2017_2018_mmc.json'
# test_data_dir='f:\\system\\experiment\\ner\\data\\ccks_2019_cmeee.json'

bert_path='f:\\system\\nlp\\model'
saving_model_dir='f:\\system\\nlp\\ner\\Bert-BiGRU-CRF\\model\\model.pth'
saving_model_state_dir='f:\\system\\nlp\\ner\\Bert-BiGRU-CRF\\model\\model_state.pth'
# data_dir='f:\\system\\nlp\\ner\\data\\ccks_2017_2018_mmc.json'
data_dir='f:\\system\\nlp\\ner\\data\\ccks2017_task2_test.json'
train_log_dir='f:\\system\\nlp\\ner\\Bert-BiGRU-CRF\\log\\TrainLog.log'
# debug_log_dir='f:\\system\\nlp\\ner\\Bert-BiGRU-CRF\\log\\NERProcessLog.log'

# current_path=os.getcwd()
# parent_path=os.path.dirname(current_path)
# bert_path=os.path.dirname(parent_path)+'\\nlp\\model'
# saving_model_dir=current_path+'\\model\\model.pth'
# data_dir=parent_path+'\\data\\ccks_2017_2018_mmc.json'
# # data_dir=parent_path+'\\nlp\\ner\\data\\ccks2017_task2_test.json'
# train_log_dir=current_path+'\\log\\TrainLog.log'

labels_to_ids={
    'O': 0,
    'B-body': 1,
    'B-chec': 2,
    'B-cure': 3,
    'B-dise': 4,
    'B-symp': 5,
    'B-drug': 6,
    'I-body': 7,
    'I-chec': 8,
    'I-cure': 9,
    'I-dise': 10,
    'I-symp': 11,
    'I-drug': 12
}

ids_to_labels={_id: _label for _label,_id in list(labels_to_ids.items())}

proportion='8:1:1'

ids_padding_value=0
labels_padding_value=-1

bert_max_length=512

log_epoch=10#每隔多少代打印一次loss和acc
num_workers=4#创建DataLoader时的进程数
num_labels=13


hidden_dropout=0.3
gru_embedding_size=768
hidden_size=384
gru_dropout=0.5

full_fine_tuning=True
clip_grad=5
batch_size=8
num_epochs=50
learning_rate=3e-5
weight_decay=0.01

min_num_epochs=5
patience=0.0002
patience_num=10
