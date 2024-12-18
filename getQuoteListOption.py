import requests, pandas as pd
from datetime import datetime, timedelta

arg1 = "TXFA5-M" # Network裡getQuoteDetail的paylaod第二個值(第三個值好像也要)
res = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteDetail", json={"SymbolID": [ "TXF-S", arg1, "TXO-R"]}).json()["RtData"]['QuoteList'][1]
last_close = float(res['CLastPrice'])
close_to_strike = int(last_close / 50) * 50

arg2 = "202412W4" # Network裡getQuoteListOption的paylaod的ExpireMonth
quote_table = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteListOption",
                            json = {"MarketType": "1", "CID": "TXO", "ExpireMonth": arg2, "SymbolType": "O", "KindID": "1", "RowSize": "全部", "PageNo": "", "SortColumn": "", "AscDesc": "A"},
                            ).json()["RtData"]['QuoteList']

QRTime = datetime.strptime(res["CTime"], '%H%M%S').strftime('%H:%M:%S')
data = [{QRTime : [item['DispEName'][9:15], (float(item['CBestAskPrice']) + float(item['CBestBidPrice'])) / 2, float(item['CBestAskPrice']) - float(item['CBestBidPrice'])]}
        for item in quote_table 
        if item['StrikePrice'] in [str(close_to_strike + i * 50) for i in range(-1,2)]]

formatted_message = " | ".join(
    f"{list(d.keys())[0]} {d[list(d.keys())[0]][0]}_成:{d[list(d.keys())[0]][1]}_差:{d[list(d.keys())[0]][2]}"
    for d in data
)

token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
requests.post(url, headers = headers,  data={'message': formatted_message})
