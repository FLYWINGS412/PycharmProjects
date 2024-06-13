import re
import os
import time
import random
import threading
import subprocess
from time import sleep
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from auth import auth
from tasks import tasks
from utils import utils
from popups import popups


# 保存当前任务和帐号进度
def save_progress(task_index, account_index):
    directory = os.path.join("record")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, "progress.txt")
    with open(file_path, "w") as file:
        file.write(f"{task_index},{account_index}")

# 获取当前任务和帐号进度
def get_progress():
    file_path = os.path.join("record", "progress.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.read().strip()
            if content:
                task_index, account_index = map(int, content.split(","))
                return task_index, account_index
    return 0, 0  # 如果文件不存在或内容为空，从第一个任务和第一个账号开始

# 帐号管理
def manage_accounts(driver, wait, width, height, accounts, current_account_index=0):
    total_accounts = len(accounts)

    while current_account_index < total_accounts:
        account = accounts[current_account_index]
        phone = account.get('phone')
        password = account.get('password')
        print(f"尝试登录账号: {phone}")

        # 调用登录函数
        if auto_login(driver, wait, width, height, phone, password):
            print(f"账号 {phone} 登录成功！")
            time.sleep(30)  # 保持登录状态一段时间，模拟用户操作
            if auto_logout(driver, wait, width, height):
                print(f"账号 {phone} 已成功登出。")
                current_account_index += 1
            else:
                print(f"账号 {phone} 登出失败。")
        else:
            print(f"账号 {phone} 登录失败。")
            current_account_index += 1
        print(f"继续尝试下一个账号，当前账号索引: {current_account_index}")

    return current_account_index

# 自动登陆
def auto_login(driver, wait, width, height, phone=None, password=None, accounts=None):
    if accounts:
        return manage_accounts(driver, wait, width, height, accounts)
    try:
        # 等待页面加载
        time.sleep(15)

        # 检查是否在启动页
        current_activity = utils.get_current_activity()
        expected_launcher_activity = "com.xiangshi.bjxsgc.activity.LauncherActivity"
        if expected_launcher_activity not in current_activity:
            print("未在启动页，可能已登录。等待30秒后尝试注销。")
            time.sleep(30)  # 等待一段时间，可能是因为应用刚启动需要时间加载
            if not auto_logout(driver, wait, width, height):
                print("注销尝试失败。")
            return False

        # 勾选协议
        login_check_button = wait.until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_login_check"))
        )
        time.sleep(random.randint(2, 5))
        login_check_button.click()
        print("勾选协议")
        time.sleep(random.randint(2, 5))

        # 点击同意
        confirm_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_confirm"))
        )
        confirm_button.click()
        print("点击同意")

    except TimeoutException as e:
        # print(f"超时异常：{str(e)}")
        print(f"超时异常")
        return False
    except Exception as e:
        # print(f"登录前半部分出现异常：{str(e)}")
        print(f"登录前半部分出现异常")
        return False

    try:
        # 等待页面加载
        time.sleep(30)

        # 检查是否在主界面
        current_activity = utils.get_current_activity()
        expected_main_activity = "com.xiangshi.main.activity.MainActivity"
        if expected_main_activity not in current_activity:
            print("未能加载到主界面，退出登录流程。")
            return False
        print("已加载主界面。")

        # 首页红包奖励
        popups.home_video_bonus(driver)

        # 点击头像
        confirm_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        confirm_button.click()
        print("点击头像")
        time.sleep(random.randint(2, 5))

        # 检查是否在登陆页
        current_activity = utils.get_current_activity()
        expected_login_activity = "com.xiangshi.main.activity.LoginActivity"
        if expected_login_activity not in current_activity:
            print("未能加载到登录页，退出登录流程。")
            return False
        print("已加载登录页。")

        # 输入电话号码
        phone_input = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/edit_phone"))
        )
        phone_input.send_keys(phone)
        print("输入电话号码")
        time.sleep(random.randint(2, 5))

        # 输入密码
        password_input = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/ed_pwd"))
        )
        password_input.send_keys(password)
        print("输入密码")
        time.sleep(random.randint(2, 5))

        # 勾选服务协议
        login_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_login_check"))
        )
        login_button.click()
        print("勾选服务协议")
        time.sleep(random.randint(2, 5))

        # 点击立即登录
        login_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_login"))
        )
        login_button.click()
        print("点击立即登录")
        time.sleep(random.randint(2, 5))

        # 视频红包奖励
        popups.home_video_bonus(driver)

        # 等待页面加载
        time.sleep(5)

        # 确认是否登录成功
        login_success_indicator = wait.until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_progress"))
        )
        if login_success_indicator:
            print("登录成功！")
            return True
        else:
            print("登录未成功。")
            return False

    except TimeoutException as e:
        # print(f"在登录过程中出现超时：{str(e)}")
        print(f"在登录过程中出现超时")
        return False
    except Exception as e:
        # print(f"登录过程中出现异常：{str(e)}")
        print(f"登录过程中出现异常")
        return False

