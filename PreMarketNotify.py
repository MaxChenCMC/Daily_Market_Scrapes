import requests, pandas as pd
import plotly.graph_objs as go
from NotifyBase import NotifyBase
font_family = "Arial, sans-serif, 微軟正黑體, Microsoft JhengHei, 黑體-简, SimHei"


def RankTradingVolTWD(audience: str):
    '''
    histock不同排行有對應網址很貼心、若要加回'價格▼'則read_html就要補且lambda也要補
    '''
    df = pd.read_html("https://histock.tw/stock/rank.aspx?m=13&d=1&p=all")[0][['代號▼','名稱▼','漲跌幅▼','振幅▼','成交值(億)▼']].head(15)
    df = df.replace("--", "+0.0%")
    df = df[df["代號▼"].apply(lambda x: len(x) == 4)]
    df["漲跌幅▼"] = df["漲跌幅▼"].apply(lambda x: float(x[:-1]))
    df["振幅▼"] = df["振幅▼"].apply(lambda x: float(x[:-1]))
    df["成交值(億)▼"] = df["成交值(億)▼"].apply(lambda x: int(x))
    df.columns = ["股號", "股名", "漲幅", "振幅", "成交值"]
    VolaPct, VolTWD = 7.0, 20.0
    res = df[(df["振幅"] > VolaPct) & (df["成交值"] > VolTWD)].head(10) # & (df["漲幅"] > chgPct) 

    title = "▌振幅>7%且成交值>20億的人氣股"
    url1 = "https://histock.tw/stock/rank.aspx?m=13&d=1&p=all"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url1, res.to_string(index = False, col_space = 8)]]
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
    fig.update_layout(title='▌成交值前15大的焦點股日K走勢強弱比較', yaxis_title = 'Change%', font=dict(family=font_family))
    #, plot_bgcolor = 'black', xaxis_title='Name', yaxis = dict(title='Price', tickformat='.2f')
    fig.write_image("RanksCandlestick.png")
    NotifyBase(audience, "圖", "RanksCandlestick.png")    


RankTradingVolTWD("1")
Candlestick("1")
