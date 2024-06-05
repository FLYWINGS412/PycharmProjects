import re
import time
import random
import subprocess
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey

def get_current_activity():
    try:
        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.check_output('adb shell dumpsys window windows', shell=True, text=True)

        # 在Python中搜索包含Activity信息的行
        for line in result.splitlines():
            if 'mCurrentFocus' in line or 'mFocusedApp' in line or 'mActivityRecord' in line:
                # 使用正则表达式从行中提取Activity名称
                match = re.search(r'([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)\b', line)
                if match:
                    full_activity_name = match.group(1) + match.group(2)
                    return full_activity_name
        return "无法获取当前页面"
    except subprocess.CalledProcessError as e:
        print(f"获取当前页面失败：{str(e)}")
        return None

def login(driver, wait, phone='13883122290', password='412412'):
    time.sleep(5)
    current_activity = get_current_activity()
    expected_activity = "com.xiangshi.bjxsgc.activity.LauncherActivity"
    if expected_activity not in current_activity:
        print("检查登陆页面失败，正在退出登录过程。")
        return False
    else:
        print("检查登陆页面正常。")

    try:
        # 勾选协议
        login_check_button = wait.until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_login_check"))
        )
        login_check_button.click()
        print("勾选协议")
        time.sleep(random.randint(2, 5))

        # 点击同意
        confirm_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_confirm"))
        )
        confirm_button.click()
        print("点击同意")
        time.sleep(30)

        # 点击头像
        confirm_button = wait.until(
            EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        confirm_button.click()
        print("点击头像")
        time.sleep(random.randint(2, 5))

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

        # 确认是否登录成功
        login_success_indicator = wait.until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_progress"))
        )

        if login_success_indicator:
            print("登录成功！")
            return True
        else:
            return False
    except TimeoutException as e:
        print(f"在登录过程中出现超时：{str(e)}")
        return False
    except Exception as e:
        print(f"其他错误：{str(e)}")
        return False

def logout(driver, wait, width, height):
    # 检查当前页面名
    # current_activity = get_current_activity()
    # if current_activity != "com.xiangshi.main.activity.MainActivity":
    #     print("当前不在主页面，尝试使用返回键回到主页面")
    #     # 初始化返回尝试计数器
    #     attempts = 0
    #     max_attempts = 5  # 最多尝试5次
    #     # 发送返回键命令尝试回到主页面
    #     while current_activity != "com.xiangshi.main.activity.MainActivity" and attempts < max_attempts:
    #         driver.press_keycode(AndroidKey.BACK)  # 发送物理返回键命令
    #         time.sleep(2)  # 增加等待时间到2秒，确保页面有足够的响应时间
    #         current_activity = get_current_activity()  # 更新当前页面名
    #         attempts += 1  # 更新尝试次数
    #         if current_activity == "com.xiangshi.main.activity.MainActivity":
    #             print("已成功回到主页面")
    #             break
    #         print(f"第 {attempts} 次尝试返回")
    #     if attempts == max_attempts:
    #         print("尝试返回主页面失败，请手动检查")
    # else:
    #     print("已在主页面")


    try:
        # 个人页面
        # 使用expected_conditions来等待元素可见并获取该元素
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
    except Exception as e:
        print(f"处理注销时发生错误: {str(e)}")
        return False

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

    return True

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        # 'deviceName': 'localhost:7555 device',
        'appPackage': 'com.xiangshi.bjxsgc',
        'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 300,  # 设置新的命令超时时间为300秒
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }

    # 连接到Appium服务器
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    wait = WebDriverWait(driver, 10)

    # 获取设备的屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    try:
        # 登陆操作
        if not login(driver, wait):
            print("登录错误，程序终止。")
            return False

        # 退出操作
        if not logout(driver, wait, width, height):
            print("退出登录失败，程序终止。")
            return False
    finally:
        # 关闭应用
        driver.close_app()
        print("应用已关闭")

        # 结束驱动会话，清理资源
        driver.quit()
        print("驱动会话已结束")

    return True

if __name__ == "__main__":
    while not main():
        print("操作失败，重新尝试。")
        time.sleep(10)  # 在重试前暂停10秒
