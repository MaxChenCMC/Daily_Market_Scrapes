import requests, pandas as pd
from datetime import datetime, timedelta


def strike_range_code(mkt_type: str, weekth: str):
    # network找getQuoteDetail
    url = "https://mis.taifex.com.tw/futures/api/getQuoteDetail"
    payload = {"SymbolID":["TXF-S","TXFJ4-M","TXO-R"]}
    if (datetime.now() + timedelta(hours = 8)).hour >= 15:
        try:
            res = requests.post(url, json = payload).json()["RtData"]['QuoteList'][1]
            last_close = float(res['CLastPrice'])
            close_to_strike = int(last_close / 50) * 50
            stike_range = [(close_to_strike + i * 50) for i in range(-1,2)] # 暫時只取±1個履約價   更多就range(-2,3)或range(-3,4)
            stike_range_code = []
            for k in [(close_to_strike + i * 50) for i in range(-1,2)]:
                stike_range_code.append(f'{weekth}104;{k}C')
                stike_range_code.append(f'{weekth}104;{k}P')
            return stike_range_code
        except Exception as e:
            print(e)


def strike_range_df(src):
    mkt_tpye = "1"
    weekth = "TXO"
    month = "10"
    url =   "https://mis.taifex.com.tw/futures/api/getQuoteListOption"
    payload =  {"MarketType": mkt_tpye, "SymbolType":"O","KindID":"1","CID": weekth, "ExpireMonth": f"2024{month}","RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"}
    quote_table = requests.post(url, json = payload).json()["RtData"]['QuoteList']
    _temp = []
    for i in range(len(quote_table)):
        if quote_table[i]['DispEName'] in src:
            _temp.append([
                # 'time', 'strike', 'mid_price', 'spread'
                (datetime.now()+ timedelta(hours = 8)).strftime("%H:%M:%S"),
                quote_table[i]['DispEName'][-6:-1],
                (float(quote_table[i]['CBestAskPrice']) + float(quote_table[i]['CBestBidPrice'])) / 2,
                float(quote_table[i]['CBestAskPrice']) - float(quote_table[i]['CBestBidPrice']) 
            ])

    _df = pd.DataFrame(_temp, columns=['time', 'strike', 'mid_price', 'spread'])
    # _df['time'] = pd.to_datetime(_df['time'])
    _df['strike'] = _df['strike'].astype(str)
    _df['mid_price'] = pd.to_numeric(_df['mid_price'])
    _df['spread'] = pd.to_numeric(_df['spread'])
    # Group by 'time' and 'strike', then sum 'parity_sum' and 'spread_sum'
    grouped_df = _df.groupby(['time', 'strike']).agg({
        'mid_price': 'sum',
        'spread': 'sum'
    }).reset_index()

    return grouped_df.sort_values(['time', 'strike'])


arg = strike_range_df(strike_range_code("1", "TXO")).to_string(index = False)
token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
requests.post(url, headers = headers,  data={'message': "\n" + arg})
