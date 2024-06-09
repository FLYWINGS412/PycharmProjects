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
from new.auth import auth
from new.tasks import tasks
from new.utils import utils
from new.popups import popups

def main():
    accounts = [
        {'phone': '13883122290', 'password': '412412'},
        {'phone': '17782070003', 'password': '412412'},
        {'phone': '19122094023', 'password': '412412'},
        {'phone': '18996925404', 'password': '412412'},
        {'phone': '13308322330', 'password': '412412'},
        {'phone': '18908361223', 'password': '412412'},
        {'phone': '16623393179', 'password': '412412'},
        {'phone': '16623490422', 'password': '412412'},
    ]

    # 打印现有帐号列表
    print("现有帐号列表:")
    for index, account in enumerate(accounts):
        print(f"{index + 1}: {account['phone']}")

    current_index = auth.get_current_index()  # 获取当前账号索引
    print(f"当前开始账号索引为: {current_index + 1}")

    # 让用户选择从哪个账号开始，提供10秒倒计时
    user_input = input("请输入开始的账号序号，或按回车键继续从上次开始的账号: ")
    if user_input.isdigit():
        current_index = int(user_input) - 1  # 用户输入的是基于1的索引

    auth.save_current_index(current_index)  # 立即保存用户选择的索引，确保异常退出时可以从这里继续

    for i in range(current_index, len(accounts)):
        account = accounts[i]
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '12',
            'deviceName': 'localhost:7555 device',
            'appPackage': 'com.xiangshi.bjxsgc',
            'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
            'automationName': 'UiAutomator2',
            'settings[waitForIdleTimeout]': 10,
            'settings[waitForSelectorTimeout]': 10,
            'newCommandTimeout': 300,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'noReset': True
        }

        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        wait = WebDriverWait(driver, 10)

        # 获取设备的屏幕大小
        size = driver.get_window_size()
        width = size['width']
        height = size['height']

        try:
            # 自动登陆
            if not auth.auto_login(driver, wait, width, height, account['phone'], account['password']):
                print(f"登录账号 {account['phone']} 错误，程序继续。")
                continue

            # 自动退出
            if not auth.auto_logout(driver, wait, width, height):
                print(f"退出登录账号 {account['phone']} 失败，程序继续。")
                continue

        except Exception as e:
            print(f"处理中发生异常：{str(e)}")

        finally:
            driver.close_app()
            driver.quit()
            print(f"账号 {account['phone']} 处理完成，应用已关闭，驱动会话已结束。")

        # 更新索引并保存
        auth.save_current_index(i + 1)

    print("所有操作完成，准备退出应用。")
    return True

if __name__ == "__main__":
    if not main():
        print("多次操作失败，停止重试。")
    else:
        print("操作成功完成。")


        # # 首页视频
        # if not tasks.handle_home_page_video(driver, wait, width, height):
        #     print("首页滑屏错误，程序终止。")
        #     return False
        #
        # # 跳转资产页
        # time.sleep(random.randint(2, 5))
        # if not utils.navigate_to_assets_page(driver, wait, width, height):
        #     print("未能导航到资产页面，程序终止。")
        #     return False
        #
        # # 点击领取
        # time.sleep(random.randint(2, 5))
        # if not utils.is_on_assets_page(driver, wait, width, height) or not utils.click_to_collect(driver, wait, width, height):
        #     return False  # 不在资产页或领取气泡失败，重新尝试
        #
        # # 领取奖励
        # time.sleep(random.randint(2, 5))
        # if not utils.is_on_assets_page(driver, wait, width, height) or not utils.collect_rewards(driver, wait, width, height):
        #     return False  # 不在资产页或领取奖励失败，重新尝试