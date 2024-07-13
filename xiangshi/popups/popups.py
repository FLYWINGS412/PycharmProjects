import re
import os
import time
import json
import random
import threading
import subprocess
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, CancelledError
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from auth import auth
from tasks import tasks
from utils import utils
from popups import popups

# 首页视频红包奖励
def home_video_bonus(driver):
    try:
        # 直接尝试获取接收弹窗元素
        bg_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
        )
        time.sleep(random.randint(2, 5))  # 随机等待2-5秒
        bg_element.click()
        print("点击了接收弹窗")

        # 尝试获取并点击关闭弹窗，仅在元素存在时执行
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            close_element.click()
            print("点击了关闭弹窗")
            return True
        except TimeoutException:
            print("未找到关闭弹窗")
            return False

    except TimeoutException:
        print("未找到弹窗")

    except Exception as e:
        print(f"处理活动时发生异常：{str(e)}")
        return False

    return True

# 每日股东分红
def daily_dividend_distribution(driver):
    try:
        receive_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_watch_ad"))
        )
        time.sleep(random.randint(2, 5))
        receive_button.click()
        print("已领取每日股东分红")

        # 处理展示页
        if not tasks.handle_display_page(driver):
            return False

        # 整点红包奖励
        if not popups.hourly_bonus(driver):
            return False

    except TimeoutException:
        print("未找到每日股东分红")

    except Exception as e:
        print(f"处理活动时发生异常：{str(e)}")
        return False

    return True

# 整点红包
def hourly_bonus(driver):
    # 直接尝试获取接收整点红包
    try:
        receive_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
        )
        time.sleep(random.randint(2, 5))
        receive_button.click()
        print("已领取整点红包")

        # 处理展示页
        if not tasks.handle_display_page(driver):
            return False

        # 尝试获取并点击关闭弹窗，仅在元素存在时执行
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(2, 5))
            close_element.click()
            print("点击了关闭弹窗")
            return True
        except TimeoutException:
            pass
            # print("未找到关闭弹窗")
            # return False

    except TimeoutException:
        print("未找到整点红包")

    except Exception as e:
        print(f"处理活动时发生异常：{str(e)}")
        return False

    return True

# 展示页弹窗
def display_page_popup(driver, popup_texts):
    handled_popup = False
    for text in popup_texts:
        try:
            xpath_expression = f"//*[contains(@text, '{text}')]"
            popup_button = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((MobileBy.XPATH, xpath_expression))
            )
            time.sleep(random.randint(1, 3))
            popup_button.click()
            print(f"关闭了‘{text}’弹窗。")
            handled_popup = True
            break
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            continue
    return handled_popup
