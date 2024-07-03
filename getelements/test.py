from appium import webdriver

def setUp():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': 'kuaishou',
        # 'udid': '7d1f9eba',
        'udid': '127.0.0.1:21503',
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

def test_current_activity(driver):
    # 等待应用启动
    driver.implicitly_wait(10)

    # 获取当前页面名称
    current_activity = driver.current_activity
    print(f"当前页面: {current_activity}")

def get_device_resolution(driver):
    # 获取设备分辨率
    size = driver.get_window_size()
    width = size['width']
    height = size['height']
    print(f"设备分辨率: {width}x{height}")

def tearDown(driver):
    driver.quit()

def main_menu():
    print("请选择操作:")
    print("1. 获取当前页面名称")
    print("2. 获取设备分辨率")
    print("3. 退出")

if __name__ == "__main__":
    driver = setUp()
    try:
        while True:
            main_menu()
            choice = input("请输入选项: ")
            if choice == '1':
                test_current_activity(driver)
            elif choice == '2':
                get_device_resolution(driver)
            elif choice == '3':
                break
            else:
                print("无效的选项，请重新选择。")
    finally:
        tearDown(driver)
