from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def test_example(driver):
    # 等待应用启动
    driver.implicitly_wait(10)

    # 切换到WebView上下文（如果适用）
    for context in driver.contexts:
        if 'WEBVIEW' in context:
            driver.switch_to.context(context)
            break

    # 滚动视图查找元素并点击
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR,
                                            'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("去看看"))'))
        )
        element.click()

        # 断言（根据具体情况修改）
        assert "expected_value" in driver.page_source
    except Exception as e:
        print(f"Error: {e}")

def tearDown(driver):
    driver.quit()

if __name__ == "__main__":
    driver = setUp()
    try:
        test_example(driver)
    finally:
        tearDown(driver)
