import re
import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 展示页
def handle_display_page(driver, wait, width, height):
    try:
        start_time = time.time()
        timeout = 70
        popup_texts = ["放弃", "离开"]
        handled_popup = False

        while time.time() - start_time < timeout:
            if not handled_popup:
                for text in popup_texts:
                    try:
                        xpath_expression = f"//*[contains(@text, '{text}')]"
                        popup_button = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((MobileBy.XPATH, xpath_expression))
                        )
                        time.sleep(random.randint(2, 5))
                        popup_button.click()
                        print(f"关闭了‘{text}’弹窗。")
                        handled_popup = True
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue
                    except StaleElementReferenceException:
                        print("遇到过时元素，正在重试。")
                        continue

            # 检查是否有返回按钮
            elements = driver.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
            if elements:
                for element in elements:
                    size = element.size
                    element_width = size['width']
                    element_height = size['height']
                    if element_width < 50 and element_height < 50:
                        start_x = random.randint(width // 3, width * 2 // 3)
                        start_y = random.randint(height * 2 // 3, height * 4 // 5)
                        end_x = random.randint(width // 3, width * 2 // 3)
                        end_y = random.randint(height // 5, height // 3)
                        duration = random.randint(200, 500)
                        action = TouchAction(driver)
                        action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
                        print(f"检查到返回按钮，Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")
                        break

            # 检查倒计时是否消失
            try:
                element_to_wait = None
                if not element_to_wait:
                    elements_with_text = driver.find_elements(MobileBy.XPATH, "//*[contains(@text, '后')]")
                    if elements_with_text:
                        element_to_wait = elements_with_text[0]

                if not element_to_wait:
                    elements_with_id = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")
                    if elements_with_id:
                        element_to_wait = elements_with_id[0]

                if not element_to_wait:
                    text_views = driver.find_elements(MobileBy.XPATH, "//android.widget.TextView[contains(@text, 's')]")
                    for text_view in text_views:
                        location = text_view.location
                        size = text_view.size
                        right_x = location['x'] + size['width']
                        top_y = location['y']
                        if right_x > width * 0.75 and top_y < height * 0.25 and text_view.is_displayed():
                            element_to_wait = text_view
                            break

                if element_to_wait and isinstance(element_to_wait, WebElement):
                    print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                    WebDriverWait(driver, 5).until(lambda driver: element_to_wait.text == '0 s')
                    print("倒计时结束。")
                    break
                else:
                    print("未找到或未能正确引用倒计时元素。")
            except TimeoutException:
                continue

        if not handled_popup:
            print("未找到任何弹窗。")

        # 调用点击元素函数
        if not retry_click_right_top_button(driver, wait, width, height):
            return False

    except Exception as e:
        print(f"处理展示页时发生错误: {str(e)}")
        return False

    return True

# 确保以下函数已被正确定义
def retry_click_right_top_button(driver, wait, width, height):
    # 函数定义内容...
    pass

if __name__ == "__main__":
    # 确保有适当的 main 函数或其他调用代码
    pass

# 获取元素
def find_right_top_button(driver, wait, width, height):
    attempts = 0
    min_distance = float('inf')
    right_top_button = None

    while attempts < 3 and not right_top_button:  # 尝试次数限制
        start_time = time.time()  # 记录查找开始时间

        # 等待并查找关闭按钮元素，优先查找ImageView
        elements = WebDriverWait(driver, 0).until(
            lambda d: d.find_elements(MobileBy.CLASS_NAME, "android.widget.ImageView") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '跳过')]") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '取消')]") +
                      d.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
                      # d.find_elements(MobileBy.CLASS_NAME, "android.widget.TextView")
        )

        for element in elements:
            try:
                # 先进行尺寸过滤，如果元素的宽度或高度大于等于50，则跳过该元素
                if element.size['width'] >= 50 and element.size['height'] >= 50:
                    continue

                # 计算元素右上角到屏幕右上角的距离
                x_right_top = element.location['x'] + element.size['width']
                y_right_top = element.location['y']

                # 过滤掉不在右上角范围内的元素
                # if x_right_top < width * 0.75 and y_right_top > height * 0.25:
                if y_right_top > height * 0.1:
                    continue

                # 优先检查元素是否可见和可点击，如果不可见或不可点击，则跳过该元素
                if not (element.is_displayed() and element.is_enabled()):
                    continue

                # 计算元素右上角到屏幕右上角的距离
                distance = ((width - x_right_top) ** 2 + y_right_top ** 2) ** 0.5

                # 如果距离更近，更新最小距离和右上角按钮
                if distance < min_distance:
                    min_distance = distance
                    right_top_button = element
            except StaleElementReferenceException:
                print("元素状态已改变，正在重新获取元素。")
                break  # 退出内部循环，将触发外部循环重新获取元素

        attempts += 1

        elapsed_time = round(time.time() - start_time, 2)
        print(f"本次查找用时: {elapsed_time} 秒")

    if right_top_button:
        print(f"找到最合适的右上角关闭按钮：类别-{right_top_button.get_attribute('className')}, 位置-{right_top_button.location}, 大小-{right_top_button.size}")
    else:
        print("未能找到合适的右上角关闭按钮。")

    return right_top_button

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'localhost:7555 device',
        # 'appPackage': 'com.xiangshi.bjxsgc',
        # 'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 300,  # 设置新的命令超时时间为300秒
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    wait = WebDriverWait(driver, 10)

    # 获取设备的屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    while True:
        start_time = time.time()  # 记录循环开始时间

        # 检查激励广告
        try:
            reward_layer = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_reward_ad"))
            )
            time.sleep(random.randint(2, 5))
            reward_layer.click()
            print("点击了激励广告")

            time.sleep(1)
            WebDriverWait(driver, 120).until(
                EC.invisibility_of_element_located((MobileBy.XPATH, "//*[contains(@text, '加载中')]"))
            )
            print("页面已正常加载")

            # 检查头像是否消失
            try:
                WebDriverWait(driver, 2).until(
                    EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
                )
                print("没检查到头像，加载展示页。")
                handle_display_page(driver, wait, width, height)
                # 检查是否存在包含“每日”文本的元素
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((MobileBy.XPATH, "//*[contains(@text, '每日20次')]"))
                    )
                    print("检测到'每日20次'文本，程序终止并退出到系统桌面。")
                    break
                except TimeoutException:
                    print("未检测到'每日20次'文本，继续执行。")
            except TimeoutException:
                print("检查到头像，继续执行滑动操作。")
        except Exception as e:
            print("未找到或不可点击激励广告。")

        # 执行滑动操作
        start_x = random.randint(width // 3, width * 2 // 3)
        start_y = random.randint(height * 2 // 3, height * 4 // 5)
        end_x = random.randint(width // 3, width * 2 // 3)
        end_y = random.randint(height // 5, height // 3)
        duration = random.randint(200, 500)
        action = TouchAction(driver)
        action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
        print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

        time.sleep(random.randint(2, 5))

        # 输出循环用时
        elapsed_time = round(time.time() - start_time, 2)
        print(f"用时: {elapsed_time} 秒")

    driver.quit()
    print("驱动已关闭，应用退出。")

if __name__ == "__main__":
    main()
