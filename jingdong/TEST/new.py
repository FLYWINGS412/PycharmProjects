import re
import os
import sys
import time
import json
import portalocker
import tkinter as tk
import multiprocessing
from appium import webdriver
from datetime import datetime
from difflib import SequenceMatcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 配置参数
with open('config.json', 'r') as f:
    devices = json.load(f)

# 保存每个设备进程的字典
device_processes = {}

# 运行设备自动化任务
def run_device(device_index):
    desired_caps = devices[device_index]

    # 启动 Appium 驱动
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    # 示例逻辑代码：刷新页面
    def refresh_page(driver):
        try:
            loading_state_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'com.mmbox.xbrowser:id/btn_loading_state'))
            )
            loading_state_button.click()
            print(f"设备 {desired_caps['deviceName']} 页面已刷新")
        except Exception as e:
            print(f"设备 {desired_caps['deviceName']} 刷新页面失败: {str(e)}")

    try:
        # 模拟长时间运行的任务
        while True:
            refresh_page(driver)
            time.sleep(10)  # 假设每隔 10 秒刷新一次页面
    except KeyboardInterrupt:
        print(f"设备 {desired_caps['deviceName']} 任务被手动停止")
    finally:
        driver.quit()

# 菜单系统
def menu():
    while True:
        print("\n菜单选项：")
        print("1. 查询设备")
        print("2. 启动设备")
        print("3. 停止设备")
        print("4. 已运行设备")
        print("5. 退出程序")
        choice = input("请输入您的选择: ").strip()

        if choice == '1':
            # 查询所有可运行的设备
            print("\n所有可运行的设备：")
            for index, device in enumerate(devices, start=1):
                print(f"{index}. 设备名称: {device['deviceName']}, UDID: {device['udid']}")

        elif choice == '2':
            # 运行设备，用户输入编号来运行设备
            selected_index = input("请输入要运行的设备编号 (例如 1, 2, 3...): ").strip()
            if selected_index.isdigit() and 1 <= int(selected_index) <= len(devices):
                selected_index = int(selected_index) - 1
                if selected_index in device_processes:
                    print(f"设备 {devices[selected_index]['deviceName']} 已经在运行中。")
                else:
                    # 创建并启动设备进程
                    p = multiprocessing.Process(target=run_device, args=(selected_index,))
                    p.start()
                    device_processes[selected_index] = p
                    print(f"设备 {devices[selected_index]['deviceName']} 已启动。")
            else:
                print("输入无效，请输入有效的设备编号。")

        elif choice == '3':
            # 停止设备，用户输入编号来停止设备
            selected_index = input("请输入要停止的设备编号: ").strip()
            if selected_index.isdigit() and int(selected_index) - 1 in device_processes:
                selected_index = int(selected_index) - 1
                device_processes[selected_index].terminate()  # 终止设备进程
                device_processes[selected_index].join()  # 等待进程结束
                del device_processes[selected_index]
                print(f"设备 {devices[selected_index]['deviceName']} 已停止。")
            else:
                print("输入无效或设备未在运行，请输入有效的设备编号。")

        elif choice == '4':
            # 查询正在运行的设备
            if not device_processes:
                print("当前没有设备在运行。")
            else:
                print("当前正在运行的设备：")
                for index in device_processes.keys():
                    print(f"设备名称: {devices[index]['deviceName']}, UDID: {devices[index]['udid']}")

        elif choice == '5':
            # 退出程序，终止所有运行的设备
            print("退出程序。停止所有正在运行的设备。")
            for p in device_processes.values():
                p.terminate()
                p.join()
            sys.exit(0)

        else:
            print("无效选择，请输入有效的选项。")

# 启动菜单
if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    menu()
