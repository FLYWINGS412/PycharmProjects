import re
import time
import random
from time import sleep
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 滑屏翻页
def perform_swipe_and_check(driver, wait, width, height):
    try:
        while True:
            start_time = time.time()  # 记录循环开始时间

            # 执行滑动操作
            start_x = random.randint(width // 3, width * 2 // 3)
            start_y = random.randint(height * 8 // 10, height * 9 // 10)
            end_x = random.randint(width // 3, width * 2 // 3)
            end_y = random.randint(height * 1 // 10, height * 2 // 10)
            duration = random.randint(200, 500)
            action = TouchAction(driver)
            action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
            print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

            # 检查并处理可能出现的弹窗
            check_and_handle_popups(driver)

            # 等待页面完成加载
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
            )
            print("页面已正常加载")

            # sleep(random_sleep)  # 翻页后的随机等待时间
            random_sleep = random.randint(0, 20)
            print(f"等待 {random_sleep} 秒")
            time.sleep(random_sleep)

            # 检查并处理可能出现的弹窗
            check_and_handle_popups(driver)

            # 立即检查 layer_redbag 元素是否存在
            elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
            if elements:
                print("找到了元素，继续循环")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
            else:
                # 第一次未找到元素时，再次处理弹窗并重新检查
                print("未找到元素，再次检查弹窗")

                # 检查并处理可能出现的弹窗
                check_and_handle_popups(driver)

                # 立即检查 layer_redbag 元素是否存在
                elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
                if not elements:
                    print("再次检查后仍未找到元素，退出循环")
                    break
    except Exception as e:
        print(f"在滑屏循环中发生错误：{e}")
        return False

    return True

# 弹窗红包
def check_and_handle_popups(driver):
    found_and_handled = False  # 初始化标记，假定没有找到或处理弹窗
    try:
        # 直接尝试获取接收弹窗元素
        bg_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
        )
        time.sleep(random.randint(2, 5))  # 随机等待2-5秒
        bg_element.click()
        print("点击了接收弹窗")
        found_and_handled = True  # 更新标记为已找到并处理弹窗

        # 尝试获取并点击关闭弹窗，仅在元素存在时执行
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            close_element.click()
            print("点击了关闭弹窗")
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            found_and_handled = True  # 确认找到并处理了关闭弹窗
        except TimeoutException:
            print("未找到关闭弹窗元素，不执行关闭操作")
    except TimeoutException:
        print("未找到弹窗或等待关闭弹窗超时")

    return found_and_handled

# 跳转资产页
def navigate_to_assets_page(driver, wait, width, height):
    """尝试导航到资产页面，并关闭可能出现的弹窗。"""
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            assets_element = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='资产']")))
            assets_element.click()
            print("已找到并点击‘资产’。")
            time.sleep(random.randint(2, 5))

            if handle_hourly_bonus(driver, wait, width, height):
                print("已领取整点红包")
                return True
            else:
                print("领取整点红包后未成功到达资产页")

            if is_on_assets_page(driver, wait, width, height):
                return True
            else:
                print("未成功到达资产页，尝试再次点击。")
        except TimeoutException:
            print("未找到‘资产’元素或未成功到达资产页。")
        except Exception as e:
            print(f"检查‘资产’时发生错误: {e}")
        attempts += 1
        time.sleep(2)

    print("尝试多次后仍未成功访问资产页。")
    return False

# 整点红包
def handle_hourly_bonus(driver, wait, width, height):
    try:
        # 检测是整点红包
        try:
            receive_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
            )
            time.sleep(random.randint(2, 5))
            receive_button.click()
            print("点击了立即领取。")

            # 处理展示页
            if not handle_display_page(driver, wait, width, height):
                print("处理展示页时出错。")
                return False

            # 尝试获取并点击关闭弹窗
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(1, 5))  # 随机等待1-5秒
            close_element.click()
            print("点击了关闭弹窗")
        except TimeoutException:
            print("未找到整点红包按钮，跳过此部分。")

    except Exception as e:
        print(f"处理活动时发生异常")
        return False

    # 检测是否已成功回到资产页
    return is_on_assets_page(driver, wait, width, height)

# 检查资产页或弹窗
def is_on_assets_page(driver, wait, width, height):
    try:
        # 检查是否存在资产页的特定元素
        assets_page_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))
        )
        print("已成功到达资产页。")
        return True
    except TimeoutException:

        # 检查整点红包弹窗
        try:
            hourly_bonus_popup = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            print("检测到整点红包弹窗。")
            return True  # 如果检测到红包弹窗，则返回False
        except TimeoutException:
            print("未成功到达资产页。")
            return False

