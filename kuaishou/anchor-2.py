import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
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

def find_element_with_retry(driver, by, value, retries=3, wait_time=10):
    for i in range(retries):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            print(f"尝试查找元素失败，第 {i+1} 次重试...")
            time.sleep(2)  # 增加等待时间
    raise e  # 如果所有重试都失败，抛出异常

def watch_featured_live_stream(driver):
    # 切换到WebView上下文（如果适用）
    for context in driver.contexts:
        if 'WEBVIEW' in context:
            driver.switch_to.context(context)
            break

    loop_count = 0

    while True:
        start_time = time.time()
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

            # 检查是否有“看播中”元素
            try:
                follow_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("看播中")'))
                )
                pass
            except Exception as e:
                print("未找到'看播中'，返回任务页")
                check_and_return_to_home(driver)
                continue

            # 查找并点击'去关注'的TextView，如果找不到就按返回键并检查当前页面
            try:
                follow_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("去关注")'))
                )
                follow_element.click()
                print("点击了去关注")
            except Exception as e:
                print("未找到'去关注'按钮")
                driver.press_keycode(AndroidKey.BACK)

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
            end_time = time.time()
            loop_duration = end_time - start_time
            print(f"完成看直播: 第 {loop_count} 次，本次用时: {loop_duration:.2f} 秒")

        except Exception as e:
            print(f"Error: {e}")
            break

def cancel_following(driver):
    # 滚动到最上方
    driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                        'new UiScrollable(new UiSelector().scrollable(true)).scrollToBeginning(1)')
    print("滚动到最上方")

    # 检查并点击关注按钮
    following_button = find_element_with_retry(driver, By.ID, "com.kuaishou.nebula:id/following_layout")
    following_button.click()
    print("点击关注按钮")
    time.sleep(random.randint(2, 5))

    # 开始循环
    while True:
        try:
            # 检查并点击三点按钮
            more_button = find_element_with_retry(driver, By.ID, "com.kuaishou.nebula:id/more_btn")
            more_button.click()
            print("点击三点按钮")
            time.sleep(random.randint(1, 3))

            # 检查并点击取消关注按钮
            unfollow_button = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                                      'new UiSelector().resourceId("com.kuaishou.nebula:id/text").text("取消关注")')
            unfollow_button.click()
            print("点击取消关注按钮")
            time.sleep(random.randint(1, 3))

            # 检查并点击确定取消关注按钮
            confirm_button = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                                     'new UiSelector().resourceId("com.kuaishou.nebula:id/qlist_alert_dialog_item_text").text("取消关注")')
            confirm_button.click()
            print("点击确定取消关注按钮")
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print("未找到更多按钮，结束循环")
            break

    # 返回任务页
    check_and_return_to_home

def tearDown(driver):
    driver.quit()

def main():
    driver = setUp()
    try:
        while True:
            print("请选择要执行的任务:")
            print("1. 看精选直播")
            print("2. 取消关注")
            choice = input("输入选项编号并按回车: ")

            if choice == '1':
                watch_featured_live_stream(driver)
                break
            elif choice == '2':
                cancel_following(driver)
                break
            else:
                print("无效选项，请重新选择")

    finally:
        tearDown(driver)

if __name__ == "__main__":
    main()
