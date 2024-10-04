import time
from appium import webdriver

# Appium 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': 'cookies',
    'udid': 'emulator-5638',
    'automationName': 'UiAutomator2',
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,
    'noReset': True,
    'browserName': 'Chrome',
    'chromeOptions': {
        'w3c': False
    },
    'autoGrantPermissions': True,  # 自动授权权限
    'chromedriverExecutable': 'E:/Develop/PycharmProjects/node_modules/.bin/chromedriver.exe'  # 确认路径正确
}

# 启动 Appium 驱动，启动 Chrome 浏览器
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 打开指定页面
driver.get('https://my.m.jd.com')

# 获取所有上下文并打印
contexts = driver.contexts
print(f"Available contexts: {contexts}")

# 切换到 Web 浏览器上下文
for context in contexts:
    if 'WEBVIEW' in context or 'CHROMIUM' in context:
        print(f"Switching to context: {context}")
        driver.switch_to.context(context)
        break

# 解析并导入 Cookies
def parse_cookies(raw_cookies):
    cookies = []
    for line in raw_cookies.strip().splitlines():
        cookie_dict = {}
        for item in line.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
        cookies.append(cookie_dict)
    return cookies

raw_cookies = """
pt_pin=7Nxno18Y293FNA1;pt_key=AAJm8m3OADA9vUQx9K3_g2tDDr46FhejLVuzNhxLCDHTnKfQ7ap3_k19-XT1NN1t9Dm-GLQe_Yc;
"""
cookies_list = parse_cookies(raw_cookies)

# 导入 Cookie 并验证
def import_cookie_and_verify(cookie):
    try:
        # 导入 Cookie
        for key, value in cookie.items():
            driver.add_cookie({'name': key, 'value': value})

        # 刷新页面查看是否登录成功
        driver.refresh()
        time.sleep(5)

        # 验证页面是否包含登录信息
        if "我的订单" in driver.page_source:
            print(f"Cookie 有效: {cookie}")
            return True
        else:
            print(f"Cookie 无效: {cookie}")
            return False
    except Exception as e:
        print(f"Error importing cookie: {e}")
        return False

# 批量验证 Cookies
for cookie in cookies_list:
    import_cookie_and_verify(cookie)

# 关闭驱动（在调试过程中可以暂时注释掉）
driver.quit()
