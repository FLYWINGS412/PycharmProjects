from appium import webdriver

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',  # 根据你的设备修改
        'deviceName': 'xiaomi',  # 根据你的设备修改
        'udid': '7d1f9eba',  # 根据你的设备修改
        'automationName': 'UiAutomator2',
        'noReset': True
    }
    # 连接到Appium Server
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    # 输出所有可用的上下文
    contexts = driver.contexts
    print(contexts)

    # 清理，关闭会话
    driver.quit()

if __name__ == '__main__':
    main()