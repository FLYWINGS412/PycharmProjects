import time
import random
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction

# 驱动参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': 'kuaishou',
    'udid': '127.0.0.1:21503',
    # 'appPackage': 'com.xiangshi.bjxsgc',
    # 'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    'noReset': True
}

# 初始化WebDriver
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
driver.wait = WebDriverWait(driver, 10)
size = driver.get_window_size()
driver.width = size['width']
driver.height = size['height']

# 定义滑屏翻页函数
def swipe_to_scroll(driver):
    start_x = random.randint(driver.width * 4 // 10, driver.width * 5 // 10)
    start_y = random.randint(driver.height * 8 // 10, driver.height * 9 // 10)
    end_x = random.randint(driver.width * 5 // 10, driver.width * 6 // 10)
    end_y = random.randint(driver.height * 1 // 10, driver.height * 2 // 10)
    duration = random.randint(200, 500)
    action = TouchAction(driver)
    action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
    print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

# 无限循环执行滑屏操作
while True:
    # 在240到290秒之间随机选择时间执行滑屏操作
    next_swipe_time = random.randint(30, 115)
    print('下一次滑屏时间为：', next_swipe_time, '秒')
    start_time = time.time()  # 获取滑屏开始的时间
    next_check_time = start_time + 58  # 设置下一个检查时间

    while True:
        current_time = time.time()
        if current_time >= next_check_time:
            # print("Current Time:", time.ctime())  # 每58秒打印一次当前时间
            next_check_time = current_time + 58  # 更新下一个检查时间

        if current_time - start_time >= next_swipe_time:
            break  # 当总时间达到随机设定的滑屏时间时跳出循环

    swipe_to_scroll(driver)  # 滑动操作
