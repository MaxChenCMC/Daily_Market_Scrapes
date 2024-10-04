import requests, pandas as pd
from datetime import datetime, timedelta

DispEName_range_call = []
DispEName_range_put = []

def step1(mkt_type: str) -> pd.DataFrame:
    url = "https://mis.taifex.com.tw/futures/api/getQuoteDetail"
    payload, payload_all = dict(), dict()
    if mkt_type == "0":
        # ★這裡要週更
        payload = {"SymbolID":["TXF-S","TXFJ4-M","TXO-R"]}
        payload_all = {"MarketType":"0","SymbolType":"O","KindID":"1","CID":"TXO","ExpireMonth":"202410W2", "RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"}
    elif mkt_type == "1":
        # ★這裡要週更
        payload =  {"SymbolID":["TXF-S","TXFJ4-M","TXO-R"]}
        payload_all = {"MarketType":"1","SymbolType":"O","KindID":"1","CID":"TXO","ExpireMonth":"202410W2", "RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"}

    res = requests.post(url, json = payload).json()["RtData"]['QuoteList'][1]
    last_close = float(res['CLastPrice'])
    # print(last_close)
    close_to_strike = int(last_close / 50) * 50
    stike_range = [(close_to_strike + i * 50) for i in range(-2,3)] #range(-3,4)

    for i in stike_range:
        # ★這裡要週更 
        DispEName_range_call.append(f"TX2W2104;{i}C")
        DispEName_range_put.append( f"TX2W2104;{i}P")


    url = "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
    res = requests.post(url, json = payload_all).json()["RtData"]['QuoteList']
    test = []
    for i in range(len(res)):
        if res[i]['DispEName'] in DispEName_range_call:
            test.append([
                # res[i]['CTime'],
                res[i]['DispEName'][-6:],
                res[i]['CBestBidPrice'],
                res[i]['CLastPrice'],
                res[i]['CBestAskPrice']
            ])
        elif res[i]['DispEName'] in DispEName_range_put:
            test.append([
                # res[i]['CTime'],
                res[i]['DispEName'][-6:],
                res[i]['CBestBidPrice'],
                res[i]['CLastPrice'],
                res[i]['CBestAskPrice']
            ])
    # return res  "Time", 
    df = pd.DataFrame(test, columns = ["Stike", "Bid", "Close", "Ask"])
    df[["Bid", "Close", "Ask"]] = df[["Bid", "Close", "Ask"]].astype(float)

    ts = (datetime.now()+ timedelta(hours = 8)).strftime('%H:%M:%M')
    ret = [
        [df[['Close']][0:2].sum().values[0], df[['Ask']][0:2].sum().values[0] - df[['Bid']][0:2].sum().values[0]],
        [df[['Close']][2:4].sum().values[0], df[['Ask']][2:4].sum().values[0] - df[['Bid']][2:4].sum().values[0]],
        [df[['Close']][4:6].sum().values[0], df[['Ask']][2:3].sum().values[0] - df[['Bid']][4:6].sum().values[0]],
        [df[['Close']][6:8].sum().values[0], df[['Ask']][2:3].sum().values[0] - df[['Bid']][6:8].sum().values[0]],
        [df[['Close']][8:10].sum().values[0], df[['Ask']][2:3].sum().values[0] - df[['Bid']][8:10].sum().values[0]],
    ]
    return df #, pd.DataFrame(ret)

arg = step1("1").to_string(index = False)
token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
requests.post(url, headers = headers,  data={'message': "\n" + arg})
