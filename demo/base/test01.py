from appium import webdriver

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

# 启动app
# app的包名和activity
    # 包名：app的唯一标识，用于识别app
    # activity：可以理解成opp的某个页面状态
    # *app包名确保指定的app；activity后动opp的指定状态/指定页面
# 如何获取 app的包名和activity
    # 第一种情况：手头上有app的安装包
        # 通过aopt进行解析获取
        # aapt：Android Asset Packoging Tools的缩写，可以使用该命令解析app信息
    # 第二种情况：手头上没有app的安装包，但是设备中已经安装
        # 可用先在移动设备中手动启动指定app，然后通过adb指令获取内存中的app信息

driver.start_activity(package, activity)     # 启动app需要两个必要参数：app的包名和activity
# 手机滑屏
size = driver.get_window_size()
# print(size)
width = size['width']
height = size['height']
# 一直从下至上滑屏，直到点击到xxx停止
while True:
    # 异常处理：当代码执行出现异常时的处理
    try:
        # 定位元素：通过appium服务器中的检索同步移动设备界面
        # appium中常用的元素定位方法
            # id、xpath：
                # id：元素的唯一标识。如果元素存在id优先使用id来定位
                # xpath：日标元素在xml文件中的层级关系
            # AppiumBy.ANDROID_UIAUTOMATOR：通过java语言编写的jar包，使用时需变使用java的语法
                # new Uiselector().text()：
                # new UiSelector().className()：
                # new UiSelector().resourceId()：
        driver.find_element(appiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().record("申请独家号")').click()


        # driver.find_element(AppiumBy.ID,'io.manong.developerdaily:id/btn_primary').click()    #点击申请独家号
        break
    except:
        driver.swipe(start_x=int(height/2),start_y=int(height*0.9),end_x=int(height/2),end_y=int(height*0.1),duration=100)
