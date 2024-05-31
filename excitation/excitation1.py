import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 展示页
def handle_display_page(driver, wait, width, height):
    try:
        start_time = time.time()
        timeout = 120
        popup_texts = ["放弃福利", "残忍离开", "放弃奖励离开"]
        handled_popup = False

        while time.time() - start_time < timeout:
            if not handled_popup:
                for text in popup_texts:
                    try:
                        xpath_expression = f"//*[contains(@text, '{text}')]"
                        popup_button = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((MobileBy.XPATH, xpath_expression))
                        )
                        time.sleep(random.randint(2, 5))
                        popup_button.click()
                        print(f"关闭了‘{text}’弹窗。")
                        time.sleep(1)  # 点击后等待页面可能的自动刷新
                        handled_popup = True
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue
                    except StaleElementReferenceException:
                        print("遇到过时元素，正在重试。")
                        continue  # 在重试之前可能需要添加一些逻辑来重新获取元素

            # 检查是否有返回按钮
            elements = driver.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
            if not elements:
                continue

            for element in elements:
                size = element.size
                element_width = size['width']
                element_height = size['height']

                if element_width < 100 and element_height < 100:
                    start_x = random.randint(width // 3, width * 2 // 3)
                    start_y = random.randint(height * 2 // 3, height * 4 // 5)
                    end_x = random.randint(width // 3, width * 2 // 3)
                    end_y = random.randint(height // 5, height // 3)
                    duration = random.randint(200, 500)
                    action = TouchAction(driver)
                    action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
                    print(f"检查到返回按钮，Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")
                    break

            try:
                element_to_wait = None

                if driver.find_elements(MobileBy.XPATH, "//*[contains(@text, '后')]"):
                    element_to_wait = (MobileBy.XPATH, "//*[contains(@text, '后')]")
                elif driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id"):
                    element_to_wait = (MobileBy.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")

                if element_to_wait:
                    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located(element_to_wait))
                print("倒计时结束。")
                break
            except TimeoutException:
                continue

        if not handled_popup:
            print("未找到任何弹窗。")

        # 调用点击元素函数
        if not retry_click_right_top_button(driver, wait):
            return False

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
        return False
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))
        return False
    return True

# 点击元素
def retry_click_right_top_button(driver, wait):
    attempts = 0
    while attempts < 5:
        # 检查是否当前在桌面
        if ".launcher3.Launcher" in driver.current_activity:
            print("检测到应用异常退回到桌面，需要重新开始。")
            return False  # 这将提示 main 函数重新启动应用

        try:
            button = find_right_top_button(driver)
            if button:
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()

                # 检测是否已成功回到激励广告页
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_progress"))
                    )
                    print("检查到转盘")
                    return True
                except TimeoutException:
                    print("未检查到转盘")
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
        except Exception as e:
            print(f"尝试点击右上角关闭按钮时发生错误")
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

# 获取元素
def find_right_top_button(driver):
    try:
        time.sleep(1)  # 间隔等待再次尝试
        elements = []

        # 等待并查找 关闭按钮 元素
        try:
            elements = WebDriverWait(driver, 120).until(lambda d: d.find_elements(MobileBy.CLASS_NAME, "android.widget.ImageView") +
                                                                  d.find_elements(MobileBy.CLASS_NAME, "android.widget.TextView") +
                                                                  d.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout") +
                                                                  d.find_elements(MobileBy.XPATH, "//*[contains(@text, '跳过')]") +
                                                                  d.find_elements(MobileBy.XPATH, "//*[contains(@text, '取消')]"))
        except TimeoutException:
            print("等待 关闭按钮 超时")

        right_top_button = None
        min_distance = float('inf')

        # 遍历找到的元素，选择最符合条件的右上角按钮
        for element in elements:
            if element.size['width'] < 100 and element.size['height'] < 100:
                distance = (element.location['x'] - driver.get_window_size()['width'])**2 + element.location['y']**2
                if distance < min_distance:
                    min_distance = distance
                    right_top_button = element

        return right_top_button
    except Exception as e:
        print(f"获取右上角按钮时发生错误: {str(e)}")
        return None

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'localhost:7555 device',
        # "appPackage": "com.xiangshi.bjxsgc",
        # "appActivity": "com.xiangshi.bjxsgc.activity.LauncherActivity",
        'settings[waitForIdleTimeout]': 100,
        'settings[waitForSelectorTimeout]': 100,
        # 'newCommandTimeout': 300,  # 设置新的命令超时时间为300秒
        'noReset': True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    wait = WebDriverWait(driver, 10)

    # 获取设备的屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    while True:
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
            time.sleep(5)  # 先等待页面可能的加载时间

            # 检查是否有转盘
            try:
                WebDriverWait(driver, 3).until(
                    EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_progress"))
                )
                print("没检查到转盘，加载展示页。")
                handle_display_page(driver, wait, width, height)
                time.sleep(random.randint(2, 5))
            except Exception as e:
                print("检查到转盘，继续循环。")
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

        # time.sleep(random.randint(2, 5))

    # driver.quit()
    print("驱动已关闭，应用退出。")

if __name__ == "__main__":
    while not main():
        print("操作失败，重新尝试。")