# 点击领取
def click_miss_bubble(driver, wait, width, height):
    try:
        while True:  # 使用无限循环，直到所有奖励被领取或发生异常
            start_time = time.time()  # 记录循环开始时间
            try:
                miss_bubble_element = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_miss_bubble")))
                miss_bubble_text = miss_bubble_element.text
                current, total = map(int, miss_bubble_text.replace(" ", "").strip('()').split('/'))
                print(f"当前状态：{current}/{total}")

                if current >= total:
                    print("所有奖励已领取完毕。")
                    break

                receive_bubble = wait.until(EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
                receive_bubble.click()
                print(f"点击了领取按钮，更新剩余次数：{current+1}/{total}")

                if not handle_display_page(driver, wait, width, height):  # 处理展示页的逻辑
                    return False

                time.sleep(random.randint(1, 5))

                # 输出循环用时
                elapsed_time = round(time.time() - start_time, 2)
                print(f"用时: {elapsed_time} 秒")

            except StaleElementReferenceException:
                print("元素不再存在于 DOM 中，重新获取元素。")
                continue

    except (TimeoutException, NoSuchElementException):
        print("找不到 txt_miss_bubble 或 txt_receive_bubble 元素，无法点击。")
        return False
    return True

# 领取奖励
def click_reward(driver, wait, width, height):
    base_xpaths = [
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"
    ]

    last_successful_index = 1  # 从最后一次成功的位置开始
    while True:
        start_time = time.time()  # 记录循环开始时间
        found = False
        for i in range(last_successful_index, 7):  # 假设有6个奖励按钮
            for base_xpath in base_xpaths:
                xpath = base_xpath.format(i=i)  # 动态生成每个按钮的 XPath
                try:
                    reward = wait.until(EC.presence_of_element_located((MobileBy.XPATH, xpath)))
                    if reward.get_attribute("selected") == "true":
                        reward.click()
                        print(f"点击了位于 {i} 的领取奖励，使用的XPath为: {xpath}")
                        if not handle_display_page(driver, wait, width, height):  # 处理展示页的逻辑
                            return False
                        last_successful_index = i + 1  # 更新最后成功的索引
                        found = True
                        break  # 成功点击后退出内循环
                except TimeoutException:
                    print(f"未能及时找到位于 {i} 的领取奖励，路径：{xpath}")
                except NoSuchElementException:
                    print(f"未能定位到位于 {i} 的领取奖励，路径：{xpath}")
                except Exception as e:
                    print(f"尝试点击位于 {i} 的领取奖励时发生异常，路径：{xpath}")
            if found:
                break  # 成功点击后退出外循环
        if not found:
            print("未找到任何选中的‘领取奖励’按钮或已完成所有奖励领取。")
            break

        time.sleep(random.randint(1, 5))

        # 输出循环用时
        elapsed_time = round(time.time() - start_time, 2)
        print(f"用时: {elapsed_time} 秒")
    return True

# 展示页
def handle_display_page(driver, wait, width, height):
    try:
        start_time = time.time()
        timeout = 70
        popup_texts = ["放弃", "离开", "取消"]
        handled_popup = False

        while time.time() - start_time < timeout:
            # 检查弹窗
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
                        start_y = random.randint(height * 8 // 10, height * 9 // 10)
                        end_x = random.randint(width // 3, width * 2 // 3)
                        end_y = random.randint(height * 1 // 10, height * 2 // 10)
                        duration = random.randint(200, 500)
                        action = TouchAction(driver)
                        action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
                        print(f"检查到返回按钮，Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")
                        break

            # 检查倒计时是否消失
            try:
                element_to_wait = None

                # 第一种检查倒计时的方法
                if driver.find_elements(MobileBy.XPATH, "//android.widget.TextView[contains(@text, 's')]"):
                    text_views = driver.find_elements(MobileBy.XPATH, "//android.widget.TextView[contains(@text, 's')]")
                    for text_view in text_views:
                        location = text_view.location
                        size = text_view.size
                        top_y = location['y']
                        # print(f"检查元素: 文本='{text_view.text}', 位置='{location}', 大小='{size}'")
                        if top_y < height * 0.15:
                            element_to_wait = text_view
                            break

                    if element_to_wait and isinstance(element_to_wait, WebElement):
                        # 使用正则表达式匹配 '0 s' 或 '0s'
                        print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                        WebDriverWait(driver, 3).until(lambda driver: re.match(r"0\s*s", element_to_wait.text) is not None)
                        print("倒计时结束。")
                        break  # 结束while循环

                # 第二种检查倒计时的方法（长度为1或2的纯数字倒计时）
                elif driver.find_elements(MobileBy.XPATH, "//android.widget.TextView[string-length(@text) <= 2 and @text = number(@text)]"):
                    text_views = driver.find_elements(MobileBy.XPATH, "//android.widget.TextView[string-length(@text) <= 2 and @text = number(@text)]")
                    for text_view in text_views:
                        location = text_view.location
                        size = text_view.size
                        top_y = location['y']
                        # print(f"检查元素: 文本='{text_view.text}', 位置='{location}', 大小='{size}'")
                        if top_y < height * 0.15:
                            element_to_wait = text_view
                            print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                            break

                    if element_to_wait and isinstance(element_to_wait, WebElement):
                        print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                        WebDriverWait(driver, 2).until(lambda driver: element_to_wait.text == '0')
                        print("倒计时结束。")
                        break

                # 检查其他可能的倒计时元素
                elif driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id"):
                    element_to_wait = (MobileBy.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")
                    WebDriverWait(driver, 2).until(EC.invisibility_of_element_located(element_to_wait))
                    print("特定ID的倒计时元素已消失。")
                    break

            except TimeoutException:
                continue

        # 检查弹窗
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

        # 调用点击元素函数
        if not retry_click_right_top_button(driver, wait, width, height):
            return False

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
        return False
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))
        return False
    return True

# 点击元素
def retry_click_right_top_button(driver, wait, width, height):
    attempts = 0
    while attempts < 5:
        # 检查是否当前在桌面
        if ".launcher3.Launcher" in driver.current_activity:
            print("检测到应用异常退回到桌面，需要重新开始。")
            return False  # 这将提示 main 函数重新启动应用

        try:
            button = find_right_top_button(driver, wait, width, height)  # 调用时传递屏幕尺寸
            if button:
                WebDriverWait(driver, 2).until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()

                # 检测是否已成功回到资产页
                if is_on_assets_page(driver, wait, width, height):
                    return True
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
        except Exception as e:
            print(f"尝试点击右上角关闭按钮时发生错误：{str(e)}")
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

# 获取元素
def find_right_top_button(driver, wait, width, height):
    attempts = 0
    min_distance = float('inf')
    right_top_button = None

    while attempts < 3 and not right_top_button:  # 尝试次数限制
        start_time = time.time()  # 记录查找开始时间

        # 等待并查找关闭按钮元素，优先查找ImageView
        elements = WebDriverWait(driver, 3).until(
            lambda d: d.find_elements(MobileBy.CLASS_NAME, "android.widget.ImageView") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '跳过')]") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '取消')]") +
                      d.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
            # d.find_elements(MobileBy.CLASS_NAME, "android.widget.TextView")
        )

        for element in elements:
            try:
                # 输出元素的基本信息
                # print(f"检查元素：类别-{element.get_attribute('className')}, 位置-{element.location}, 大小-{element.size}")

                # 先进行尺寸过滤，如果元素的宽度或高度大于等于50，则跳过该元素
                if element.size['width'] >= 50 and element.size['height'] >= 50:
                    # print("跳过元素：尺寸超过限制")
                    continue

                # 计算元素右上角到屏幕右上角的距离
                x_right_top = element.location['x'] + element.size['width']
                y_right_top = element.location['y']

                # 过滤掉不在屏幕顶部范围内的元素
                if y_right_top > height * 0.25:
                    # print("跳过元素：不在顶部范围内")
                    continue

                # 优先检查元素是否可见和可点击，如果不可见或不可点击，则跳过该元素
                if not (element.is_displayed() and element.is_enabled()):
                    # print("跳过元素：不可见或不可点击")
                    continue

                # 计算元素右上角到屏幕右上角的距离
                distance = ((width - x_right_top) ** 2 + y_right_top ** 2) ** 0.5

                # 如果距离更近，更新最小距离和右上角按钮
                if distance < min_distance:
                    min_distance = distance
                    right_top_button = element
                    print("更新最合适的右上角按钮")
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
    # time.sleep(30)  # 等待APP完全加载

    # 等待页面完成加载
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
    )
    print("首次加载页面已完成")

    # 检查并处理可能出现的弹窗
    check_and_handle_popups(driver)

    # 获取屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    try:
        # # 首页滑屏
        # if not perform_swipe_and_check(driver, wait, width, height):
        #     print("首页滑屏错误，程序终止。")
        #     return False
        #
        # # 跳转资产页
        # time.sleep(random.randint(2, 5))
        # if not navigate_to_assets_page(driver, wait, width, height):
        #     print("未能导航到资产页面，程序终止。")
        #     return False

        # 点击领取
        time.sleep(random.randint(2, 5))
        if not is_on_assets_page(driver, wait, width, height) or not click_miss_bubble(driver, wait, width, height):
            return False  # 不在资产页或领取气泡失败，重新尝试

        # 领取奖励
        time.sleep(random.randint(2, 5))
        if not is_on_assets_page(driver, wait, width, height) or not click_reward(driver, wait, width, height):
            return False  # 不在资产页或领取奖励失败，重新尝试

        print("所有操作完成，准备退出应用。")
        return True  # 返回 True 表示成功完成操作

    except Exception as e:
        print(f"处理中发生异常：{str(e)}")
        return False

    finally:
        driver.quit()
        print("驱动已关闭，应用退出。")

if __name__ == "__main__":
    while not main():
        print("操作失败，重新尝试。")
