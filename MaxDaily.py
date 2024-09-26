import requests, pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
import requests


def TwseTradingForeignBfi82u() -> list[int, int]:
    '''外資買賣超、投信買賣超'''
    UrlDataDate = datetime.now().strftime("%Y%m%d")
    url: str = "https://www.twse.com.tw/fund/BFI82U?response=csv&dayDate=" + UrlDataDate + "&type=day"
    try:
        df: pd.DataFrame = pd.read_csv(StringIO(requests.get(url).text), header = 1).dropna(how = 'all', axis = 1).dropna(how = 'any')
        return [int(df.loc[3, '買賣差額'].replace(',', '')), int(df.loc[2, '買賣差額'].replace(',', ''))]
    except Exception:
        return ["-","-"]


def futContractsDate() -> list[int, int, int, int]:
    '''大台淨多空、大台未平倉，小台淨多空、小台未平倉'''
    url: str = "https://www.taifex.com.tw/cht/3/futContractsDate"
    try:
        response: str = requests.post(url, data = {"queryType": 1})
        soup: str = BeautifulSoup(response.text, features = "html.parser")
        table = soup.find( "table", class_ = "table_f")
        TXFNet = table.find_all('tr')[5].find_all('td')[5].find_all('div')[0].get_text(strip = True).replace(",","")
        TXFOI = table.find_all('tr')[5].find_all('td')[11].find_all('div')[0].get_text(strip = True).replace(",","")
        MTXNet = table.find_all('tr')[14].find_all('td')[5].find_all('div')[0].get_text(strip = True).replace(",","")
        MTXOI = table.find_all('tr')[14].find_all('td')[11].find_all('div')[0].get_text(strip = True).replace(",","")
        return [int(i) for i in [TXFNet, TXFOI, MTXNet, MTXOI]]
    except Exception:
        return [ "-", "-", "-", "-"]   


def futDailyMarketReport_OHLCV() -> list[int, int, int, int, any]:
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    try:
        txf_ohlc = pd.read_html(url, encoding= "utf-8")[0]
        Ohlcv = txf_ohlc.loc[0,:][["開盤價","最高價","最低價","最後 成交價",'*一般交易時段 成交量']].values.tolist()
        Ohlcv_ = [str(i) if i == "-" else int(i) for i in Ohlcv ]
        return Ohlcv_
    except Exception:
        return [ "-", "-", "-", "-", "-"]   


def TwseOHLCV() -> list[float, float, float, float, float]:
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_t00.tw"
    try:
        src = requests.get(url).json()["msgArray"][0]
        tse_ohlcv = [float(src.get(i)) for i in ["o","h","l","z","v"]]
        tse_ohlcv[-1] /= 100
        return tse_ohlcv
    except Exception:
        return [ "-", "-", "-", "-", "-"]   


def TaifexPcRatio() -> list[float, float]:
    '''PutCallVolume, PutCallRatio'''
    url = "https://www.taifex.com.tw/cht/3/pcRatio"
    try:
        df = pd.read_html(url, encoding = "utf-8")[0].iloc[0][["日期",'買賣權成交量比率%',"買賣權未平倉量比率%"]]
        return [df.values[1], df.values[2]]
    except Exception:
        return [ "-", "-"]   


def histock_2330() -> list[int, int]:
    '''台積電外資買賣超、三大法人外資買賣超'''
    url = "https://histock.tw/stock/chips.aspx?no=2330"
    try:
        df = pd.read_html(url)[0][["日期","外資","總計"]].head(1)
        res = df.iloc[0,].values[-2:]
        return [int(_)for _ in res]
    except Exception:
        return [ "-", "-"]   


arg = TwseTradingForeignBfi82u()+futContractsDate()+futDailyMarketReport_OHLCV()+TwseOHLCV()+TaifexPcRatio()+histock_2330()
token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
response = requests.post(url, headers = headers,  data={'message': arg})