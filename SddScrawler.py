import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO
from typing import List, Union
# Type aliases
NumberOrStr = Union[int, float, str]


def TwseTradingForeignBfi82u():
    """
    從台灣證券交易所抓取當日外資與投信的買賣超總額。

    Returns:
        List[Union[int, str]]: 包含外資與投信買賣差額的列表。
                               若抓取失敗，則返回 ["-", "-"]。
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        url = f"https://www.twse.com.tw/fund/BFI82U?response=csv&dayDate={today}&type=day"
        response = requests.get(url)
        response.raise_for_status()

        if not response:
            return ["-", "-"]
        df: pd.DataFrame = pd.read_csv(StringIO(requests.get(url).text), header = 1).dropna(how = 'all', axis = 1).dropna(how = 'any')
        
        # 提取外資和投信的數據
        foreign_trade = df[df['單位名稱'] == '外資及陸資(不含外資自營商)']['買賣差額'].iloc[0]
        trust_trade = df[df['單位名稱'] == '投信']['買賣差額'].iloc[0]

        # 清理並轉換為整數
        foreign_net = int(foreign_trade.replace(',', ''))
        trust_net = int(trust_trade.replace(',', ''))

        return [foreign_net, trust_net]
    except Exception as e:
        print(f"Error in TwseTradingForeignBfi82u: {e}")
        return ["-", "-"]


def futContractsDate():
    """
    從台灣期貨交易所抓取台指期與小台指的未平倉數據。

    Returns:
        List[Union[int, str]]: 包含大台指與小台指未平倉數據的列表。
                               若抓取失敗，則返回 ["-", "-", "-", "-"]。
    """
    try:
        url = "https://www.taifex.com.tw/cht/3/futContractsDate"
        response = requests.post(url, data={"queryType": 1})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='table_f')
        rows = table.find_all('tr')[3:]  # 從第四行開始是數據

        data = {"TXF": ["-", "-"], "MTX": ["-", "-"]}

        foreign_count = 0  # 計數器來追蹤"外資"出現次數
        txf_written = False  # 追蹤是否已經寫入TXF資料

        for row in rows:
            cols = row.find_all('td')
            contract = cols[0].text.strip()
            # display(cols[0])
            
            if "外資" in contract:
                foreign_count += 1
                # 第一次遇到"外資"且尚未寫入TXF資料時
                if not txf_written and foreign_count == 1:
                    net_oi = int(cols[5].text.strip().replace(',', ''))
                    total_oi = int(cols[11].text.strip().replace(',', ''))
                    data["TXF"] = [net_oi, total_oi]
                    txf_written = True  # 標記已經寫入TXF資料
                # 第4次遇到"外資"時
                elif foreign_count == 4:
                    net_oi = int(cols[5].text.strip().replace(',', ''))
                    total_oi = int(cols[11].text.strip().replace(',', ''))
                    data["MTX"] = [net_oi, total_oi]

        return data["TXF"] + data["MTX"]
    
    except Exception as e:
        print(f"Error in futContractsDate: {e}")
        return ["-", "-", "-", "-"]


def futDailyMarketReport_OHLCV() -> List[NumberOrStr]:
    '''Fetch futures daily market OHLCV data from TAIFEX

    Returns:
        List containing [open, high, low, close, volume]
    '''
    url = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    columns = ["開盤價", "最高價", "最低價", "最後 成交價", '*一般交易時段 成交量']

    try:
        df = pd.read_html(url, encoding="utf-8")[0]
        ohlcv = df.loc[0, columns].values.tolist()
        return [str(i) if i == "-" else int(i) for i in ohlcv]
    except Exception as e:
        print(f"Error fetching futures OHLCV: {e}")
        return ["-"] * 5


def TwseOHLCV() -> List[NumberOrStr]:
    '''Fetch TWSE index OHLCV data

    Returns:
        List containing [open, high, low, close, volume]
    '''
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_t00.tw"
    fields = ["o", "h", "l", "z", "v"]

    try:
        response = requests.get(url)
        data = response.json()["msgArray"][0]

        # Convert and adjust volume
        values = [float(data.get(field, "-")) for field in fields]
        values[-1] /= 100  # Adjust volume
        return values
    except Exception as e:
        print(f"Error fetching TWSE OHLCV: {e}")
        return ["-"] * 5


def TaifexPcRatio() -> List[NumberOrStr]:
    '''Fetch Put/Call ratio data from TAIFEX

    Returns:
        List containing [volume_ratio, OI_ratio]
    '''
    url = "https://www.taifex.com.tw/cht/3/pcRatio"
    columns = ["日期", "買賣權成交量比率%", "買賣權未平倉量比率%"]

    try:
        df = pd.read_html(url, encoding="utf-8")[0]
        ratios = df.iloc[0][columns].values[1:]
        return [float(ratio) for ratio in ratios]
    except Exception as e:
        print(f"Error fetching P/C ratio: {e}")
        return ["-", "-"]


def histock_2330() -> List[NumberOrStr]:
    '''Fetch TSMC (2330) institutional investor data

    Returns:
        List containing [foreign_net, total_net]
    '''
    url = "https://histock.tw/stock/chips.aspx?no=2330"
    columns = ["日期", "外資", "總計"]

    try:
        df = pd.read_html(url)[0][columns].head(1)
        values = df.iloc[0].values[-2:]
        return [int(val) for val in values]
    except Exception as e:
        print(f"Error fetching TSMC data: {e}")
        return ["-", "-"]


def get_all_market_data():
    """
    整合所有市場數據。

    Returns:
        List[Union[int, str]]: 包含所有市場數據的扁平化列表。
    """
    res = [datetime.now().strftime('%Y/%m/%d')] + TwseTradingForeignBfi82u() + futContractsDate() + futDailyMarketReport_OHLCV() + TwseOHLCV() + TaifexPcRatio() + histock_2330()
    csv_string = ",".join(str(item) for item in res)
    return csv_string


if __name__ == "__main__":
    market_data = get_all_market_data()
    print(market_data)
