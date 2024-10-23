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
        # change per week contract
        if mkt_type == "0":
            arg1, arg2, arg3 = 'K', "F", "Q"
        elif mkt_type == "1":
            arg1, arg2, arg3 = 'K', "M", "R"
            
        res = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteDetail",
                            json = {"SymbolID": ["TXF-S", f"TXF{arg1}4-{arg2}", f"TXO-{arg3}"]}
                            ).json()["RtData"]['QuoteList'][1]
        QRTime = datetime.strptime(res["CTime"], '%H%M%S').strftime('%H:%M:%S')
        last_close = float(res['CLastPrice'])
        # 還要補抓漲跌跟日期
        # last_change = float(res['漲跌'])
        # daydate = float(res['日期印象中沒有'])
        close_to_strike = int(last_close / 50) * 50
        stike_range_code = []
        for k in [(close_to_strike + i * 50) for i in range(-1,2)]:
            stike_range_code.append(f'{DispEName + str(k)}C')
            stike_range_code.append(f'{DispEName + str(k)}P')
        
        quote_table = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteListOption", 
                                    json = {"MarketType": mkt_type,
                                            "CID": contract_id,
                                            "ExpireMonth": ExpireMonth, 
                                            "SymbolType":"O","KindID":"1","RowSize":"全部","PageNo":"","SortColumn":"","AscDesc":"A"},
                                    ).json()["RtData"]['QuoteList']
        
        _temp = []
        for i in range(len(quote_table)):
            if quote_table[i]['DispEName'] in stike_range_code:
                _temp.append([
                    QRTime,
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


arg = strike_range_code("TX5W5104;", "1", "TXO", "202410W5").to_string(index = False)
token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'
url = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': 'Bearer ' + token} 
requests.post(url, headers = headers,  data={'message': "\n" + arg})
