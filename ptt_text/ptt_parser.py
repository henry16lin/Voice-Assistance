import requests
from requests_html import HTML
import sqlite3
from bs4 import BeautifulSoup
import datetime
import time
import warnings


def daily_base_article_parser(date_str):
    warnings.filterwarnings("ignore")
    
    query_time_obj = datetime.datetime.strptime(date_str, '%Y/%m/%d')
    
    # 18歲認證
    payload = {
            'from':'/bbs/Gossiping/index.html',
            'yes':'yes'
            }
    
    #initial last page
    url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
    rs = requests.session()
    res = rs.post('https://www.ptt.cc/ask/over18',verify=False,data=payload)
    res = rs.get(url,verify=False)
    soup = BeautifulSoup(res.text)
    
    
    #尋找上一頁的 index
    html = HTML(html=res.text)
    controls = html.find('.action-bar a.btn.wide')
    link = str(controls[1]).split('/')[-1]
    page_url = 'https://www.ptt.cc/bbs/Gossiping/'+link[:-2]
    page = int(page_url.split('index')[1][:-5])
    
    
    conn = sqlite3.connect('ptt.db') #create/connect to db
    cursor = conn.cursor()
    table_creator(cursor)    #create table if table doesn't exist
    
    
    article_cnt = 0
    today_flag = True
    while today_flag:
        #取的最新page的 text
        rs = requests.session()
        res = rs.post('https://www.ptt.cc/ask/over18',verify=False,data=payload)
        res = rs.get(page_url,verify=False)
        soup = BeautifulSoup(res.text)
    
        for entry in soup.select('.r-ent'):    
            #判斷文章是否為當日
            #print(entry.select('.nrec')[0].text)
            tmp_date = entry.select('.date')[0].text
            if tmp_date[0]==' ':  #個位數月份PTT上為補空白
                artical_date = '0'+tmp_date[1:]
            else:
                artical_date = tmp_date
                
            today_article_flag = (artical_date == date_str[-5:])
            
            if today_article_flag:
                date= artical_date
                author=( entry.select('.author')[0].text)
                title=( entry.select('.title')[0].text)
                push = (entry.select('.nrec')[0].text)
                if push == '':
                    push = '0'
                tmp = str(entry.select('.title')[0])
                url=('www.ptt.cc/bbs/Gossiping/'+tmp[str.find(tmp,'Gossiping/')+10:str.find(tmp,'.html')+5])
                
                rpt_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                
                
                sqlstr = 'INSERT OR REPLACE into gossiping_article_view (PAGE,DATE,AUTHOR,PUSH,TITLE,ARTICLE_URL,RPT_DATETIME) values(?,?,?,?,?,?,?)'
                cursor.execute(sqlstr,[page,date,author,push,title,url,rpt_datetime])
                
                article_cnt += 1
        
        #單頁最後的artical_date 與query date 比較 往前翻頁
        full_artical_date = today[:4]+'/'+artical_date
        artical_date_obj = datetime.datetime.strptime(full_artical_date, '%Y/%m/%d')
        if query_time_obj < artical_date_obj:
            if query_time_obj<(artical_date_obj-datetime.timedelta(days=1)):
                page = page - 50
                print('\n**date: %s , jump 50 pages before\n**' %artical_date )
            else:
                page = page - 1
                print('**\ndate: %s , jump 1 page before\n**' %artical_date )
        elif query_time_obj == artical_date_obj:
            page = page - 1
            print('**\ndate: %s , jump 1 page before\n**' %artical_date )
        else:
            today_flag = False

        print('### finish search page index: %d with latest date is: %s ###' %(page,artical_date))
        page_url = 'https://www.ptt.cc/bbs/Gossiping/index'+str(page)+'.html'
    
    print('total insert article count: %d'%article_cnt)
    conn.commit()
    conn.close
    
    warnings.resetwarnings()



def table_creator(cursor):
    try:
        insert_sql_str = """CREATE TABLE gossiping_article_view (
        	PAGE	INTEGER NOT NULL,
        	DATE	TEXT NOT NULL,
        	AUTHOR	TEXT,
        	PUSH	TEXT,
        	TITLE	TEXT,
        	ARTICLE_URL	TEXT,
        	RPT_DATETIME	TEXT NOT NULL,
        	PRIMARY KEY(DATE,AUTHOR,TITLE)
        );"""
        cursor.execute(insert_sql_str)
    except:
        print('table already exist, parse data and insert to exists table...')




if __name__ == '__main__':
    today = datetime.datetime.today().strftime('%Y/%m/%d')
    yesterday_obj = datetime.datetime.strptime(today, '%Y/%m/%d')- datetime.timedelta(days=1)
    yesterday = datetime.datetime.strftime(yesterday_obj,'%Y/%m/%d')
    print('parse yesterday %s article menu' %yesterday)
    
    daily_base_article_parser(yesterday)


#daily_base_article_parser('2019/04/26')
