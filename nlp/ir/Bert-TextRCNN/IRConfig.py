

bert_path='f:\\system\\nlp\\model'
train_log_dir='f:\\system\\nlp\\ir\\Bert-TextRCNN\\log\\TrainLog.log'
saving_model_dir='f:\\system\\nlp\\ir\\Bert-TextRCNN\\model\\model.pth'
saving_model_state_dir='f:\\system\\nlp\\ir\\Bert-TextRCNN\\model\\model_state.pth'
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

# labels_dict={
#     "病症":{
#         "所属科室":1,
#         "治愈率":2,
#         "病症禁忌":3,
#         "定义":4,
#         "相关病症":5,
#         "推荐医院":6,
#         "病因":7,
#         "诱因":8,
#         "严重性":9,
#         "临床表现(病症表现)":10,
#         "治疗方法":11,
#         "禁忌":12,
#         "传染性":13,
#         "预防":14
#         },
#     "药物":{
#         "价钱":15,
#         "副作用":16,
#         "作用":17,
#         "适用症":18,
#         "功效":19,
#         "用法":20,
#         "成分":21,
#         "禁忌":22,
#         "设备用法":23,
#         "药物禁忌":24
#         },
#     "其他":{
#         "养生":25,
#         "多问":26,
#         "两性":27,
#         "对比":28,
#         "无法确定":0,
#         "设备用法":29,
#         "整容":30
#         },
#     "治疗方案":{
#         "疗效":31,
#         "正常指标":32,
#         "方法":33,
#         "治疗时间":34,
#         "化验/体检方案":35,
#         "临床意义/检查目的":36,
#         "有效时间":37,
#         "恢复时间":38,
#         "费用":39,
#         "恢复":40,
#         "手术时间":41
#     }
# }

num_workers=4

proportion='8:1:1'

ids_padding_value=0
# labels_padding_value=-1
bert_max_length=64


num_labels=9

pooler_kernel_size=32
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