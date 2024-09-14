import time
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '12',
    'deviceName': 'MI 10',
    'udid': '192.168.0.213:41155',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    'noReset': True,  # 不重置应用
}

# 启动 Appium 驱动，不重新启动浏览器
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# # 打印页面源代码
# page_source = driver.page_source
# print(page_source)

# # 使用 XPath 通过文本定位“回到首页”按钮
# home_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@text="回到首页"]'))
# )
# home_button.click()  # 点击按钮
# print("成功点击回到首页按钮")
# time.sleep(10)
#
# # 使用 XPath 通过文本定位“获取任务”按钮
# home_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@text="获取任务"]'))
# )
# home_button.click()  # 点击按钮
# print("成功点击回到获取任务")
# time.sleep(10)

# # 等待并查找 text 为 '京东' 的 android.widget.Image 元素
# jd_image = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//android.widget.Image[@text="京东"]'))
# )
# jd_image.click()
# print("成功点击了'京东'的图片元素")
# time.sleep(10)

# # 使用 XPath 定位并获取文本内容
# element = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View[2]/android.widget.TextView[5]'))
# )
# element_text = element.text
# print(f"元素的文本内容: {element_text}")
# time.sleep(10)
#
# # 等待输入框出现并点击
# search_box = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View[1]/android.view.View[1]/android.view.View/android.view.View/android.view.View/android.view.View[2]/android.view.View/android.view.View/android.view.View/android.widget.EditText'))
# )
# search_box.click()
# search_box.send_keys(element_text)
# time.sleep(10)
#
# # 搜索
# search_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@text="搜索"]'))
# )
# search_button.click()  # 点击按钮
# print("表单已提交")
# time.sleep(10)
#
# # 点击第一个商品栏
# element_to_click = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[3]/android.view.View/android.view.View[1]'))
# )
# element_to_click.click()
# print("元素已点击")

# 前往店铺
shop_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@text="前往店铺"]'))
)
shop_button.click()
print("成功点击'前往店铺'按钮")
time.sleep(10)

# 商品1详情
product_1 = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View[2]/android.view.View[2]/android.widget.ListView/android.view.View[1]/android.view.View/android.widget.TextView[1]'))
)
product_1.click()
print("成功点击'商品 1'详情")
time.sleep(10)

# 商品1提交
product_1_submit = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[4]/android.view.View[2]/android.widget.ListView/android.view.View[1]/android.view.View/android.widget.TextView[2]'))
)
product_1_submit.click()
print("成功点击'商品 1'的提交按钮")
time.sleep(10)

# 提交确定
search_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@text="确定"]'))
)
search_button.click()  # 点击按钮
print("表单已提交")

# 刷新页面
loading_state_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'com.mmbox.xbrowser.pro:id/btn_loading_state'))
)
loading_state_button.click()
print("页面已刷新")


# # 检查商品 1 的文本是否为 '已完成'
# product_1_status = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[5]/android.view.View[2]/android.widget.ListView/android.view.View[1]/android.view.View[1]/android.widget.TextView[3]'))
# )
# product_1_text = product_1_status.text
# print(f"商品 1 的文本值为: {product_1_text}")
#
# if product_1_text == '已完成':
#     # 如果商品 1 的文本是 '已完成'，则检查商品 2 的文本
#     product_2_status = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[5]/android.view.View[2]/android.widget.ListView/android.view.View[2]/android.view.View[1]/android.widget.TextView[3]'))
#     )
#     product_2_text = product_2_status.text
#     print(f"商品 2 的文本值为: {product_2_text}")
#
#     if product_2_text == '已完成':
#         print("商品 1 和商品 2 都为 '已完成'")
#     else:
#         print("商品 2 不是 '已完成'")
# else:
#     print("商品 1 不是 '已完成'")

# # 使用 XPath 通过文本定位“任务完成”按钮
# task_done_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@text="任务完成"]'))
# )
# task_done_button.click()  # 点击按钮
# print("成功点击回到首页按钮")
#
# # 任务完成确定
# search_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@text="确定"]'))
# )
# search_button.click()  # 点击按钮
# print("表单已提交")
