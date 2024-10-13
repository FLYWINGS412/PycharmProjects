import os
import sys
from appium import webdriver

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks'))
from tasks import watch_home_videos, watch_featured_live_stream, cancel_following

def setUp():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '7',
        'deviceName': 'xiaoyao',
        'udid': '127.0.0.1:21513',
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

def main():
    driver = setUp()
    try:
        while True:
            print("请选择要执行的任务:")
            print("1. 首页看视频")
            print("2. 看精选直播")
            print("3. 取消关注")
            choice = input("输入选项编号并按回车: ")
            if choice == '1':
                watch_home_videos(driver)
                break
            elif choice == '2':
                watch_featured_live_stream(driver)
                break
            elif choice == '3':
                cancel_following(driver)
                break
            else:
                print("无效选项，请重新选择")
    finally:
        tearDown(driver)

if __name__ == "__main__":
    main()
