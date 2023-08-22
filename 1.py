import random
import string
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from api.ads_api import get_user_ids
from api.huohuli import get_phone_number, get_verification_code, add_phone_to_blacklist
from selenium.webdriver.support.ui import Select


SELECTORS = {
        "create_account": [
            "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-dgl2Hf ksBjEc lKxP2d LQeN7 FliLIb uRo0Xe TrZEUc Xf9GD']",
            "//*[@class='JnOM6e TrZEUc kTeh9 KXbQ4b']"
        ],
        'for_my_personal_use': [
            "//span[@class='VfPpkd-StrnGf-rymPhb-b9t22c']",
        ],
        "first_name": "//*[@name='firstName']",
        "last_name": "//*[@name='lastName']",
        "username": "//*[@name='Username']",
        "password": "//*[@name='Passwd']",
        "confirm_password": "//*[@name='PasswdAgain']",
        "next": [
            "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 qIypjc TrZEUc lw1w4b']",
            "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe P62QJc LQeN7 xYnMae TrZEUc lw1w4b']",
            "//button[contains(text(),'Next')]",
            "//*[@id='next']",
            "//button[contains(text(),'次へ')]",
            "//*[@class='VfPpkd-Jh9lGc']"
            "//button[contains(text(),'I agree')]",
            "//button[contains(text(),'Ich stimme zu')]",
            "//div[@class='VfPpkd-RLmnJb']"
        ],
        "recoveryNext": [
            "//*[@id='recoveryNext']",
            "//button[contains(text(),'Next')]"
        ],
        "Create_Gmail": [
            "//*[@id='selectionc2']",
            "//div[text()='Create your own Gmail address']",
            "//div[text()='Gmail-Adresse erstellen']",
            "//div[text()='自分で Gmail アドレスを作成']"
        ],
        "phone_number": "//*[@id='phoneNumberId']",
        "code": '//input[@name="code"]',
        "acc_phone_number": '//input[@id="phoneNumberId"]',
        "acc_day": '//input[@name="day"]',
        "acc_month": '//select[@id="month"]',
        "acc_year": '//input[@name="year"]',
        "acc_gender": '//select[@id="gender"]',
        "username_warning": '//*[@class="jibhHc"]',
        "recovery": "//*[@name='recovery']",
        "skip": [
            "//*[@id='view_container']/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/button/span",
            "//button[contains(text(),'Skip')]",
            "//button[contains(text(),'スキップ ')]",
            "//button[contains(text(),'Pomiń')]",
            "//button[contains(text(),'Пропустить')]",
            "//button[contains(text(),'Omite')]"
        ],
        "confirm": [
            "//button[contains(text(),'Confirm')]",
            "//span[@class='RveJvd snByac']"
        ],
    }

def generate_random_surname():
    url = "https://www.behindthename.com/random/random.php?number=1&gender=both&surname=&all=no&usage_eng=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    name_element = soup.find(class_="random-results").find("a")
    last_name = name_element.get_text().strip()
    return last_name



# 生成随机的名字
def generate_random_name():
    url = "https://www.behindthename.com/random/random.php?number=1&gender=both&surname=&all=no&usage_eng=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    name_element = soup.find(class_="random-results").find("a")
    first_name = name_element.get_text().strip()
    return first_name


WAIT = 10

def process_phone_verification(driver):

    phone_key, phone_to_copy = get_phone_number()
    if phone_key is not None:
        print("获取到手机号id:", phone_key)
        print("获取到手机号:", phone_to_copy)

    try:

        # 显性等待，等待电话号码输入框出现并可输入
        phone_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "phoneNumberId"))
        )
        #打印出电话号码
        print(phone_to_copy)
        # 检查输入框是否有内容，如果有则先清除内容
        if phone_input.get_attribute("value"):
            phone_input.clear()
        phone_input.send_keys(phone_to_copy)

        # 点击下一步按钮
        print('################ 点击下一步按钮 ################')
        for selector in SELECTORS['next']:
            try:
                next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
                next_button.click()
                break
            except:
                pass

        # 检查是否存在 aria-invalid="true" 属性（表示电话号码无效）
        try:
            invalid_element = WebDriverWait(driver, 9).until(
                EC.presence_of_element_located((By.XPATH, "//input[@aria-invalid='true']"))
            )
            # 如果带有 aria-invalid="true" 属性的元素存在，说明电话号码无效
            print("电话号码无效。将其添加到黑名单并重试...")
            add_phone_to_blacklist(phone_key)

            # 通过获取新的电话号码来重试流程
            phone_key, phone_to_copy = get_phone_number()
            process_phone_verification(driver)  # 递归调用以重试流程

        except Exception:
            # 如果不存在 aria-invalid="true" 属性，则继续检查是否存在 id="code" 属性
            try:
                verification_code_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "code"))
                )
                # 如果找到 id="code" 属性，则继续获取验证码
                print("电话号码有效。继续获取验证码。")
                time.sleep(5)  # 在获取验证码之前等待5秒
                verification_code = get_verification_code(phone_key)
                # 接下来执行脚本的其余部分...
                # 将验证码填入输入框
                verification_code_input.send_keys(verification_code)
                time.sleep(2)  # 等待1秒以确保验证码已填入输入框
                print('################ 点击下一步按钮 ################')
                for selector in SELECTORS['next']:
                    try:
                        next_button = WebDriverWait(driver, WAIT).until(
                            EC.element_to_be_clickable((By.XPATH, selector)))
                        next_button.click()
                        break
                    except:
                        pass

                # 在填写验证码后添加处理下一步的代码

            except Exception:
                # 如果既没有 aria-invalid="true" 属性，也没有 id="code" 属性，则处理错误情况
                print("发生意外错误。")
                # 在此处添加处理错误的代码

    finally:
        # 不要在这里退出 WebDriver；将其交给调用者处理
        pass


