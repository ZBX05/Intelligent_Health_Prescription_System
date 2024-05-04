

bert_path='f:\\system\\nlp\\model'
train_log_dir='f:\\system\\nlp\\ir\\Bert-TextRNN\\log\\TrainLog.log'
saving_model_dir='f:\\system\\nlp\\ir\\Bert-TextRNN\\model\\model.pth'
saving_model_state_dir='f:\\system\\nlp\\ir\\Bert-TextRNN\\model\\model_state.pth'
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

# labels_dict={
#     "病症":{
#         "定义":1,
#         "病因":2,
#         "临床表现(病症表现)":3,
#         "治疗方法":4
#         },
#     "治疗方案":{
#         "化验/体检方案":5,
#         "治疗时间":6,
#         "方法":7,
#         "正常指标":8
#         },
#     "其他":{
#         "无法确定":0
#         }
# }

num_workers=4

proportion='8:1:1'

ids_padding_value=0
bert_max_length=512


num_labels=9

hidden_dropout=0.3
gru_embedding_size=768
hidden_size=384
gru_dropout=0.5

full_fine_tuning=True
clip_grad=5
batch_size=16
num_epochs=50
learning_rate=3e-6
weight_decay=0.01

min_num_epochs=10
patience=0.0002
patience_num=5