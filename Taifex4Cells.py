import requests, os, csv, pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from NotifyBase import NotifyBase

def TotalTableDate(audience: str):
    '''
    '10 7 * * 1-5' 
    '''
    df = pd.read_html("https://www.taifex.com.tw/cht/3/totalTableDate", encoding="utf-8")[0]
    col1 = df[(         '交易口數與契約金額',                 '多方',   '口數')].tolist()
    col2 = df[(         '交易口數與契約金額',                 '空方',   '口數')].tolist()
    col3 = df[(         '交易口數與契約金額',               '多空淨額',   '口數')].tolist()
    pd.DataFrame([col1, col2, col3], columns=["","多方","空方","淨額"])
    df = pd.DataFrame([col1, col2, col3], columns = ["自營商", "投信", "外資", "合計"], index = ["多方","空方","淨額"]).T
    title = "▌期交所三大法人總表_交易口數"
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.to_string(index = True, col_space = 10)]]
    NotifyBase(audience, "文", "\n".join(msg))

    df = pd.read_html("https://www.taifex.com.tw/cht/3/totalTableDate", encoding="utf-8")[1]
    col1 = df[(        '未平倉口數與契約金額',                 '多方',   '口數')].tolist()
    col2 = df[(        '未平倉口數與契約金額',                 '空方',   '口數')].tolist()
    col3 = df[(        '未平倉口數與契約金額',               '多空淨額',   '口數')].tolist()
    pd.DataFrame([col1, col2, col3], columns=["","多方","空方","淨額"])
    df = pd.DataFrame([col1, col2, col3], columns = ["自營商", "投信", "外資", "合計"], index = ["多方","空方","淨額"]).T
    
    title = "▌期交所三大法人總表_未平倉口數"
    url = "https://www.taifex.com.tw/cht/3/totalTableDate"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.to_string(index = True, col_space = 10)]]
    NotifyBase(audience, "文", "\n".join(msg))


def largeTraderFutQry() -> list[int]:
    url = "https://www.taifex.com.tw/cht/3/largeTraderFutQry"
    '''
    # 寫法之一
    response: str = requests.post(url, data = {"queryType": 1})
    soup: str = BeautifulSoup(response.text, features = "html.parser")
    table = soup.find( "table", class_ = "table_f").find_all('tr')[5].find_all('td')
    NLargest5Buy = table[1].find_all('div')[0].get_text(strip = True).replace(",","")
    NLargest5Sell = table[5].find_all('div')[0].get_text(strip = True).replace(",","")
    return [int(re.findall(r'\d+', i)[0]) for i in [NLargest5Buy, NLargest5Sell]]
    '''    
    df: pd.DataFrame = pd.read_html(url, encoding= "utf-8")[0]
    res1 = df.loc[2,("買方","前五大交易人合計  (特定法人合計)","部位數")].replace(",","").split()[0]
    res2 = df.loc[2,("賣方","前五大交易人合計  (特定法人合計)","部位數")].replace(",","").split()[0]
    return [int(res1) , int(res2)]


def futContractsDate() -> list[int]:
    '''
    投信_未平倉餘額_多空淨額_口數、外資_未平倉餘額_多空淨額_口數
    '''
    url: str = "https://www.taifex.com.tw/cht/3/futContractsDate" 
    response: str = requests.post(url, data = {"queryType": 1})
    soup: str = BeautifulSoup(response.text, features = "html.parser")
    table = soup.find( "table", class_ = "table_f")
    TrustOI = table.find_all('tr')[4].find_all('td')[11].find_all('div')[0].get_text(strip = True).replace(",","")
    ForeignOI = table.find_all('tr')[5].find_all('td')[11].find_all('div')[0].get_text(strip = True).replace(",","")
    return [int(TrustOI), int(ForeignOI)]


def CrawlAndSaveCsv() -> None:
    csv_path = os.path.abspath("Taifex4Cells.csv")
    if os.path.exists(csv_path):
        existing_data = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                existing_data.append(row) 
        
        isRepeat = False
        for i in existing_data:
            if i[0] == datetime.now().strftime("%Y/%m/%d"):
                print("爬過了")
                
                isRepeat = True
                break
            
        if not isRepeat:
            CurrentData = [i for datas in [largeTraderFutQry(), futContractsDate()] for i in datas]
            CurrentData.insert(0, datetime.now().strftime("%Y/%m/%d"))
            existing_data.append(CurrentData)

        new_csv_path = csv_path
        with open(new_csv_path, 'w', newline='', encoding = 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(existing_data)
            print(f"正在寫入(覆寫){existing_data[-1]}")
    else:
        print("沒東西可沿用")


def Taifex4Cells(audience):
    if datetime.now().weekday() > 4:
        print("log:假日")
    else: 
        CrawlAndSaveCsv()  
    df = pd.read_csv("Taifex4Cells.csv")
    title = "▌五大交易人買賣、大台未平倉投信外資"
    url = "https://www.taifex.com.tw/cht/3/largeTraderFutQry" + "\n\n" + "https://www.taifex.com.tw/cht/3/futContractsDate"
    msg = ["\n" + title]
    [msg.append(i + "\n") for i in [url, df.iloc[-5:].to_string(index = False, col_space = 6)]]
    NotifyBase(audience, "文", "\n".join(msg))

TotalTableDate("0")
Taifex4Cells("0")
