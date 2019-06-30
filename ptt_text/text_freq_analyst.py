import jieba
import jieba.analyse
from collections import Counter
import os
import numpy as np

#import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image



class text_freq_analyst:
    cwd = os.getcwd()
    jieba.set_dictionary(os.path.join(cwd,'ptt_text','dict','dict.txt.big'))
    stop_words = open(os.path.join(cwd,'ptt_text','data','stop_words_gossiping.txt'),encoding='utf8').read()
    
    def __init__(self,text):
        self.text = text
        self.words = [t for t in jieba.cut(text, cut_all=False) if t not in self.stop_words]
    
    
    def freq_summary(self,topK):
        words = self.words
        tf = sorted(Counter(words).items(), key=lambda x:x[1],reverse=True)
        sub_combine_title = ''.join(words)
        #print('斷詞結果:\n ' , ','.join(words))
        #print('top 10 term freq:\n',tf[:topK])
        
        #tf-idf
        tags = jieba.analyse.extract_tags(sub_combine_title,topK=topK,withWeight=True)
        
        tf_idf_result = {}
        for tag, weight in tags:
            tf_idf_result.update( {tag:np.round(weight,3)})
            
        return tf[:topK],tf_idf_result
    
    
    ### word cloud  
    def word_cloud_generator(self):
        words = self.words
        mask = np.array(Image.open("ptt_text/cloud_template.png"))
        wc = WordCloud(font_path= os.path.join(self.cwd,'ptt_text','fonts\\NotoSansMonoCJKtc-Regular.otf'), #設置字體
                       background_color="white", #背景顏色
                       max_words = 2000, mask = mask)
        wc.generate_from_frequencies(frequencies = Counter(words))
        
        #image_colors = ImageColorGenerator(mask)
        '''
        plt.figure(figsize=(10,6))
        plt.imshow(wc)
        plt.axis("off")
        plt.show()
        '''
        return wc
  