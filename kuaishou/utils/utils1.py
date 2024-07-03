import os
import time
import random
import pytesseract
from PIL import Image
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey

def setUp():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': 'kuaishou',
        'udid': '7d1f9eba',
        'automationName': 'UiAutomator2',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True,
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver

def tearDown(driver):
    driver.quit()

# 返回任务页
def check_and_return_to_home(driver):
    while True:
        current_activity = driver.current_activity
        print(f"当前页面: {current_activity}")
        if current_activity == 'com.yxcorp.gifshow.HomeActivity':
            print("已回到任务页，重新开始循环")
            break
        else:
            print("未回到任务页，再次按返回键")
            driver.press_keycode(AndroidKey.BACK)
            time.sleep(2)  # 增加一点等待时间，确保页面有时间响应

# 查找元素
def find_element_with_retry(driver, by, value, retries=3, wait_time=10):
    for i in range(retries):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            # print(f"尝试查找元素失败，第 {i+1} 次重试...")
            pass
    raise e

# 切换到 WebView 上下文
def switch_to_webview_context(driver):
    available_contexts = driver.contexts
    for context in available_contexts:
        if "WEBVIEW" in context:
            driver.switch_to.context(context)
            print("切换到了WebView上下文")
            return True
    print("未找到WebView上下文")
    return False

# 滑屏翻页
def swipe_to_scroll(driver):
    window_size = driver.get_window_size()
    start_x = random.randint(window_size['width'] * 4 // 10, window_size['width'] * 5 // 10)
    start_y = random.randint(window_size['height'] * 8 // 10, window_size['height'] * 9 // 10)
    end_x = random.randint(window_size['width'] * 5 // 10, window_size['width'] * 6 // 10)
    end_y = random.randint(window_size['height'] * 1 // 10, window_size['height'] * 2 // 10)
    duration = random.randint(200, 500)
    action = TouchAction(driver)
    action.press(x=start_x, y=start_y).wait(ms=duration).move_to(x=end_x, y=end_y).release().perform()
    # print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

# 设置 Tesseract 可执行文件的路径
def get_progress_bar_value(driver):
    # # 设置 Tesseract 可执行文件的路径
    # pytesseract.pytesseract.tesseract_cmd = r"D:\Program\Tesseract-OCR\tesseract.exe"

    screenshot_dir = "screenshot"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    cropped_screenshot_path = os.path.join(screenshot_dir, "cropped_screenshot.png")

    driver.save_screenshot(screenshot_path)
    image = Image.open(screenshot_path)
    cropped_image = image.crop((894, 300, 1038, 444))  # 小米6
    cropped_image.save(cropped_screenshot_path)

    progress_value = pytesseract.image_to_string(cropped_image, config='--psm 6')
    print(f"进度条的值是: {progress_value.strip()}")
    return progress_value.strip()
