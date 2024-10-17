import requests, pandas as pd
from datetime import datetime, timedelta


def strike_range_code(DispEName: str, mkt_type: str, contract_id: str, ExpireMonth: str) -> pd.DataFrame:
    '''
    RegularSession與AfterHoursSession，取最新成交價的"Request URL"都一樣，payload也一樣，只差在MarketType是0或1
    先產±1個履約價的CP共6個CODE，
    A is 1, K is 11
    TXFK4-M, TXFK4-M
    '''
    try:
        _monthcode = 'K'
        res = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteDetail",
                            json = {"SymbolID":["TXF-S", f"TXF{_monthcode}4-M", "TXO-R"]}
                            ).json()["RtData"]['QuoteList'][1]
        QRTime = datetime.strptime(res["CTime"], '%H%M%S').strftime('%H:%M:%S')
        last_close = float(res['CLastPrice'])
        close_to_strike = int(last_close / 50) * 50
        stike_range_code = []
        for k in [(close_to_strike + i * 50) for i in range(-1,2)]:  # 暫時只取±1個履約價   更多就range(-2,3)或range(-3,4)
            stike_range_code.append(f'{DispEName + str(k)}C')
            stike_range_code.append(f'{DispEName + str(k)}P')
        # return stike_range_code
        
        quote_table = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteListOption", 
                                    json = {"MarketType": mkt_type,
                                            "CID": contract_id,
                                            "ExpireMonth": ExpireMonth, 
                                            "SymbolType":"O","KindID":"1","RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"},
                                    ).json()["RtData"]['QuoteList']
        # return quote_table
        

        _temp = []
        for i in range(len(quote_table)):
            if quote_table[i]['DispEName'] in stike_range_code:
                _temp.append([
                    # 欄名： 'time', 'strike', 'mid_price', 'spread'
                    QRTime,  # (datetime.now()+ timedelta(hours = 0)).strftime("%H:%M:%S"), 
                    quote_table[i]['DispEName'][-6:-1],
                    (float(quote_table[i]['CBestAskPrice']) + float(quote_table[i]['CBestBidPrice'])) / 2,
                    float(quote_table[i]['CBestAskPrice']) - float(quote_table[i]['CBestBidPrice'])
                ])

        _df = pd.DataFrame(_temp, columns=['time', 'strike', 'mid_price', 'spread'])
        _df['strike'] = _df['strike'].astype(str)
        _df['mid_price'] = pd.to_numeric(_df['mid_price'])
        _df['spread'] = pd.to_numeric(_df['spread'])
        grouped_df = _df.groupby(['time', 'strike']).agg({
            'mid_price': 'sum',
            'spread': 'sum'
        }).reset_index()
        
        return grouped_df.sort_values(['time', 'strike'])             

    except Exception as e:
        print(e)


arg = strike_range_code("TX4W4104;", "1", "TXO", "202410W4").to_string(index = False)
token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
requests.post(url, headers = headers,  data={'message': "\n" + arg})
