import requests
import time

def read_proxy_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        proxies = [line.strip() for line in lines]
    return proxies

def create_account(proxy_host, proxy_port):
    url = "http://local.adspower.com:50325/api/v1/user/create"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "group_id": "0",
        "user_proxy_config": {
            "proxy_soft": "other",
            "proxy_type": "socks5",
            "proxy_host": proxy_host,
            "proxy_port": proxy_port
        },
        "fingerprint_config": {
            "automatic_timezone": "1",
            "language": ["en-US", "en"],
            "webgl": "3",
            "flash": "block",
            "webrtc": "disabled"
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data["code"] == 0:
            account_id = data["data"]["id"]
            return account_id
        else:
            return None
    else:
        return None

proxy_file_path = 'proxy.txt'
proxies = read_proxy_file(proxy_file_path)
num_accounts_to_generate = 3  # 设置生成账号的数量

for i, proxy_params in enumerate(proxies):
    if i >= num_accounts_to_generate:
        break

    proxy_params_list = proxy_params.split(':')
    if len(proxy_params_list) == 2:
        account_id = create_account(proxy_params_list[0], proxy_params_list[1])
        if account_id is None:
            print("账号添加失败")
        else:
            print("账号添加成功，账号ID为：{}".format(account_id))
            time.sleep(1)  # 等待1秒
    else:
        print("代理参数格式错误:", proxy_params)
