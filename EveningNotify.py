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
from datetime import datetime, timedelta
import plotly.graph_objs as go
from NotifyBase import NotifyBase

def TwseT86YYYYMMDD(audience: str):
    '''
    # 16:30
    '''
    if datetime.now().weekday() == 5: YYYYMMDD = (datetime.now() - timedelta(days = 1)).strftime("%Y%m%d")
    elif datetime.now().weekday() == 6: YYYYMMDD = (datetime.now() - timedelta(days = 2)).strftime("%Y%m%d")
    else: YYYYMMDD = datetime.now().strftime("%Y%m%d")

    # strDate = datetime.now().strftime("%Y%m%d")
    res = requests.get(f'https://www.twse.com.tw/rwd/zh/fund/T86?date={YYYYMMDD}&selectType=ALL&response=json&_=1713107929300').json()
    df = pd.DataFrame.from_dict(res['data'])
    df.columns = res['fields']
    df = df[df['證券代號'].str.len() == 4][["證券名稱", "外陸資買賣超股數(不含外資自營商)", "投信買賣超股數", "三大法人買賣超股數"]]
    df.iloc[:,-3:] = df.iloc[:,-3:].apply(lambda x: x.str.replace(',', '').astype(float)).apply(lambda x: x / 1000).apply(lambda x: round(x, 0)).sort_values(by = '三大法人買賣超股數', ascending = False)
    df.columns = ["股票","外資","投信","法人買超"]
    df = df.head(10)

    title = "▌三大法人買賣超日報"
    url1 = "https://www.twse.com.tw/zh/trading/foreign/t86.html"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url1, df.to_string(index = False, col_space = 10)]]
    NotifyBase(audience, "文", "\n".join(msg))


def RankTradingVolTWD(audience: str):
    '''
    histock不同排行有對應網址很貼心
    '''
    df = pd.read_html("https://histock.tw/stock/rank.aspx?m=13&d=1&p=all")[0][['代號▼','名稱▼','價格▼','漲跌幅▼','振幅▼','成交值(億)▼']].head(20)
    df = df.replace("--", "+0.0%")
    df = df[df["代號▼"].apply(lambda x: len(x) == 4)]
    df["價格▼"] = df["價格▼"].apply(lambda x: float(x))
    df["漲跌幅▼"] = df["漲跌幅▼"].apply(lambda x: float(x[:-1]))
    df["振幅▼"] = df["振幅▼"].apply(lambda x: float(x[:-1]))
    df["成交值(億)▼"] = df["成交值(億)▼"].apply(lambda x: int(x))
    df.columns = ["股號", "股名", "股價", "漲幅", "振幅", "成交值"]
    chgPct, VolaPct, VolTWD = 4.0, 4.0, 8
    res = df[(df["漲幅"] > chgPct) & (df["振幅"] > VolaPct) & (df["成交值"] > VolTWD)]

    title = "▌漲幅>4%、振幅>4%、成交值>8億"
    url1 = "https://histock.tw/stock/rank.aspx?m=13&d=1&p=all"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url1, res.to_string(index = False, col_space = 5)]]
    NotifyBase(audience, "文", "\n\t".join(msg))
   

def Candlestick(audience: str):
    df = pd.read_html("https://histock.tw/stock/rank.aspx?m=13&d=1&p=all")[0][['代號▼']]
    df = df.replace("--", "+0.0%")
    df = df[df["代號▼"].apply(lambda x: len(x) == 4)].head(15)
    tickers = df["代號▼"].tolist()
    part_url = "|".join(["tse_" + ticker + ".tw" for ticker in tickers] + ["otc_" + ticker + ".tw" for ticker in tickers])
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch={part_url}"
    Datas = requests.get(url).json()["msgArray"]

    _temp = []
    for Data in range(len(Datas)):
        # ["股名"] 拼接 [開o→高h→底l→收z 減昨收y的幅度]
        Fields = [Datas[Data][Field] for Field in ["n","o","h","l","z","y"]]
        Fields_ = [Fields[0]] + [
            round(((float(x) - float(Fields[-1]))*100 / float(Fields[-1])), 2)
            for x in Fields[1:-1]]
        _temp.append(Fields_)
    df = pd.DataFrame(_temp, columns=["name", "open", "high", "low", "close"])
    fig = go.Figure(
        data = [go.Candlestick(x = df['name'],
                               open = df['open'], high = df['high'], low = df['low'], close = df['close'],
                               increasing_line_color = "red", decreasing_line_color = "green"
                               )
                ], layout = go.Layout(xaxis_rangeslider_visible = False))
    fig.update_layout(title='成交值前15大日K(漲跌幅%表示)', yaxis_title = 'Change%') #, plot_bgcolor = 'black', xaxis_title='Name', yaxis = dict(title='Price', tickformat='.2f')
    fig.write_image("RanksCandlestick.png")
    NotifyBase(audience, "圖", "RanksCandlestick.png")    

    
TwseT86YYYYMMDD("2")
RankTradingVolTWD("2")
Candlestick("2")
