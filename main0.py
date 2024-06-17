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

# 执行任务
def execute_task(driver, wait, width, height, task_function, account, task_args=None):
    try:
        print(f"账号 {account['phone']} 开始任务")

        # 自动登陆
        if not auth.auto_login(driver, wait, width, height, account['phone'], account['password']):
            print(f"登录账号 {account['phone']} 错误，程序继续。")
            return False

        # 执行任务
        if not task_function(driver, wait, width, height, account, task_args):
            print(f"{account['phone']} 执行任务失败，程序继续。")
            return False

        # 自动退出
        if not auth.auto_logout(driver, wait, width, height):
            print(f"退出登录账号 {account['phone']} 失败，程序继续。")
            return False

        return True

    except Exception as e:
        # print(f"处理中发生异常：{str(e)}")
        print(f"处理中发生异常")
        return False

    finally:
        driver.close_app()
        driver.quit()
        print(f"账号 {account['phone']} 处理完成，应用已关闭，驱动会话已结束。")

# 开始任务
def perform_tasks(accounts, tasks_list, start_task_index=0, start_account_index=0, is_single_task=False):
    while True:
        task_index, account_index = start_task_index, start_account_index
        while task_index < len(tasks_list):
            task_function = tasks_list[task_index]['function']
            task_name = tasks_list[task_index]['name']

            print(f"当前任务 {task_name} 开始账号索引为: {account_index + 1}")

            while account_index < len(accounts):
                account = accounts[account_index]

                # 检查好友互助奖励是否已经完成
                if task_function == tasks.mutual_assistance_reward and utils.has_completed_mutual_assistance_reward(account):
                    print(f"账号 {account['phone']} 已完成今日的 {task_name}，跳过此任务。")
                    account_index += 1
                    continue

                # 提前保存当前任务和账号索引
                auth.save_progress(task_index, account_index)

                desired_caps = {
                    'platformName': 'Android',
                    'platformVersion': '12',
                    'deviceName': 'localhost:7555 device',
                    # 'udid': 'localhost:7555',
                    'appPackage': 'com.xiangshi.bjxsgc',
                    'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
                    'automationName': 'UiAutomator2',
                    'settings[waitForIdleTimeout]': 10,
                    'settings[waitForSelectorTimeout]': 10,
                    'newCommandTimeout': 21600,
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

                if execute_task(driver, wait, width, height, task_function, account):
                    account_index += 1

            # 如果是单任务，在最后一个账号执行完成任务后退出应用并停止代码运行
            if is_single_task and account_index >= len(accounts):
                print("单任务执行完成，程序退出。")
                return

            # 检查日期变化
            if task_function == tasks.collect_rewards:
                if utils.check_and_reset_system_date():
                    print("日期已更改，立即执行下一次任务循环。")
                # else:
                #     print("日期未更改，任务循环暂停半小时。")
                #     time.sleep(1800)  # 暂停半小时

            # 重置账号索引，准备执行下一个任务
            account_index = 0
            task_index += 1

        # 重置任务和账号索引，准备新一轮循环
        start_task_index = 0
        start_account_index = 0

# 关注任务
def perform_follow_task(accounts, follow_list):
    for account in accounts:
        print(f"账号 {account['phone']} 开始关注任务")

        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '12',
            'deviceName': 'localhost:7555 device',
            # 'udid': 'localhost:7555',
            'appPackage': 'com.xiangshi.bjxsgc',
            'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
            'automationName': 'UiAutomator2',
            'settings[waitForIdleTimeout]': 10,
            'settings[waitForSelectorTimeout]': 10,
            'newCommandTimeout': 21600,
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

        if not execute_task(driver, wait, width, height, tasks.follow, account, follow_list):
            print(f"账号 {account['phone']} 执行关注任务失败，程序继续。")

def main():
    accounts = [
        # {'name': 'WY', 'phone': '13883122290', 'password': '412412'},
        # {'name': 'WY', 'phone': '17782070003', 'password': '412412'},
        {'name': 'WY', 'phone': '19122094023', 'password': '412412'},
        # {'name': 'WY', 'phone': '18996925404', 'password': '412412'},
        # {'name': 'WY', 'phone': '13308322330', 'password': '412412'},
        # {'name': 'WY', 'phone': '18908361223', 'password': '412412'},
        # {'name': 'WY', 'phone': '15523233363', 'password': '412412'},
        # {'name': 'WY', 'phone': '18580757722', 'password': '412412'},
        # {'name': 'WY', 'phone': '13752881027', 'password': '412412'},
        # {'name': 'WY', 'phone': '13508310332', 'password': '412412'},
        # {'name': 'WY', 'phone': '13594851384', 'password': '412412'},
        # {'name': 'TJ', 'phone': '16623393179', 'password': '412412'},
        # {'name': 'TJ', 'phone': '16623490422', 'password': '412412'},
        # {'name': 'TJ', 'phone': '13983801809', 'password': 'xxf851101'},
        # {'name': 'TJ', 'phone': '15683627751', 'password': 'xxf851101'}
    ]

    follow_list = ['323353', '123456', '789012']

    tasks_list = [
        # {'function': tasks.handle_home_page_video, 'name': '首页红包奖励'},
        {'function': tasks.mutual_assistance_reward, 'name': '激励视频奖励'},
        {'function': tasks.collect_rewards, 'name': '资产页广告奖励'},
        {'function': tasks.like, 'name': '自动点赞'}
    ]

    # 初始化系统日期
    utils.initialize_system_date()

    print("请选择任务类型:")
    print("1. 单任务")
    print("2. 循环任务")
    print("3. 自动关注")
    task_type = input("请输入任务类型序号: ")

    if task_type == '1':
        print("请选择任务:")
        for index, task in enumerate(tasks_list):
            print(f"{index + 1}. {task['name']}")
        task_choice = input("请输入任务序号，或按回车键继续从上次的任务开始: ")
        if task_choice.isdigit():
            start_task_index = int(task_choice) - 1
            start_account_index = 0
        else:
            start_task_index, start_account_index = auth.get_progress()

        print("请选择帐号开始:")
        for index, account in enumerate(accounts):
            print(f"{index + 1}: {account['phone']}")
        user_input = input("请输入开始的账号序号，或按回车键继续从上次的账号开始: ")
        if user_input.isdigit():
            start_account_index = int(user_input) - 1
        perform_tasks(accounts, tasks_list, start_task_index, start_account_index, is_single_task=True)

    elif task_type == '2':
        print("请选择任务:")
        for index, task in enumerate(tasks_list):
            print(f"{index + 1}. {task['name']}")
        task_choice = input("请输入任务序号，或按回车键继续从上次的任务开始: ")
        if task_choice.isdigit():
            start_task_index = int(task_choice) - 1
            start_account_index = 0
        else:
            start_task_index, start_account_index = auth.get_progress()

        print("请选择帐号开始:")
        for index, account in enumerate(accounts):
            print(f"{index + 1}: {account['phone']}")
        user_input = input("请输入开始的账号序号，或按回车键继续从上次的账号开始: ")
        if user_input.isdigit():
            start_account_index = int(user_input) - 1
        perform_tasks(accounts, tasks_list, start_task_index, start_account_index)

    elif task_type == '3':
        perform_follow_task(accounts, follow_list)

if __name__ == "__main__":
    main()
