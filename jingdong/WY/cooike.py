# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': 'test',
    'udid': 'emulator-5556',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    # 'unicodeKeyboard': False,
    # 'resetKeyboard': False,
    'noReset': True,  # 不重置应用
}

# 启动 Appium 驱动，不重新启动浏览器
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
