

bert_path='f:\\system\\nlp\\model'
train_log_dir='f:\\system\\nlp\\ir\\Bert-TextRNN-Att\\log\\TrainLog.log'
saving_model_dir='f:\\system\\nlp\\ir\\Bert-TextRNN-Att\\model\\model.pth'
saving_model_state_dir='f:\\system\\nlp\\ir\\Bert-TextRNN-Att\\model\\model_state.pth'
data_dir='f:\\system\\nlp\\ir\\data\\KUAKE_QIC_data.json'
# data_dir='f:\\system\\nlp\\ir\\data\\CMID_test.json'

labels_dict={
    "病情诊断":1,
    "病因分析":2,
    "治疗方案":3,
    "就医建议":4,
    "指标解读":5,
    "疾病表述":6,
    "功效作用":7,
    "后果表述":8,
    "其他":0
}


num_workers=4

proportion='8:1:1'

ids_padding_value=0
# labels_padding_value=-1
bert_max_length=64


num_labels=9

gru_embedding_size=768
hidden_size=384
classified_size=64
gru_dropout=0.5
attention_dropout=0.3

full_fine_tuning=True
clip_grad=5
batch_size=16
num_epochs=50
learning_rate=3e-6
# learning_rate=1e-6
weight_decay=0.01

min_num_epochs=10
patience=0.0002
patience_num=5