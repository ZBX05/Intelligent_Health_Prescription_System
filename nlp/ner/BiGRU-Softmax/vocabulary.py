import numpy as np
from d2l import torch as d2l
#import jieba
import json
import numpy as np
import pandas as pd
import logging
import os
from typing import Any
import NERConfig

class Vocabulary:
    def __init__(self,vocab_dir:str) -> None:
        self.vocab_dir=vocab_dir
        self.word_to_id=None
        self.id_to_word=None
    
    def load_vocab(self) -> None:
        if os.path.exists(self.vocab_dir):
            data=np.load(self.vocab_dir,allow_pickle=True)
            self.word_to_id=data["word_to_id"][()]
            self.id_to_word=data["id_to_word"][()]
        else:
            logging.error('Please provide a vocabulary path!')
            print('Please provide a vocabulary path!')
            exit()
    
    def __len__(self) -> int:
        try:
            return len(self.word_to_id)
        except:
            return 0

    def vocab_size(self) -> int:
        try:
            return len(self.word_to_id)
        except:
            return 0

    def get_word_to_id(self) -> dict:
        if(self.word_to_id is not None):
            return self.word_to_id
        else:
            logging.info('Automatically load vocabulary.')
            print('Automatically load vocabulary.')
            self.load_vocab()
            return self.word_to_id
    
    def get_id_to_word(self) -> dict:
        if(self.id_to_word is not None):
            return self.id_to_word
        else:
            logging.info('Automatically load vocabulary.')
            print('Automatically load vocabulary.')
            self.load_vocab()
            return self.id_to_word
    
    def word_trans_id(self,word:str) -> int:
        if(self.word_to_id is None):
            logging.info('Automatically load vocabulary.')
            print('Automatically load vocabulary.')
            self.load_vocab()
        try:
            return self.word_to_id[word]
        except:
            return self.word_to_id[self.id_trans_word(len(self.id_to_word)-1)]
    
    def id_trans_word(self,id:int) -> str:
        if(self.id_to_word is None):
            logging.info('Automatically load vocabulary.')
            print('Automatically load vocabulary.')
            self.load_vocab()
        return self.id_to_word[id]
    
    def word_ids(self,text:str) -> tuple:
        word_freq_id_list=[]
        for word in text:
            word_freq_id_list.append(self.word_trans_id(word))
        word_id_list=list(range(0,len(word_freq_id_list)))
        return word_freq_id_list,word_id_list
