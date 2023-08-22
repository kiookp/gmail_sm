import requests
import time

# 常量定义
MAX_ATTEMPTS = 12
RETRY_WAIT_TIME = 3
base_url = "http://www.firefox.fun/yhapi.ashx"
token = "******************"

# 账户信息接口的参数
my_info_params = {
    "act": "myInfo",
    "token": token
}

# 获取手机号接口的参数
get_phone_params = {
    "act": "getPhone",
    "token": token,
    "iid": "1002",
    "seq": 0,
    "country": "mys"    # mys: 马来西亚  zaf: 南非   eng: 英格兰
}

# 获取验证码接口的参数
get_code_params = {
    "act": "getPhoneCode",
    "token": token,
}

# 加黑手机号接口的参数
add_black_params = {
    "act": "addBlack",
    "token": token,
    "reason": "used"
}

def get_account_info():
    response = requests.get(base_url, params=my_info_params)
    result = response.text.split('|')
    status_code = result[0]

    if status_code == "1":
        balance = result[1]
        level = result[2]
        points = result[3]
        return balance, level, points
    else:
        error_code = result[1]
        print("获取账户信息失败。失败代号:", error_code)
        return None, None, None


def get_phone_number():
    response = requests.get(base_url, params=get_phone_params)
    result = response.text.split('|')
    status_code = result[0]

    if status_code == "1":
        phone_key = result[1]
        extract_time = result[2]
        country_area_code = result[4]
        location = result[5]
        phone_number = result[7]
        print("提取时间:", extract_time)
        print("国家区号: +" + country_area_code)
        print("手机号: +" + country_area_code + phone_number)

        # Copy phone number to clipboard
        phone_to_copy = "+" + country_area_code + phone_number

        print("手机号已复制到剪切板。")
        # phone_key 手机号id
        # phone_to_copy 手机号
        return phone_key, phone_to_copy
    else:
        error_code = result[1]
        print("获取手机号失败。失败代号:", error_code)
        return None


def get_verification_code(phone_key, max_attempts=MAX_ATTEMPTS, retry_wait_time=RETRY_WAIT_TIME):
    for attempt in range(max_attempts):
        get_code_params["pkey"] = phone_key
        response = requests.get(base_url, params=get_code_params)
        result = response.text.split('|')
        status_code = result[0]

        if status_code == "1":
            code = result[1]
            print("获取到验证码:", code)
            return code

        elif status_code == "-3":
            print(f"等待验证码，{retry_wait_time}秒后重新调用...")
            time.sleep(retry_wait_time)

        else:
            error_code = result[1]
            print("获取验证码失败。失败代号:", error_code)
            time.sleep(retry_wait_time)

    print(f"{max_attempts}次尝试后仍无法获取验证码。加黑手机号码。")
    add_black_params["pkey"] = phone_key
    response = requests.get(base_url, params=add_black_params)
    result = response.text.split('|')
    status_code = result[0]

    if status_code == "1":
        print("成功加黑手机号。")
    else:
        error_code = result[1]
        print("加黑手机号失败。失败代号:", error_code)

    print("无法获取验证码。")
    return None



def add_phone_to_blacklist(phone_key):
    if not phone_key:
        print("请先获取手机号。")
        return

    # 加黑手机号
    add_black_params["pkey"] = phone_key
    response = requests.get(base_url, params=add_black_params)
    result = response.text.split('|')
    status_code = result[0]

    if status_code == "1":
        print("成功加黑手机号。")
    else:
        error_code = result[1]
        print("加黑手机号失败。失败代号:", error_code)



