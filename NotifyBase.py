import requests

def NotifyBase(acct: str, msg: str, arg):
    '''
    08:30
    15:10
    16:30
    '''
    if acct == "0": token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'    # 台股數據通知中心
    elif acct == "1": token = "TVR9kcFsdDS0Si7YtusO4bl3gcgUUjKz248yXivtJ56"  # 個人開發😎先選【透過1 對1】
    elif acct == "2": token = "3WKXlzNj7DixgamCXtvdkX9GRsbZv5XvepjnlWWdeYz"  # 期交所測試階段先一對多
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + token}
    if msg == "圖":
        response = requests.post(url, headers = headers, data = {'message': "點圖放大"},  # message不得為空
                                 files = {'imageFile': open(arg, 'rb')})
    elif msg == "文":
        response = requests.post(url, headers = headers,
                                 data = {'message': arg})