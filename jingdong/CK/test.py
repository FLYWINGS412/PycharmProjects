import re
import os
import sys
import time
import portalocker
import tkinter as tk
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
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': 'CK-01',
    'udid': 'emulator-5616',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    'noReset': True,  # 不重置应用
}

# 启动 Appium 驱动
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 定位 dp-main 父容器
main_view = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
)
print("成功找到dp-main父容器")

# 在 dp-main 容器下查找第一行商品
try:
    first_item = WebDriverWait(main_view, 10).until(
        EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[1]'))
    )
    print("成功找到第一行商品")
except Exception as e:
    print("未找到第一行商品，继续尝试...")

while True:  # 无限循环，直到第一行商品完成
    time.sleep(5)
    # 在第一行商品下查找 "详情" 按钮并点击
    try:
        # 尝试查找包含 dp-good-detail 的按钮
        detail_button = WebDriverWait(first_item, 5).until(
            EC.presence_of_element_located((By.XPATH, './/android.view.View[contains(@resource-id, "dp-good-submit")]'))
        )
        detail_button.click()
        print("成功点击第一行商品的'提交'按钮")
    except Exception as e:
        print(f"未找到第一行商品的'提交'按钮")
        continue