def open_browser(ads_id):
    open_url = f"http://local.adspower.net:50325/api/v1/browser/start?user_id={ads_id}"
    close_url = f"http://local.adspower.net:50325/api/v1/browser/stop?user_id={ads_id}"

    resp = requests.get(open_url).json()
    if resp["code"] != 0:
        print(resp["msg"])
        print("please check ads_id:", ads_id)
        return

    chrome_driver = resp["data"]["webdriver"]
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    driver = webdriver.Chrome(chrome_driver, options=chrome_options)
    driver.set_window_size(590, 900)
    print(driver.title)
    driver.get("https://www.baidu.com")
    password = "hTFX5pQrTxxKQv1vFVUH"
    print("设置密码为：" + password)
    driver.get('https://ipinfo.io/ip')
    # driver.get("https://ipleak.net")
    time.sleep(2)
    driver.get("https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp")

    print('################ 设置名 ################')
    first_name_tag = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, SELECTORS['first_name'])))
    first_name = generate_random_name()
    print(first_name)

    first_name_tag.send_keys(first_name)

    print('################ 设置姓 ################')
    last_name_tag = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, SELECTORS['last_name'])))

    last_name = generate_random_surname()
    last_name_tag.send_keys(last_name)

    print('################ 点击下一步按钮 ################')
    for selector in SELECTORS['next']:
        try:
            next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
            next_button.click()
            break
        except:
            pass

    print('################ 设置生日 ################')
    birthday = str(random.randint(1, 12)) + "/" + str(random.randint(1, 28)) + "/" + str(random.randint(1990, 2003))

    date_input = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, SELECTORS['acc_day'])))
    date_input.clear()
    date_input.send_keys(birthday.split('/')[1])

    month_select = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, SELECTORS['acc_month'])))
    month = Select(month_select)
    month.select_by_value(birthday.split('/')[0])

    year_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, SELECTORS['acc_year'])))
    year_input.clear()
    year_input.send_keys(birthday.split('/')[2])

    gender_select = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, SELECTORS['acc_gender'])))
    gender = Select(gender_select)
    gender.select_by_value('1')
    time.sleep(0.5)
    print('################ 点击下一步按钮 ################')
    for selector in SELECTORS['next']:
        try:
            next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
            next_button.click()
            break
        except:
            pass

    time.sleep(3)
    print('################ 选择gmail ################')
    gmail_ids = ["selectionc1", "selectionc0"]

    selected_id = random.choice(gmail_ids)
    selector = f'//*[@id="{selected_id}"]'

    try:
        Gmail_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
        Gmail_button.click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        email_div = soup.find('div', {'id': selected_id})
        email = email_div.text.strip()

        print(email)

    except:
        pass

    print('################ 点击下一步按钮 ################')
    for selector in SELECTORS['next']:
        try:
            next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
            next_button.click()
            break
        except:
            pass

    print('################ Set Password ################')
    password_tag = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, SELECTORS['password'])))
    password_tag.send_keys(password)
    time.sleep(0.5)

    print('################ Set Confirm Password ################')
    confirm_password_tag = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.XPATH, SELECTORS['confirm_password'])))
    confirm_password_tag.send_keys(password)
    time.sleep(0.5)

    print('################ 点击下一步按钮 ################')
    for selector in SELECTORS['next']:
        try:
            next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
            next_button.click()
            break
        except:
            pass
    time.sleep(3)
    print('################ Set Phone ################')
    process_phone_verification(driver)

    time.sleep(10)
    def generate_random_email():
        suffixes = ['@163.com', '@126.com', '@gmail.com', '@qq.com']
        random_suffix = random.choice(suffixes)

        random_length = random.randint(6, 13)
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=random_length))

        random_email = random_chars + random_suffix
        return random_email

    print('################ Set Recovery Email ################')
    recovery_email = generate_random_email()
    print(recovery_email)
    recovery_email_tag = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, SELECTORS['recovery'])))
    recovery_email_tag.send_keys(recovery_email)

    print('################ 点击绑定辅助邮箱下一步按钮 ################')
    for selector in SELECTORS['next']:
        try:
            next_button = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.XPATH, selector)))
            next_button.click()
            break
        except:
            pass

    time.sleep(2)
    # 等待元素出现id="phoneNumberId"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "phoneNumberId"))
    )
    print('################ 辅助电话出现 ################')

    time.sleep(1)
    # 等待所有的按钮出现并可点击
    buttons = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "VfPpkd-LgbsSe"))
    )

    # 检查按钮是否足够，防止出现数组越界的错误
    if len(buttons) < 2:
        raise Exception("找不到足够的按钮")

    # 等待第二个按钮可点击
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(buttons[1])
    )

    # 点击第二个按钮
    buttons[1].click()
    print('################ 当前账号信息 ################')
    account_info = f"{email}----{password}----{recovery_email}"
    print(account_info)

    with open("k.txt", "a") as file:
        file.write(account_info + "\n")
    # driver.quit()
    # requests.get(close_url)
    # print(f"Finished for ads_id: {ads_id}")


def main():
    profile_ids = get_user_ids(page_size=10)
    print("Profile IDs:", profile_ids)

    with ThreadPoolExecutor(max_workers=5) as executor:  # 设置最大线程数
        for profile_id in profile_ids:
            executor.submit(open_browser, profile_id)
            time.sleep(2)  # 等待1秒后再启动下一个线程

    print("All tasks finished!")


if __name__ == "__main__":
    main()
