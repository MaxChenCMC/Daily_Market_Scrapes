import requests

def NotifyBase(acct: str, msg: str, arg):
    '''
    08:30
    15:10
    16:30
    '''
    # token = 'HkMGQ4rpNqCk5jOcIFFqRk2fvpVz8HEolq0RhNuAmbd'  # 扶
    token = 'Ww9Y7PSHCNkdmdGkxpdPT54vMGf0VaZBoMZH7BudlVS'  # 台股數據通知中心
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + token}
    if msg == "圖":
        response = requests.post(url, headers = headers, data = {'message': "點圖放大"},  # message不得為空
                                 files = {'imageFile': open(arg, 'rb')})
    elif msg == "文":
        response = requests.post(url, headers = headers,
                                 data = {'message': arg})
