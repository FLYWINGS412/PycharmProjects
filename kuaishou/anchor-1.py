import time
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey

def setUp():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': 'kuaishou',
        'udid': '7d1f9eba',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True,
        'automationName': 'UiAutomator2'
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver

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
            time.sleep(1)  # 增加一点等待时间，确保页面有时间响应

def test_example(driver):
    # 切换到WebView上下文（如果适用）
    for context in driver.contexts:
        if 'WEBVIEW' in context:
            driver.switch_to.context(context)
            break

    loop_count = 0

    while True:
        try:
            # 尝试查找“去看看”按钮并点击
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR,
                                                'new UiSelector().text("去看看")'))
            )
            element.click()
            print("开始看直播")

            # 等待15秒
            time.sleep(15)

            # 查找并点击'去关注'的TextView，如果找不到就按返回键并检查当前页面
            try:
                follow_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("去关注")'))
                )
                follow_element.click()
                print("点击了去关注")
            except Exception as e:
                print("未找到'去关注'按钮，按返回键并检查当前页面")
                check_and_return_to_home(driver)
                continue  # 重新开始循环

            # 等待15分钟
            time.sleep(15 * 60)

            # 检查并点击'做任务'的TextView
            task_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("做任务")'))
            )
            if task_element:
                check_and_return_to_home(driver)

            # 增加循环次数
            loop_count += 1
            print(f"完成看直播: 第 {loop_count} 次")

        except Exception as e:
            print(f"Error: {e}")
            break  # 如果发生异常，跳出循环

def tearDown(driver):
    driver.quit()

if __name__ == "__main__":
    driver = setUp()
    try:
        test_example(driver)
    finally:
        tearDown(driver)
