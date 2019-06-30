import time
import tempfile
import webbrowser
import re  #正規表示
import datetime
import matplotlib.pyplot as plt
import sqlite3
from pandas import read_sql_query
import speech_recognition
import wikipedia
import pyaudio   #for麥克風
from gtts import gTTS     #text to speech via google
from pygame import mixer  #說出聲音
from googletrans import Translator
from similar_text_search import similar_skill_search

from ptt_text.text_freq_analyst import text_freq_analyst



def speeker(texts,lang='zh-tw'):
    mixer.init()
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=texts,lang=lang)
        tts.save("{}.mp3".format(fp.name))
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play()


def listener():
    r = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        audio = r.listen(source)
    
    return r.recognize_google(audio,language = 'zh-tw')


def google_translator(texts,target_lang):
    translator = Translator()
    return translator.translate(texts,dest=target_lang).text



def skill_resp(listen_text):
    res_flag = 1
    
    if '翻譯' in listen_text:
        target_search_result = re.search('翻譯(.*)', listen_text)
        target_lang = target_search_result.group(1)
        if target_lang =='':
            speeker('你想翻譯成什麼語言?')
            target_lang = listener()
            print(target_lang)
        
        if target_lang in ['英文','日文','韓文']:
            speeker('請說出想翻譯的中文')

            translate_text = listener()
            print(translate_text)
            if '英文' in target_lang:
                res_text = google_translator(translate_text,target_lang='en')
                print('翻譯結果為:%s'%res_text)
                speeker(res_text,lang = 'en')
            elif '日文' in target_lang:
                res_text = google_translator(translate_text,target_lang='ja')
                print('翻譯結果為:%s'%res_text)
                speeker(res_text,lang = 'ja')
            elif '韓文' in target_lang:
                res_text = google_translator(translate_text,target_lang='ko')
                print('翻譯結果為:%s'%res_text)
                speeker(res_text,lang = 'ko')
                
        else:
            speeker('不好意思 我還不會這個語言')
        
    elif '天氣' in listen_text:
        speeker('請自己看氣象網站')
        url = 'https://weather.com'
        webbrowser.open(url, new=0, autoraise=True)
        
        
    elif ('時間' in listen_text) or ('幾點' in listen_text):
        now = datetime.datetime.now()
        res_text = '現在時間是 %d 點 %d 分' % (now.hour, now.minute)
        speeker(res_text)
    
    elif '告訴我什麼是' in listen_text:
        reg_ex = re.search('告訴我什麼是(.*)', listen_text)
        try:
            tmp_txt = google_translator(reg_ex.group(1),target_lang = 'en')
            print('wiki for "%s"'%tmp_txt)
            wiki_text = wikipedia.summary(tmp_txt,sentences=2)
            print(wiki_text)
            speeker(wiki_text,lang='en')
            #speeker(google_translator(wiki_text,target_lang = 'zh-tw'))
        except:
            speeker('不好意思 我不知道QAQ')
    
    
    elif '熱門話題' in listen_text:
        today = datetime.datetime.today().strftime('%Y/%m/%d')
        yesterday_obj = datetime.datetime.strptime(today, '%Y/%m/%d')- datetime.timedelta(days=1)
        date = datetime.datetime.strftime(yesterday_obj,'%Y/%m/%d')
        
        speeker('讓我來統整一下...')
        
        sql_str = " select * from gossiping_article_view where AUTHOR <>\'-\' and DATE in (\'" + date[-5:] + "\');"
        conn = sqlite3.connect("ptt_text/ptt.db")
        query_article_menu = read_sql_query(sql_str, conn)
        conn.commit()
        conn.close
        
        single_date_article_menu = query_article_menu[query_article_menu['DATE']==date[-5:]]
        daily_article_cnt = single_date_article_menu.shape[0]
        
        title = single_date_article_menu['TITLE'].tolist()
        text = ','.join(title)
        text_obj = text_freq_analyst(text)
        top_fq,tf_idf_result = text_obj.freq_summary(3)
        wc = text_obj.word_cloud_generator()
        
        topic_resp_str = '最近的熱門話題第一名是'+ top_fq[0][0]+'第二名是'+ top_fq[1][0]+'第三名是'+ top_fq[2][0]
        speeker(topic_resp_str)
        
        # graph wordcloud
        plt.figure(figsize = (12,12))
        plt.imshow(wc,aspect='equal')
        plt.axis("off")
        plt.title(date+' Article Wordcloud\n (article count:'+str(daily_article_cnt)+')')
        plt.show()
    
    elif '笑話' in listen_text:
        from random import randint
        jokes = []
        f = open('./info/joke.txt','r')
        for line in f:
            jokes.append(line)
        f.close
        
        ind = randint(0,len(jokes))
        res_text = jokes[ind]
        print(res_text)
        speeker(res_text)
        
    elif ('拜拜' in listen_text) or ('再見' in listen_text):
        speeker('有緣再相會')
        res_flag = -1
    
    else: 
        res_flag = 0
        
    return res_flag




qa = {
      '你好嗎':'我很好',
      '你好': '你也好',
      '你今年幾歲': '我正值二八年華',
      '你幾歲':'我18歲',
      '你是誰':'我是你的語音小助手',
      '謝謝':'不客氣',
      '你叫什麼名字':'我是沒有名子的卑微小助手'
      }

default_ans = '我還在學習中 請自己估狗'


res_cnt = 0
fail_cnt = 0
learned_skill = ['翻譯','笑話','拜拜','再見','時間','幾點','熱門話題','天氣']

while True:
    if res_cnt==0:
        speeker('你好我是你的語音小助手 想要我幫你什麼嗎')
        res_cnt  = 1
    
    try:
        listen_text = listener()
        print(listen_text)
        
        if  listen_text in [q for q in qa]:
            speeker( qa.get(listen_text,default_ans) )
        
        else: #若詢問中有打中關鍵字則以對應的技能回應 
            res_flag = skill_resp(listen_text)
        
        
            if res_flag ==0: #若上面沒打中關鍵字 則已單詞相近字來找最相近的回應
                most_simi_skill,most_skill_score = similar_skill_search(listen_text,learned_skill)
                
                if most_skill_score>=0.4:
                    listen_text = most_simi_skill
                    print('most_simi_skill:%s, score:%f'%(most_simi_skill,most_skill_score))
                    res_flag = skill_resp(listen_text)
                    
                else:
                    speeker(default_ans)
            
            if res_flag ==-1: #for 再見相似詞 跳出while
                time.sleep(2)
                break
                
        fail_cnt = 0
    
    except:
        print('say something...')
        fail_cnt +=1
               
    if fail_cnt == 2:
        speeker('說話啊')
    
    if fail_cnt >4:
        speeker('不說話就滾')
        time.sleep(3)
        break





'''
#### opencc 簡轉繁
f = open('wiki_texts.txt',encoding='utf8')
wiki_texts = f.readlines()
f.close()


from opencc import OpenCC 
cc = OpenCC('s2t')
cc.set_conversion('s2tw') 

wiki_zh_tw = []
for i in range(len(wiki_texts)):
    to_convert = wiki_texts[i]
    converted = cc.convert(to_convert)
    wiki_zh_tw.append(converted)

f = open('wiki_zh_tw.txt','a',encoding='utf8')
for i in range(len(wiki_zh_tw)):
    f.write("%s\n" % wiki_zh_tw[i])

'''





