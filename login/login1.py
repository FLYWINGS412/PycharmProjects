import re
import os
import time
import random
import threading
import subprocess
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey

# 获取当前页
def get_current_activity():
    try:
        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.run(["adb", "shell", "dumpsys", "window", "windows"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if 'mActivityRecord' in line or 'mCurrentFocus' in line:
                # print("原始行:", line)  # 输出原始行以供检查
                match = re.search(r'([^\s/]+)/([^\s/]+)', line)
                if match:
                    package_name = match.group(1)
                    activity_name = match.group(2)
                    if activity_name.startswith('.'):
                        activity_name = package_name + activity_name
                    full_activity_name = f"{activity_name}".replace('..', '.')
                    print("当前页面为:", full_activity_name)  # 在控制台输出获取到的当前页面
                    return full_activity_name
        print("未找到当前焦点的 Activity。")
        return "无法获取当前页面"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"

# 帐号管理
def manage_accounts(driver, wait, width, height, accounts, current_account_index=0):
    total_accounts = len(accounts)

    while current_account_index < total_accounts:
        account = accounts[current_account_index]
        phone = account.get('phone')
        password = account.get('password')
        print(f"尝试登录账号: {phone}")

        # 调用登录函数
        if login(driver, wait, width, height, phone, password):
            print(f"账号 {phone} 登录成功！")
            time.sleep(30)  # 保持登录状态一段时间，模拟用户操作
            if logout(driver, wait, width, height):
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
def login(driver, wait, width, height, phone=None, password=None, accounts=None):
    if accounts:
        return manage_accounts(driver, wait, width, height, accounts)
    try:
        # 等待页面加载
        time.sleep(15)

        # 检查是否在启动页
        current_activity = get_current_activity()
        expected_launcher_activity = "com.xiangshi.bjxsgc.activity.LauncherActivity"
        if expected_launcher_activity not in current_activity:
            print("未在启动页，可能已登录。等待30秒后尝试注销。")
            time.sleep(30)  # 等待一段时间，可能是因为应用刚启动需要时间加载
            if not logout(driver, wait, width, height):
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
        print(f"超时异常：{str(e)}")
        return False
    except Exception as e:
        print(f"登录前半部分出现异常：{str(e)}")
        return False

    try:
        # 等待页面加载
        time.sleep(30)

        # 检查是否在主界面
        current_activity = get_current_activity()
        expected_main_activity = "com.xiangshi.main.activity.MainActivity"
        if expected_main_activity not in current_activity:
            print("未能加载到主界面，退出登录流程。")
            return False
        print("已加载主界面。")

        # 点击头像
        confirm_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        confirm_button.click()
        print("点击头像")
        time.sleep(random.randint(2, 5))

        # 检查是否在登陆页
        current_activity = get_current_activity()
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
        print(f"在登录过程中出现超时：{str(e)}")
        return False
    except Exception as e:
        print(f"登录过程中出现异常：{str(e)}")
        return False

# 自动退出
def logout(driver, wait, width, height):
    try:
        # 等待页面加载
        time.sleep(5)

        # 获取当前活动并检查是否已经在主界面
        current_activity = get_current_activity()
        expected_main_activity = "com.xiangshi.main.activity.MainActivity"
        print(f"当前页面为: {current_activity}")

        # 如果不在主界面，则尝试返回到主界面
        if current_activity != expected_main_activity:
            print("不在主界面，尝试返回到主界面。")
            max_attempts = 5
            attempts = 0
            while current_activity != expected_main_activity and attempts < max_attempts:
                driver.press_keycode(AndroidKey.BACK)  # 发送物理返回键命令
                time.sleep(random.randint(2, 5))  # 等待2秒以观察效果
                current_activity = get_current_activity()  # 再次获取当前活动
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
        current_activity = get_current_activity()
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
        print(f"处理注销时发生错误: {str(e)}")
        return False

    return True

# 保存帐号进度
def save_current_index(index):
    with open("current_account_index.txt", "w") as file:
        file.write(str(index))

# 获取帐号进度
def get_current_index():
    if os.path.exists("current_account_index.txt"):
        with open("current_account_index.txt", "r") as file:
            content = file.read().strip()
            if content.isdigit():  # 确保内容是数字
                return int(content)
            else:
                return 0  # 如果文件不是数字，返回0
    return 0  # 如果文件不存在或内容为空，从第一个账号开始

def timed_input(prompt, timeout=10):
    print(prompt)
    timer = threading.Timer(timeout, lambda: print("\n输入时间已过，将自动从当前账号开始。"))
    timer.start()
    try:
        user_input = input()
        if user_input == '':
            print("没有输入，将自动从当前账号开始。")
        return user_input
    finally:
        timer.cancel()

def main():
    accounts = [
        {'phone': '13883122290', 'password': '412412'},
        {'phone': '17782070003', 'password': '412412'},
        {'phone': '19122094023', 'password': '412412'},
        {'phone': '18996925404', 'password': '412412'},
        {'phone': '13308322330', 'password': '412412'},
        {'phone': '18908361223', 'password': '412412'},
    ]

    # 打印现有帐号列表
    print("现有帐号列表:")
    for index, account in enumerate(accounts):
        print(f"{index + 1}: {account['phone']}")

    current_index = get_current_index()  # 获取当前账号索引
    print(f"当前开始账号索引为: {current_index + 1}")

    # 让用户选择从哪个账号开始，提供10秒倒计时
    user_input = timed_input("请输入开始的账号序号，或按回车键继续从上次开始的账号 (10秒内响应): ", 10)
    if user_input.isdigit():
        current_index = int(user_input) - 1  # 用户输入的是基于1的索引

    save_current_index(current_index)  # 立即保存用户选择的索引，确保异常退出时可以从这里继续

    for i in range(current_index, len(accounts)):
        account = accounts[i]
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '12',
            'deviceName': 'localhost:7555 device',
            'appPackage': 'com.xiangshi.bjxsgc',
            'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
            'settings[waitForIdleTimeout]': 10,
            'settings[waitForSelectorTimeout]': 10,
            'newCommandTimeout': 300,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'noReset': True
        }

        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        wait = WebDriverWait(driver, 10)

        try:
            if not login(driver, wait, driver.get_window_size()['width'], driver.get_window_size()['height'], account['phone'], account['password']):
                print(f"登录账号 {account['phone']} 错误，程序继续。")
                continue

            if not logout(driver, wait, driver.get_window_size()['width'], driver.get_window_size()['height']):
                print(f"退出登录账号 {account['phone']} 失败，程序继续。")
                continue

        except Exception as e:
            print(f"处理账号 {account['phone']} 时发生错误: {str(e)}")
            continue
        finally:
            driver.close_app()
            driver.quit()
            print(f"账号 {account['phone']} 处理完成，应用已关闭，驱动会话已结束。")

    return True

if __name__ == "__main__":
    if not main():
        print("多次操作失败，停止重试。")
    else:
        print("操作成功完成。")
