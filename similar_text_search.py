import jieba
from gensim import models


jieba.set_dictionary('info/text/dict.txt.big') 
stop_words = open('info/text/stops.txt',encoding='utf8').read() 

model = models.Word2Vec.load('./word2vec_model/word2vec_from_wiki_250d.model')

def similar_skill_search(listen_text,learned_skill):
    
    listen_words =[t for t in jieba.cut(listen_text, cut_all=False) if t not in stop_words] # 斷詞 & 移除停用字
    most_skill_score = -999
    for w in listen_words:
        skill_score = -999
        for skill in learned_skill:
            res = model.similarity(w,skill)
            if res>skill_score:
                simi_skill = skill
                skill_score = res
        print('"%s"最相近的skill 為 "%s" 相似度為: %f'%(w,simi_skill,skill_score))
        if skill_score>most_skill_score:
            most_skill_score = skill_score
            most_simi_skill = simi_skill
    
    #print('你是說"%s"相關的事嗎'%most_simi_skill)      
    return most_simi_skill,most_skill_score