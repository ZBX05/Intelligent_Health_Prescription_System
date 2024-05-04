from execute import *
import NERConfig


if __name__=='__main__':
    # logging.basicConfig(level=logging.INFO,filename=NERConfig.train_log_dir,filemode='w',
    #                 format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # #加载数据
    # data_text=read_text_list(NERConfig.data_dir)
    # data_labels=read_labels_list(NERConfig.data_dir)
    # #切分训练集、验证集、测试集
    # data=train_val_test_split(data_text,data_labels,NERConfig.proportion)
    # run(data,NERConfig)
    # test(data,NERConfig)
    save_model_state(NERConfig.saving_model_dir,NERConfig.saving_model_state_dir)