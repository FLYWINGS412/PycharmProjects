import re
import os
import time
import uuid
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

# 全局变量
driver = None
device_name = 'huawei'

# 驱动参数
def create_driver():
    global driver
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '8',
        'deviceName': device_name,
        'udid': '8RYBB18404152438',
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

    driver = webdriver.Remote('http://localhost:4725/wd/hub', desired_caps)
    driver.wait = WebDriverWait(driver, 10)
    size = driver.get_window_size()
    driver.width = size['width']
    driver.height = size['height']
    driver.device_name = device_name
    return driver

# 执行任务
def execute_task(task_function, account, task_args=None):
    global driver
    try:
        print(f"账号 {account['phone']} 开始任务")

        if not driver:
            print("驱动无效，跳过任务")
            return False

        if not auth.auto_login(driver, account['phone'], account['password']):
            print(f"登录账号 {account['phone']} 错误，程序继续。")
            return False

        if task_args is not None:
            if not task_function(driver, account, *task_args):
                print(f"{account['phone']} 执行任务失败，程序继续。")
                return False
        else:
            if not task_function(driver, account):
                print(f"{account['phone']} 执行任务失败，程序继续。")
                return False

        if not auth.auto_logout(driver):
            print(f"退出登录账号 {account['phone']} 失败，程序继续。")
            return False

        return True
    except Exception as e:
        print(f"处理中发生异常: {type(e).__name__}, 信息: {str(e)}")
        return False
    finally:
        if driver:
            driver.close_app()
            driver.quit()
        print(f"账号 {account['phone']} 处理完成，应用已关闭，驱动会话已结束。")

# 循环任务
def perform_tasks(accounts, tasks_list, start_task_index=0, start_account_index=0, is_single_task=False):
    global driver, device_name
    while True:
        task_index, account_index = start_task_index, start_account_index
        while task_index < len(tasks_list):
            task_function = tasks_list[task_index]['function']
            task_name = tasks_list[task_index]['name']
            task_args = tasks_list[task_index].get('task_args')

            print(f"当前任务 {task_name} 开始账号索引为: {account_index + 1}")

            while account_index < len(accounts):
                account = accounts[account_index]

                # 检查好友互助奖励是否已经完成
                if task_function == tasks.mutual_assistance_reward and utils.has_completed_mutual_assistance_reward(account, device_name):
                    print(f"账号 {account['phone']} 已完成今日的 {task_name}，跳过此任务。")
                    account_index += 1
                    continue

                # 提前保存当前任务和账号索引
                auth.save_progress(device_name, task_index, account_index)

                # 创建驱动
                driver = create_driver()

                if execute_task(task_function, account, task_args):
                    account_index += 1

            # 如果是单任务，在最后一个账号执行完成任务后退出应用并停止代码运行
            if is_single_task and account_index >= len(accounts):
                print("单任务执行完成，程序退出。")
                return

            # 检查日期变化
            if task_function == tasks.collect_rewards:
                if utils.check_and_reset_system_date(device_name):
                    print("日期已更改，立即执行下一次任务循环。")
                # KEEP: else:
                #    print("日期未更改，任务循环暂停半小时。")
                #    time.sleep(1800)  # 暂停半小时

            # 重置账号索引，准备执行下一个任务
            account_index = 0
            task_index += 1

        # 重置任务和账号索引，准备新一轮循环
        start_task_index = 0
        start_account_index = 0

def main():
    global device_name
    # 初始化系统日期
    utils.initialize_system_date(device_name)

    # 帐号列表
    accounts = [
        {'name': 'WY', 'phone': '13883122290', 'password': '412412'},
        # {'name': 'WY', 'phone': '17782070003', 'password': '412412'},
        # {'name': 'WY', 'phone': '17788487195', 'password': '412412'},
        # {'name': 'WY', 'phone': '13308322330', 'password': '412412'},
        # {'name': 'WY', 'phone': '17330966207', 'password': '412412'},
        # {'name': 'WY', 'phone': '18908361223', 'password': '412412'},
        # {'name': 'WY', 'phone': '19122094023', 'password': '412412'},
        # {'name': 'WY', 'phone': '18996925404', 'password': '412412'},
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

    # 关注列表
    follow_list = ['323353', '123456', '789012']

    # 任务菜单
    tasks_list = [
        # KEEP: {'function': tasks.handle_home_page_video, 'name': '首页红包奖励'},
        {'function': tasks.mutual_assistance_reward, 'name': '激励视频奖励'},
        {'function': tasks.collect_rewards, 'name': '资产页广告奖励'},
        {'function': tasks.follow, 'name': '自动关注', 'task_args': [follow_list]},
        {'function': tasks.like, 'name': '自动点赞', 'task_args': [follow_list]},
        {'function': tasks.unfollow, 'name': '取消关注', 'task_args': [follow_list]}
    ]

    # 任务菜单
    menu_options = {
        '1': {'desc': '单任务', 'is_single_task': True},
        '2': {'desc': '循环任务', 'is_single_task': False},
        '3': {'desc': '自动关注', 'is_single_task': True, 'task_index': 3},
        '4': {'desc': '自动点赞', 'is_single_task': True, 'task_index': 4},
        '5': {'desc': '取消关注', 'is_single_task': True, 'task_index': 5}
    }

    print("请选择任务类型:")
    for key, option in menu_options.items():
        print(f"{key}. {option['desc']}")
    task_type = input("请输入任务类型序号: ")

    if task_type in ['1', '2']:
        # 只显示前两个任务，并且只包括未注释的任务
        available_tasks = [task for task in tasks_list[:2] if task.get('function')]
        print("请选择任务:")
        for index, task in enumerate(available_tasks):
            print(f"{index + 1}. {task['name']}")
        task_choice = input("请输入任务序号，或按回车键继续从上次的任务开始: ")
        if task_choice.isdigit():
            start_task_index = int(task_choice) - 1
            start_account_index = 0
        else:
            start_task_index, start_account_index = auth.get_progress(device_name)

        print("请选择帐号开始:")
        for index, account in enumerate(accounts):
            print(f"{index + 1}: {account['phone']}")
        user_input = input("请输入开始的账号序号，或按回车键继续从上次的账号开始: ")
        if user_input.isdigit():
            start_account_index = int(user_input) - 1

        perform_tasks(accounts, available_tasks, start_task_index, start_account_index, is_single_task=menu_options[task_type]['is_single_task'])

    elif task_type in ['3', '4', '5']:
        task_index = menu_options[task_type]['task_index']
        perform_tasks(accounts, [tasks_list[task_index]], 0, 0, is_single_task=menu_options[task_type]['is_single_task'])

if __name__ == "__main__":
    main()