# 自动退出
def auto_logout(driver, wait, width, height):
    try:
        # 等待页面加载
        time.sleep(5)

        # 获取当前活动并检查是否已经在主界面
        current_activity = utils.get_current_activity()
        expected_main_activity = "com.xiangshi.main.activity.MainActivity"
        print(f"当前页面为: {current_activity}")

        # 首页红包
        popups.home_video_bonus(driver)

        # 整点红包
        popups.hourly_bonus(driver, wait, width, height)

        # 如果不在主界面，则尝试返回到主界面
        if current_activity != expected_main_activity:
            print("不在主界面，尝试返回到主界面。")
            max_attempts = 5
            attempts = 0
            while current_activity != expected_main_activity and attempts < max_attempts:
                driver.press_keycode(AndroidKey.BACK)  # 发送物理返回键命令
                time.sleep(random.randint(2, 5))  # 等待2秒以观察效果
                current_activity = utils.get_current_activity()  # 再次获取当前活动
                attempts += 1
                print(f"尝试 {attempts}: 当前页面为 {current_activity}")
            if attempts == max_attempts:
                print("尝试返回主界面失败，请手动检查")
                return False
        else:
            print("已在主界面，无需返回。")

        # 个人页面
        my_tab = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='我的']")))
        my_tab.click()
        print("点击我的")
        time.sleep(random.randint(2, 5))

        # 更多菜单
        more_button = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_more_me")))
        more_button.click()
        print("点击更多菜单")
        time.sleep(random.randint(2, 5))

        # 滑动菜单并点击了个性设置
        while True:
            start_x = random.randint(width * 6 // 10, width * 9 // 10)
            start_y = random.randint(height * 8 // 10, height * 9 // 10)
            end_x = random.randint(width * 6 // 10, width * 9 // 10)
            end_y = random.randint(height * 1 // 10, height * 2 // 10)
            duration = random.randint(200, 500)
            action = TouchAction(driver)
            action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
            print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")
            time.sleep(random.randint(2, 5))

            try:
                settings = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='个性设置']")))
                settings.click()
                print("找到并点击了个性设置")
                time.sleep(random.randint(2, 5))
                break  # 成功找到，退出循环
            except TimeoutException:
                print("未找到个性设置，再次尝试滑动")

        # 检查是否在个性设置页
        current_activity = utils.get_current_activity()
        expected_setting_activity = "com.xiangshi.main.activity.SettingActivity"
        if expected_setting_activity not in current_activity:
            print("未能加载到个性设置，退出登出流程。")
            return False
        print("个性设置页。")

        # 退出登录
        logout_button = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='退出登录']")))
        logout_button.click()
        print("点击退出登录")
        time.sleep(random.randint(2, 5))

        # 继续退出
        continue_to_exit_button = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='继续退出']")))
        continue_to_exit_button.click()
        print("继续退出")
        time.sleep(random.randint(2, 5))

    except Exception as e:
        # print(f"处理注销时发生错误: {str(e)}")
        print(f"处理注销时发生错误")
        return False

    return True
