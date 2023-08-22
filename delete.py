import time
from api.ads_api import check_account_status, close_account_browser, delete_user_accounts, get_user_ids


if __name__ == "__main__":
    profile_ids = get_user_ids()
    print("账号ID列表：", profile_ids)

    if profile_ids:
        for user_id in profile_ids:
            status = check_account_status(user_id)
            if status == "Active":
                close_account_browser(user_id)
                time.sleep(1)  # 关闭浏览器后等待1秒
            elif status == "Inactive":
                pass  # 账号已处于非活动状态，无需关闭浏览器
            else:
                print("未知的账号状态：", status)
                continue  # 跳过此账号，继续下一个

            delete_user_accounts([user_id])
