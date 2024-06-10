import re
import os
import time
import random
import threading
import subprocess
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


# 点击关闭按钮
def click_close_button(driver, wait, width, height):
    attempts = 0
    while attempts < 5:
        # 检查是否当前在桌面
        if ".launcher3.Launcher" in driver.current_activity:
            print("检测到应用异常退回到桌面，需要重新开始。")
            return False  # 这将提示 main 函数重新启动应用

        try:
            button = get_close_button(driver, wait, width, height)  # 调用时传递屏幕尺寸
            if button:
                WebDriverWait(driver, 2).until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()

                # 检测是否已成功回到资产页
                if is_on_assets_page(driver, wait, width, height):
                    return True
                # 检测是否已成功回到互助视频页
                elif is_on_ad_page(driver, wait, width, height):
                    return True
                else:
                    print("继续点击关闭按钮")
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
        except TimeoutException:
            print("元素不可点击，超时。")
        except Exception as e:
            print(f"尝试点击右上角关闭按钮时发生错误：{str(e)}")
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

# 获取关闭按钮
def get_close_button(driver, wait, width, height):
    attempts = 0
    min_distance = float('inf')
    close_button = None

    while attempts < 3 and not close_button:  # 尝试次数限制
        start_time = time.time()  # 记录查找开始时间

        # 等待并查找关闭按钮元素，优先查找ImageView
        elements = WebDriverWait(driver, 3).until(
            lambda d: d.find_elements(MobileBy.CLASS_NAME, "android.widget.ImageView") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '跳过')]") +
                      d.find_elements(MobileBy.XPATH, "//*[contains(@text, '取消')]")
                      # d.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
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
                if y_right_top > height * 0.15:
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
                    close_button = element
                    # print("更新最合适的右上角按钮")
            except StaleElementReferenceException:
                # print("元素状态已改变，正在重新获取元素。")
                break  # 退出内部循环，将触发外部循环重新获取元素

        attempts += 1

        elapsed_time = round(time.time() - start_time, 2)
        print(f"本次查找用时: {elapsed_time} 秒")

    if close_button:
        # print(f"找到最合适的右上角关闭按钮：类别-{close_button.get_attribute('className')}, 位置-{close_button.location}, 大小-{close_button.size}")
        pass
    else:
        print("未能找到合适的右上角关闭按钮。")

    return close_button

# 滑屏翻页
def swipe_to_scroll(driver, width, height):
    start_x = random.randint(width // 3, width * 2 // 3)
    start_y = random.randint(height * 8 // 10, height * 9 // 10)
    end_x = random.randint(width // 3, width * 2 // 3)
    end_y = random.randint(height * 1 // 10, height * 2 // 10)
    duration = random.randint(200, 500)
    action = TouchAction(driver)
    action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
    print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

# 获取当前页名
def get_current_activity():
    try:
        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.run(["adb", "shell", "dumpsys", "window", "windows"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if 'mActivityRecord' in line or 'mCurrentFocus' in line:
                # print("原始行:", line)  # 输出原始行以供检查
                match = re.search(r'([^\s/]+)/([^\s/]+)', line)
                if match:
                    package_name = match.group(1)
                    activity_name = match.group(2)
                    if activity_name.startswith('.'):
                        activity_name = package_name + activity_name
                    full_activity_name = f"{activity_name}".replace('..', '.')
                    print("当前页面为:", full_activity_name)  # 在控制台输出获取到的当前页面
                    return full_activity_name
        print("未找到当前焦点的 Activity。")
        return "无法获取当前页面"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"

# 菜单倒计时
def handle_menu_countdown(prompt, timeout=10):
    print(prompt)
    timer = threading.Timer(timeout, lambda: print("\n输入时间已过，将自动从当前账号开始。"))
    timer.start()
    try:
        user_input = input()
        if user_input == '':
            print("没有输入，将自动从当前账号开始。")
        return user_input
    finally:
        timer.cancel()

# 检查返回按钮
def check_back_button(driver, width, height):
    elements = driver.find_elements(By.CLASS_NAME, "android.widget.RelativeLayout")
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

# # 跳转资产页
# def navigate_to_assets_page(driver, wait, width, height):
#     """尝试导航到资产页面，并关闭可能出现的弹窗。"""
#     max_attempts = 3
#     attempts = 0
#     while attempts < max_attempts:
#         try:
#             assets_element = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='资产']")))
#             assets_element.click()
#             print("已找到并点击‘资产’。")
#             time.sleep(random.randint(2, 5))
#
#         except TimeoutException:
#             print("未找到‘资产’元素或未成功到达资产页。")
#         except Exception as e:
#             print(f"检查‘资产’时发生错误: {e}")
#         attempts += 1
#         time.sleep(2)
#
#     print("尝试多次后仍未成功访问资产页。")
#     return False

# 检查资产页
def is_on_assets_page(driver, wait, width, height):
    try:
        # 检查是否存在资产页的特定元素
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))
        )
        print("已成功到达资产页。")
        return True
    except TimeoutException:
        print("未成功到达资产页。")
        return False
    # except TimeoutException:
    #
        # # 检查整点红包弹窗
        # try:
        #     hourly_bonus_popup = WebDriverWait(driver, 2).until(
        #         EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
        #     )
        #     print("检测到整点红包弹窗。")
        #     return True  # 如果检测到红包弹窗，则返回False
        # except TimeoutException:
        #     print("未成功到达资产页。")
        #     return False

# 检查互助视频页
def is_on_ad_page(driver, wait, width, height):
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        print("已成功到达互助视频页")
        return True
    except TimeoutException:
        print("未成功到达互助视频页")
        return False

# 获取我的享币和享点
def get_and_store_points(driver, account):
    try:
        # 获取“我的享币”
        coin_element = driver.find_element(MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_coin")
        my_coin = coin_element.text

        # 获取“我的享点”
        point_element = driver.find_element(MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_point")
        my_point = point_element.text

        # 构造文件路径
        directory = os.path.join("record")
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = os.path.join(directory, "points.txt")

        # 读取现有内容
        points_data = {}
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                for line in file:
                    parts = line.strip().split("，")
                    phone = parts[0].split("：")[1]
                    coin = parts[1].split("：")[1]
                    point = parts[2].split("：")[1]
                    points_data[phone] = (coin, point)

        # 更新当前账号的值
        points_data[account['phone']] = (my_coin, my_point)

        # 覆盖写入新的内容，确保字段对齐
        with open(file_name, "w") as file:
            for phone, (coin, point) in points_data.items():
                file.write(f"帐号：{phone.ljust(15, '　')}享币：{coin.ljust(15, '　')}享点：{point.ljust(15, '　')}\n")

        print(f"已成功获取并存储 {account['phone']} 的享币和享点")
        return True

    except Exception as e:
        print(f"获取并存储 {account['phone']} 的享币和享点时发生异常：{str(e)}")
        return False
