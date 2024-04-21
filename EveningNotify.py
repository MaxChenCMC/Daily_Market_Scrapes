"""
from io import StringIO
from bs4 import BeautifulSoup
import os, glob
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
# !pip install nbformat --upgrade
# !pip install -U kaleido
"""
import requests, pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from datetime import datetime, timedelta
from NotifyBase import NotifyBase
import lxml # 本機沒遇到，反而github workflow要求裝


def TwseT86YYYYMMDD(audience: str):
    '''
    '30 8 * * 1-5'
    '''
    if datetime.now().weekday() == 5: YYYYMMDD = (datetime.now() - timedelta(days = 1)).strftime("%Y%m%d")
    elif datetime.now().weekday() == 6: YYYYMMDD = (datetime.now() - timedelta(days = 2)).strftime("%Y%m%d")
    else: YYYYMMDD = datetime.now().strftime("%Y%m%d")
    res = requests.get(f'https://www.twse.com.tw/rwd/zh/fund/T86?date={YYYYMMDD}&selectType=ALL&response=json&_=1713717436223').json()
    df = pd.DataFrame.from_dict(res['data'])
    df.columns = res['fields']
    df = df[(df['證券代號'].str.len() == 4)][["證券名稱", "三大法人買賣超股數"]]
    df.iloc[:,-1:] = df.iloc[:,-1:].apply(lambda x: x.str.replace(',', '').astype(float)).apply(lambda x: x / 1000).apply(lambda x: round(x, 0)).sort_values(by = '三大法人買賣超股數', ascending = False)
    df.columns = ["買超", "張數"]
    df.reset_index(drop = True, inplace = True)
    df_ = df.copy()
    df_.sort_values(by = '張數', ascending = True, inplace = True)
    df_.columns = ["賣超", "張數"]
    df_.reset_index(drop = True, inplace = True)
    df = pd.concat([df.head(),df_.head()], axis=1)

    title = "▌三大法人買賣超日報"
    url1 = "https://www.twse.com.tw/zh/trading/foreign/t86.html"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url1, df.iloc[:,:2].to_string(index = False), df.iloc[:,2:].to_string(index = False) ]]
    NotifyBase(audience, "文", "\n".join(msg))


def MopsYYYMMDD(audience: str):
    '''
    '30 8 * * 1-5'
    不能選"_q1"會爬不到，過12想爬只能手動寫死日期
    '''
    # Monday = 0, Friday = 4
    if datetime.now().weekday() == 5: YYYMMDD = datetime.now() - timedelta(days = 1)
    elif datetime.now().weekday() == 6: YYYMMDD = datetime.now() - timedelta(days = 2)
    else: YYYMMDD = datetime.now()
    url = f"https://mops.twse.com.tw/mops/web/t56sb12?encodeURIComponent=1&run=&step=2&year={str(YYYMMDD.year-1911)}&month={YYYMMDD.strftime('%m')}&day={YYYMMDD.strftime('%d')}&report=SY&firstin=true"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    response = requests.post(url, headers = headers)
    dfs = pd.read_html(StringIO(response.text))
    df = pd.concat([_ for _ in dfs if not _.empty])
    df = df[[('公司名稱', '公司名稱'), ('公司 代號', '公司 代號'),('預定轉讓總股數', '自有持股')]]
    df.columns = ["公司","代號","預定轉讓"]
    df["代號"] = df["代號"].apply(lambda x: str(x))

    title = "▌股權轉讓事前申報"
    url = "https://mops.twse.com.tw/mops/web/t56sb12_q1"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.dropna().to_string(index = False, col_space = 10)]]
    NotifyBase(audience, "文", "\n".join(msg))

    
def AnnouncementNoticeYYYYMMDD(audience: str):
    '''
    '30 8 * * 1-5'
    '''
    if datetime.now().weekday() == 5: YYYYMMDD = (datetime.now() - timedelta(days = 1)).strftime("%Y%m%d")
    elif datetime.now().weekday() == 6: YYYYMMDD = (datetime.now() - timedelta(days = 2)).strftime("%Y%m%d")
    else: YYYYMMDD = datetime.now().strftime("%Y%m%d")
    YYYYMMDD = "20240419"
    response = requests.get(f"https://www.twse.com.tw/rwd/zh/announcement/notice?querytype=1&stockNo=&selectType=&startDate={YYYYMMDD}&endDate={YYYYMMDD}&sortKind=STKNO&response=json").json()["data"]
    # [[response[i][2],response[i][4]+"\n\n"] for i in range(len(response))]
    # df = pd.DataFrame([[response[i][2],response[i][4][:35]] for i in range(len(response))], columns=['Company', 'Details']).head(10)
    [[response[i][2],response[i][4]+"\n\n"] for i in range(len(response))]
    df = pd.DataFrame([(response[i][1],response[i][2])for i in range(len(response))], columns=['Company', 'Details']).head(10)    
    title = "▌注意有價證券"
    url = "https://www.twse.com.tw/zh/announcement/notice.html"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.to_string(index = False)]]
    NotifyBase(audience, "文", "\n".join(msg))
   
    
TwseT86YYYYMMDD("0")
MopsYYYMMDD("0")
AnnouncementNoticeYYYYMMDD("0")

