from appium import webdriver

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

def test_current_activity(driver):
    # 等待应用启动
    driver.implicitly_wait(10)

    # 获取当前页面名称
    current_activity = driver.current_activity
    print(f"当前页面: {current_activity}")

def tearDown(driver):
    driver.quit()

if __name__ == "__main__":
    driver = setUp()
    try:
        test_current_activity(driver)
    finally:
        tearDown(driver)
