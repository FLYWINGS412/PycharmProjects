import time
import random
from time import sleep
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def check_and_handle_popups(driver):
    """检查并循环处理弹窗直到没有更多弹窗出现"""
    time.sleep(1)
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
        except TimeoutException:
            print("未找到关闭弹窗元素，不执行关闭操作")
    except TimeoutException:
        print("未找到弹窗或等待关闭弹窗超时")

def main():
    desired_caps = {
        "platformName": "Android",
        "platformVersion": "9",
        "deviceName": "192.168.0.246:5555 device",
        "appPackage": "com.xiangshi.bjxsgc",
        "appActivity": "com.xiangshi.bjxsgc.activity.LauncherActivity",
        'settings[waitForIdleTimeout]': 100,
        'settings[waitForSelectorTimeout]': 100,
        'newCommandTimeout': 300,  # 设置新的命令超时时间为300秒
        "unicodeKeyboard": True,
        "resetKeyboard": True,
        "noReset": True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    wait = WebDriverWait(driver, 10)
    time.sleep(30)  # 等待APP完全加载

    # 等待页面完成加载
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
    )
    print("首次加载页面已完成")

    # 检查并处理可能出现的弹窗
    check_and_handle_popups(driver)

    # 获取设备的屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    # 视频观看循环
    while True:
        start_time = time.time()  # 记录循环开始时间

        while True:
            # 记录小循环开始时间
            start_time_inner = time.time()

            # 执行滑动操作
            start_x = random.randint(width // 3, width * 2 // 3)
            start_y = random.randint(height * 2 // 3, height * 4 // 5)
            end_x = random.randint(width // 3, width * 2 // 3)
            end_y = random.randint(height // 5, height // 3)
            duration = random.randint(200, 500)
            action = TouchAction(driver)
            action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
            print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

            # 检查并处理可能出现的弹窗
            check_and_handle_popups(driver)

            # 现在可以安全地读取进度条文本，因为所有弹窗处理已完成
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/progressbar"))
                )
                progressbar_text_initial = driver.find_element(By.ID, "com.xiangshi.bjxsgc:id/progressbar").text
                time.sleep(3)  # 短暂等待后再次读取以检查变化

                # 检查并处理可能出现的弹窗
                check_and_handle_popups(driver)

                # 第二次读取进度条文本
                progressbar_text_updated = driver.find_element(By.ID, "com.xiangshi.bjxsgc:id/progressbar").text

                # 判断进度条文本是否发生变化
                if progressbar_text_initial != progressbar_text_updated:
                    print("进度条已变化，退出小循环")

                    # 输出小循环用时
                    end_time_inner = time.time()
                    elapsed_time_inner = round(end_time_inner - start_time_inner, 2)
                    print(f"小循环用时: {elapsed_time_inner} seconds")

                    break
                else:
                    print("进度条未变化，继续小循环")
            except NoSuchElementException:
                print("未能找到进度条元素，可能页面还未完全加载或元素ID已更改。")

        # 等待页面完成加载
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
        )
        print("页面已正常加载")

        # sleep(random_sleep)  # 翻页后的随机等待时间
        random_sleep = random.randint(0, 15)
        print(f"等待 {random_sleep} 秒")
        time.sleep(random_sleep)

        # 检查并处理可能出现的弹窗
        check_and_handle_popups(driver)

        # 立即检查 layer_redbag 元素是否存在
        elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
        if elements:
            print("找到了元素，继续循环")

            # 输出循环用时
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print(f"用时: {elapsed_time} seconds")
        else:
            # 第一次未找到元素时，再次处理弹窗并重新检查
            print("未找到元素，再次检查弹窗")
            check_and_handle_popups(driver)
            elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")

            # 输出循环用时
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print(f"用时: {elapsed_time} seconds")
            if not elements:
                print("再次检查后仍未找到元素，退出循环")
                break

    driver.quit()

if __name__ == "__main__":
    main()
