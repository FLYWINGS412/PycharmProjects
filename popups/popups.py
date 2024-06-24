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

# 首页视频红包奖励
def home_video_bonus(driver):
    found_and_handled = False  # 初始化标记，假定没有找到或处理弹窗
    try:
        # 直接尝试获取接收弹窗元素
        bg_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
        )
        time.sleep(random.randint(2, 5))  # 随机等待2-5秒
        bg_element.click()
        print("点击了接收弹窗")
        found_and_handled = True  # 更新标记为已找到并处理弹窗

        # 尝试获取并点击关闭弹窗，仅在元素存在时执行
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            close_element.click()
            print("点击了关闭弹窗")
            found_and_handled = True  # 确认找到并处理了关闭弹窗
        except TimeoutException:
            print("未找到关闭弹窗元素，不执行关闭操作")
    except TimeoutException:
        print("未找到弹窗或等待关闭弹窗超时")

    return found_and_handled

# 每日股东分红
def daily_dividend_distribution(driver):
    global wait, width, height  # 使用全局变量
    try:
        # 检查每日股东分红
        try:
            receive_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_watch_ad"))
            )
            time.sleep(random.randint(2, 5))
            receive_button.click()
            print("已领取每日股东分红。")

            # 处理展示页
            if not tasks.handle_display_page(driver):
                print("处理展示页时出错。")
                return False

            # 检查并点击整点红包
            try:
                hourly_bonus_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_the_hour"))
                )
                time.sleep(random.randint(2, 5))
                hourly_bonus_button.click()
                print("点击了整点红包图标。")

                # 整点红包奖励
                popups.hourly_bonus(driver)

            except TimeoutException:
                print("未找到整点红包图标，跳过此部分。")

        except TimeoutException:
            print("未找到每日股东分红，跳过此部分。")
            return  # 直接退出函数，不执行后续代码

    except Exception as e:
        print(f"处理活动时发生异常：{str(e)}")
        return False

    return True

# 整点红包
def hourly_bonus(driver):
    try:
        try:
            receive_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
            )
            print("找到整点红包")
            time.sleep(random.randint(2, 5))
            receive_button.click()
            print("已领取整点红包。")

            # 处理展示页
            if not tasks.handle_display_page(driver):
                print("处理展示页时出错。")
                return False

        except TimeoutException:
            print("未找到整点红包按钮，跳过此部分。")

    except Exception as e:
        print("处理活动时发生异常")
        return False

# 展示页弹窗
def display_page_popup(driver, popup_texts):
    handled_popup = False
    for text in popup_texts:
        try:
            xpath_expression = f"//*[contains(@text, '{text}')]"
            popup_button = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((MobileBy.XPATH, xpath_expression))
            )
            time.sleep(random.randint(2, 5))
            popup_button.click()
            print(f"关闭了‘{text}’弹窗。")
            handled_popup = True
            break
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            continue
    return handled_popup
