from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

from bases.base import Info
import time

info = Info()

# Appium服务器
server = 'http://localhost:4723/wd/hub'

# 远程设备信息
device = {
    "platformName": info.get_platform_name(),
    "platformVersion": info.get_platform_version(),
    "deviceName": info.get_device_name(),
    "unicodeKeyboard": True,
    "resetKeyboard": True
}

apk = r'E:\Develop\App\xs.apk'
package = info.get_package_name(apk)
activity = info.get_activity(apk)
# info.clear_app(package)

# 通过webdriver实例化对象，连接Appium和远程设备
driver = webdriver.Remote(server, device)

# driver.start_activity(package, activity)     # 启动app需要两个必要参数：app的包名和activity
# 手机滑屏
# size = driver.get_window_size()
# print(size)
# width = size['width']
# height = size['height']

        # AppiumBy.ANDROID_UIAUTOMATOR：通过java语言编写的jar包，使用时需变使用java的语法
        # new Uiselector().text()：
        # new UiSelector().className()：
        # new UiSelector().resourceId()：

        # driver.find_element(appiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().txt("申请独家号")').click()
        # driver.find_element(AppiumBy.ID,'io.manong.developerdaily:id/btn_primary').click()    #点击申请独家号
        # driver.swipe(start_x=int(height/2),start_y=int(height*0.9),end_x=int(height/2),end_y=int(height*0.1),duration=100)


# 使用图像识别点击按钮
close_button_image = 'path_to_close_button_image.png'
close_button = driver.find_element_by_image(close_button_image)
close_button.click()

