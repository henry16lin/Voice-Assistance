# Voice-Assistance
語音助理實做  
  
環境: python3.6  
所需套件:  
speechrecognition  
pyaudio  
gtts  
pygame  
googletrans  
jieba  
gensim  
  
## Note:  
1. 因 word2vec 模型太大 無法放上來 請自己找語料庫訓練(by gensim), 並修改 *`similar_text_search.py`* 裡的model 路徑。如何訓練請參考 http://zake7749.github.io/2016/08/28/word2vec-with-gensim/   
2. 語音助理中有項功能是由PTT爬網後的結果summary，可先執行 `/ptt_text/ptt_parser.py` 抓取最新資料  
3. 語音助理說話時可能會聽到自己說話的聲音而錯亂，建議插上耳機 or 控制麥克風開關

## 執行:  
*`python voice_assistance.py`*


