import subprocess
import time
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import subprocess

import re

def get_current_activity():
    try:
        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.check_output('adb shell dumpsys window windows', shell=True, text=True)

        # 在Python中搜索包含Activity信息的行
        for line in result.splitlines():
            if 'mCurrentFocus' in line or 'mFocusedApp' in line or 'mActivityRecord' in line:
                print("找到的行：", line)  # 打印找到的行，帮助诊断
                # 使用正则表达式从行中提取Activity名称
                match = re.search(r'(\S+)/(\S+)\s', line)
                if match:
                    activity_name = match.group(2).split('/')[0]  # 获取Activity名称
                    return activity_name
        return "无法获取当前活动"
    except subprocess.CalledProcessError as e:
        print(f"获取当前活动失败：{str(e)}")
        return None

def login(driver, phone='13883122290', password='412412'):
    # 获取当前页面名
    current_activity = get_current_activity()
    print("当前活动:", current_activity)

    # 登录逻辑
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "com.xiangshi.bjxsgc:id/btn_login_check"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "com.xiangshi.bjxsgc:id/btn_confirm"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "com.xiangshi.bjxsgc:id/edit_phone"))
        ).send_keys(phone)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "com.xiangshi.bjxsgc:id/ed_pwd"))
        ).send_keys(password)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "com.xiangshi.bjxsgc:id/btn_login"))
        ).click()
        print("登录成功！")
        return True
    except TimeoutException as e:
        print(f"在登录过程中出现超时：{str(e)}")
        return False

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'localhost:7555 device',
        'appPackage': 'com.xiangshi.bjxsgc',
        'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
        'appWaitDuration': 30000,
        'newCommandTimeout': 300,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }

    # 连接到Appium服务器
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    if not login(driver):
        print("登录错误，程序终止。")
        return False
    return True

if __name__ == "__main__":
    while not main():
        print("操作失败，重新尝试。")
        time.sleep(10)  # 在重试前暂停10秒
