from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time

desired_caps = dict()

# 手机参数
desired_caps['platformName'] = 'Android'
desired_caps['platformVersion'] = '12'
desired_caps['deviceName'] = '192.168.0.34:5555 device'

# 应用参数
# desired_caps['appPackage'] = 'com.android.settings'
# desired_caps['appActivity'] = '.Settings'

# 获取driver
driver = webdriver.Remote('http://localhost:4723/wd/hub',desired_caps)

# 跳转到短信
# driver.start_activity('com.android.mms','ui.ConversationList')

# 输出当前程序的包名
# print(driver.current_package)

# 输出当前程序的界面名
print(driver.current_activity)

# 关闭应用
# driver.close_app()

# 判断安智市场是否已经安装
# if driver.is_app_installed("cn.goapk.market"):
#     # 如果安装，就要卸载
#     driver.remove_app("cn.goapk.market")
#     # 如果没有安装就要安装
# else:
#     driver.install_app("/Users/Yoson/Desktop/anzhishichang.apk")

# 模拟Home键，将应用旋转后台5秒，再回到前台
# driver.background_app(5)

# 等待3秒
time.sleep(5)

# 退出driver

driver.quit()