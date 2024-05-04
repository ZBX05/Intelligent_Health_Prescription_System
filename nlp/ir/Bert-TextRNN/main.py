from execute import *
import logging
import IRConfig

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,filename=IRConfig.train_log_dir,filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    #加载数据
    data_text=read_text_list(IRConfig.data_dir)
    data_labels=read_labels_list(IRConfig.data_dir)
    #切分训练集、验证集、测试集
    data=train_val_test_split(data_text,data_labels,IRConfig.proportion)
    run(data,IRConfig)
    test(data,IRConfig)
    save_model_state(IRConfig.saving_model_dir,IRConfig.saving_model_state_dir)