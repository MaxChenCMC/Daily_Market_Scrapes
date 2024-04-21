import requests, pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from NotifyBase import NotifyBase


def MopsYYYMMDD(audience: str):
    '''
    '30 0 * * 1-5'
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
    df = df[[('公司名稱', '公司名稱'),('申報人身分', '申報人身分'),('目前持有股數', '自有持股'),('預定轉讓總股數', '自有持股')]]
    df.columns = ["公司","申報身份","現有","預定轉讓"]

    title = "▌股權轉讓事前申報"
    url = "https://mops.twse.com.tw/mops/web/t56sb12_q1"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.dropna().to_string(index = False, col_space = 8)]]
    NotifyBase(audience, "文", "\n".join(msg))
    
    
def AnnouncementNoticeYYYYMMDD(audience: str):
    '''
    '30 0 * * 1-5'
    '''
    if datetime.now().weekday() == 5: YYYYMMDD = (datetime.now() - timedelta(days = 1)).strftime("%Y%m%d")
    elif datetime.now().weekday() == 6: YYYYMMDD = (datetime.now() - timedelta(days = 2)).strftime("%Y%m%d")
    else: YYYYMMDD = datetime.now().strftime("%Y%m%d")
    response = requests.get(f"https://www.twse.com.tw/rwd/zh/announcement/notice?querytype=1&stockNo=&selectType=&startDate={YYYYMMDD}&endDate={YYYYMMDD}&sortKind=STKNO&response=json").json()["data"]
    [[response[i][2],response[i][4]+"\n\n"] for i in range(len(response))]
    df = pd.DataFrame([[response[i][2],response[i][4][:35]] for i in range(len(response))], columns=['Company', 'Details']).head(10)
    
    title = "▌注意有價證券"
    url = "https://www.twse.com.tw/zh/announcement/notice.html"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.to_string(index = True)]]
    NotifyBase(audience, "文", "\n".join(msg))


MopsYYYMMDD("0")
AnnouncementNoticeYYYYMMDD("0")
