from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '12',
    'deviceName': 'MI 10',
    'udid': '192.168.0.213:41901',
    'automationName': 'UiAutomator2',
    'browserName': 'Chrome',
    'chromedriverExecutable': 'C:/Users/63061/.wdm/drivers/chromedriver/win64/128.0.6613.137/chromedriver.exe',
    'noReset': True,
    'chromeOptions': {
        'args': ['--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36']
    }
}

# 启动 Appium 驱动
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 打开京东 m.jd.com 网站
driver.get('https://m.jd.com')

# 等待直到搜索框出现
try:
    # 获取上下文列表，并切换到 WebView 上下文
    contexts = driver.contexts
    print("Available contexts: ", contexts)
    driver.switch_to.context('CHROMIUM')

    # 使用 XPath 定位搜索框
    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="msKeyWord"]'))  # 使用 XPath 定位
    )
    search_box.click()

    # 输入搜索关键词并提交
    search_box.send_keys('手机')
    search_box.submit()

# 不再关闭浏览器
finally:
    print("测试完成，浏览器不会关闭")