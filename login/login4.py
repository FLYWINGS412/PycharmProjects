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

# 获取当前页
def get_current_activity():
    try:
        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.check_output('adb shell dumpsys window windows', shell=True, text=True)

        # 在Python中搜索包含Activity信息的行
        for line in result.splitlines():
            if 'mCurrentFocus' in line or 'mFocusedApp' in line or 'mActivityRecord' in line:
                print("原始行:", line)  # 输出原始行以供检查
                # 使用正则表达式从行中提取Activity名称，仅提取活动名，排除包名
                match = re.search(r'[\w\.]+/([\w\.]+)', line)
                if match:
                    activity_name = match.group(1)
                    print("当前页面为:", activity_name)  # 在控制台输出获取到的当前页面
                    return activity_name
        print("未能获取当前页面信息。")
        return "无法获取当前页面"
    except subprocess.CalledProcessError as e:
        print(f"获取当前页面失败：{str(e)}")
        return None

# 自动登陆
def login(driver, wait, width, height, phone='13883122290', password='412412'):
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
                time.sleep(2)  # 等待2秒以观察效果
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

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'localhost:7555 device',
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
        if not login(driver, wait, width, height):
            print("登录错误，程序终止。")
            return False

        # 退出操作
        if not logout(driver, wait, width, height):
            print("退出登录失败，程序终止。")
            return False

    except Exception as e:
        print(f"处理时发生错误: {str(e)}")
        return False
    finally:
        # 关闭应用
        if 'driver' in locals():
            driver.close_app()
            print("应用已关闭")
            # 结束驱动会话，清理资源
            driver.quit()
            print("驱动会话已结束")

    return True

if __name__ == "__main__":
    retry_count = 0
    max_retries = 5  # 设置最大重试次数
    while not main():
        retry_count += 1
        if retry_count > max_retries:
            print("多次操作失败，停止重试。")
            break
        print("操作失败，重新尝试。")
        time.sleep(10)  # 在重试前暂停10秒
