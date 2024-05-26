from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from pycparser.c_ast import ID
from selenium.webdriver.support.wait import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
import time

desired_caps = {
    "platformName": "Android",
    "platformVersion": "9",
    "deviceName": "192.168.0.34:5555 device",
    # "appPackage": "com.xiangshi.bjxsgc",
    # "appActivity": "com.xiangshi.bjxsgc.activity.LauncherActivity",
    "unicodeKeyboard": True,
    "resetKeyboard": True
}

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# -----输入和清空输入框内容-----------------------------------------------------------------------------------------------
# driver.find_element(MobileBy.ID,"com.xiangshi.bjxsgc:id/iv_close").click()
# time.sleep(5)
# input_label = driver.find_element(MobileBy.ID, "android:id/search_src_text")
# input_label.send_keys("hello")
# time.sleep(5)
# driver.find_element(MobileBy.ID,"android:id/search_src_text").clear()
# time.sleep(5)
# driver.find_element(MobileBy.ID,"android:id/search_src_text").send_keys("你好")

# -----获取元素文本的内容-------------------------------------------------------------------------------------------------
# time.sleep(3)
# eles = driver.find_elements(MobileBy.CLASS_NAME,"android.widget.ImageView")
# for i in eles:
#     print(i.text)

# -----获取元素的位置和大小------------------------------------------------------------------------------------------------
# time.sleep(3)
# search_button = driver.find_element(MobileBy.ID,"com.android.settings:id/search")
# print(search_button.location)
# print(search_button.location['x'])
# print(search_button.location['y'])
# print(search_button.size)
# print(search_button.size['width'])
# print(search_button.size['height'])

# -----获获取元素的属性值-------------------------------------------------------------------------------------------------
# eles = driver.find_elements(MobileBy.CLASS_NAME,"android.widget.ImageView")
# for i in eles:
#    print(i.get_attribute("enabled"))
#    print(i.get_attribute("text"))
#    print(i.get_attribute("resourceId"))
#    print(i.get_attribute("className"))
#    print(i.get_attribute("content-desc"))

# -----Swipe滑动事件----------------------------------------------------------------------------------------------------
# driver.swipe(100,2000,100,100,5000)

# -----Scroll & Drag_and_Drop------------------------------------------------------------------------------------------
# save_button = driver.find_element(MobileBy.XPATH, "//*[@text='存储']")
# more_button = driver.find_element(MobileBy.XPATH, "//*[@text='更多']")

# 使用 scroll 方法滚动到目标元素
# driver.scroll(save_button, more_button)

# 使用 Drag_and_Drop 方法滚动到目标元素
# driver.drag_and_drop(save_button,more_button)

# -----高级手势TouchAction----------------------------------------------------------------------------------------------
# 找到要点的元素
# wlan_button = driver.find_element(MobileBy.XPATH,"//*[@text='WLAN']")

# 轻敲
# TouchAction(driver).tap(wlan_button).perform()

# 按下和抬起
# TouchAction(driver).press(x=650, y=650).release().perform()

# 等待
# TouchAction(driver).tap(x=650,y=650).perform()
# time.sleep(2)
# TouchAction(driver).press(x=650,y=650).wait(2000).release().perform()

# 长按
# TouchAction(driver).tap(x=650,y=650).perform()
# time.sleep(2)
# TouchAction(driver).long_press(x=650,y=650,duration=2000).perform()

# 移动
# (TouchAction(driver).press(x=235,y=850).move_to(x=715,y=850).move_to(x=715,y=1330).move_to(x=715,y=1815)
#  .move_to(x=1200,y=1810).release().perform())

# -----获取手机分辨率----------------------------------------------------------------------------------------------------
# print(driver.get_window_size())
# print(driver.get_window_size()["width"])
# print(driver.get_window_size()["height"])

# -----获取截图---------------------------------------------------------------------------------------------------------
driver.get_screenshot_as_file("d:/screen.png")

# -----获取和设置手机网络-------------------------------------------------------------------------------------------------
# print(driver.network_connection)
# print(driver.set_network_connection(4))

# -----发送键到设备-----需求：(三次音量+) (返回) (两次音量-)-----------------------------------------------------------------
# driver.press_keycode(24)
# time.sleep(2)
# driver.press_keycode(24)
# time.sleep(2)
# driver.press_keycode(24)
# time.sleep(2)
# driver.press_keycode(4)
# time.sleep(2)
# driver.press_keycode(25)
# time.sleep(2)
# driver.press_keycode(25)

# -----操作手机通知栏----------------------------------------------------------------------------------------------------
# 打开通知栏
# driver.open_notifications()
# time.sleep(2)

# 关闭通知栏
# driver.press_keycode(4)


time.sleep(3)
driver.quit()
