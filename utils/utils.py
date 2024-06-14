import re
import os
import time
import random
import threading
import subprocess
from time import sleep
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from auth import auth
from tasks import tasks
from utils import utils
from popups import popups

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
                time.sleep(1)    # 等待加载页面

                # 使用多线程同时检查资产页和互助视频页
                assets_page_result = [False]
                ad_page_result = [False]

                def check_assets_page():
                    assets_page_result[0] = is_on_assets_page(driver, wait, width, height)

                def check_ad_page():
                    ad_page_result[0] = is_on_ad_page(driver, wait, width, height)

                assets_page_thread = threading.Thread(target=check_assets_page)
                ad_page_thread = threading.Thread(target=check_ad_page)

                assets_page_thread.start()
                ad_page_thread.start()

                assets_page_thread.join()
                ad_page_thread.join()

                assets_result = assets_page_result[0]
                ad_result = ad_page_result[0]

                if assets_result or ad_result:
                    if assets_result:
                        print("已成功到达资产页。")
                    if ad_result:
                        print("已成功到达互助视频页")
                    return True
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
        except TimeoutException:
            print("元素不可点击，超时。")
        except Exception as e:
            # print(f"尝试点击右上角关闭按钮时发生错误：{str(e)}")
            print(f"尝试点击右上角关闭按钮时发生错误")
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
                      d.find_elements(MobileBy.XPATH, "//android.widget.TextView[@text='跳过']") +
                      d.find_elements(MobileBy.XPATH, "//android.widget.TextView[@text='取消']")
                      # d.find_elements(MobileBy.CLASS_NAME, "android.widget.RelativeLayout")
        )

        for element in elements:
            try:
                # 输出元素的基本信息
                # print(f"检查元素：类别-{element.get_attribute('className')}, 位置-{element.location}, 大小-{element.size}")

                # 先进行尺寸过滤，如果元素的宽度或高度大于等于50，则跳过该元素
                if element.size['width'] >= 150 and element.size['height'] >= 50:
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
        # return f"执行 adb 命令时发生错误: {e}"
        return f"执行 adb 命令时发生错误"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"
        return f"获取当前 Activity 时发生错误"

# 检查返回按钮
def check_back_button(driver, width, height):
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

        except TimeoutException:
            print("未找到‘资产’元素或未成功到达资产页。")
        except Exception as e:
            # print(f"检查‘资产’时发生错误: {e}")
            print(f"检查‘资产’时发生错误")
        attempts += 1
        time.sleep(2)

    print("尝试多次后仍未成功访问资产页。")
    return False

# 检查资产广告页
def is_on_assets_page(driver, wait, width, height):
    try:
        # 尝试获取并点击关闭弹窗
        try:
            close_element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            close_element.click()
        except TimeoutException:
            pass

        # 检查是否存在资产页的特定元素
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))
        )
        # print("已成功到达资产广告页。")
        return True
    except TimeoutException:
        # print("未成功到达资产广告页页。")
            pass

# 检查激励视频页
def is_on_ad_page(driver, wait, width, height):
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        # print("已成功到达激励视频页")
        return True
    except TimeoutException:
        # print("未成功到达激励视频页")
            pass
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
            with open(file_name, "r", encoding='utf-8') as file:
                for line in file:
                    try:
                        parts = line.strip().split("，")
                        if len(parts) == 4:
                            name = parts[0].split("：")[1].strip()
                            phone = parts[1].split("：")[1].strip()
                            coin = parts[2].split("：")[1].strip()
                            point = parts[3].split("：")[1].strip()
                            points_data[phone] = (name, coin, point)
                        else:
                            print(f"忽略格式错误的行: {line}")
                    except IndexError as e:
                        print(f"解析行时发生错误: {line}, 错误: {e}")

        # 更新当前账号的值
        points_data[account['phone']] = (account['name'], my_coin, my_point)

        # 确定最长的电话长度和名字长度以确保对齐
        max_phone_length = max(len(phone) for phone in points_data.keys())
        max_name_length = max(len(name) for name, _, _ in points_data.values())

        # 覆盖写入新的内容，确保字段对齐
        with open(file_name, "w", encoding='utf-8') as file:
            for phone, (name, coin, point) in points_data.items():
                name_field = f"名字：{name}".ljust(max_name_length + 4)
                phone_field = f"帐号：{phone}".ljust(max_phone_length + 4)
                coin_field = f"享币：{coin}".ljust(20)
                point_field = f"享点：{point}".ljust(20)
                file.write(f"{name_field}，{phone_field}，{coin_field}，{point_field}\n")

        print(f"已成功获取并存储 {account['phone']} 的享币和享点")
        return True

    except Exception as e:
        # print(f"获取并存储 {account['phone']} 的享币和享点时发生异常：{str(e)}")
        print(f"获取并存储 {account['phone']} 的享币和享点时发生异常")
        return False

# # 首页红包奖励排除名单
# def log_handle_home_page_video(account):
#     try:
#         directory = os.path.join("record")
#         if not os.path.exists(directory):
#             os.makedirs(directory)
#         file_name = os.path.join(directory, "handle_home_page_video.txt")
#
#         with open(file_name, "a", encoding='utf-8') as file:
#             file.write(f"账号：{account['phone']}\n")
#
#         print(f"已成功记录账号：{account['phone']} 的首页红包奖励完成")
#     except Exception as e:
#         print(f"记录账号 {account['phone']} 的首页红包奖励信息时发生异常：{str(e)}")
#
# # 检查是否已经完成首页红包奖励
# def has_completed_handle_home_page_video(account):
#     file_path = os.path.join("record", "handle_home_page_video.txt")
#     if os.path.exists(file_path):
#         with open(file_path, "r", encoding='utf-8') as file:
#             for line in file:
#                 if account['phone'] in line:
#                     return True
#     return False

# 激励视频奖励排除名单
def log_mutual_assistance_reward(account):
    try:
        directory = os.path.join("record")
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = os.path.join(directory, "mutual_assistance_reward.txt")

        with open(file_name, "a", encoding='utf-8') as file:
            file.write(f"账号：{account['phone']}\n")

        print(f"已成功记录账号：{account['phone']} 激励视频奖励完成")
    except Exception as e:
        # print(f"记录账号 {account['phone']} 的激励视频奖励信息时发生异常：{str(e)}")
        print(f"记录账号 {account['phone']} 的激励视频奖励信息时发生异常")

# 检查是否已经完成激励视频奖励
def has_completed_mutual_assistance_reward(account):
    file_path = os.path.join("record", "mutual_assistance_reward.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding='utf-8') as file:
            for line in file:
                if account['phone'] in line:
                    return True
    return False

# 初始化系统日期
def initialize_system_date():
    try:
        # 定义记录目录
        directory = "record"
        # 如果记录目录不存在，则创建它
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 定义系统日期记录文件的路径
        date_file_path = os.path.join(directory, "system_date.txt")
        # 获取当前系统日期
        today_date = time.strftime("%Y-%m-%d")

        # 打开系统日期记录文件，并将当前日期写入文件
        with open(date_file_path, "w", encoding='utf-8') as file:
            file.write(today_date)
            print(f"当前系统日期: {today_date} 已写入文件: {date_file_path}")

    except Exception as e:
        # 捕获并打印任何异常
        # print(f"初始化系统日期时发生错误: {str(e)}")
        print(f"初始化系统日期时发生错误")

# 检查并重置系统日期
def check_and_reset_system_date():
    # 定义记录目录和文件路径
    directory = "record"
    date_file_path = os.path.join(directory, "system_date.txt")
    # handle_home_page_video_file_path = os.path.join(directory, "handle_home_page_video.txt")
    mutual_assistance_file_path = os.path.join(directory, "mutual_assistance_reward.txt")

    # 获取当前系统日期
    today_date = time.strftime("%Y-%m-%d")

    # 读取上次记录的系统日期
    with open(date_file_path, "r", encoding='utf-8') as file:
        last_date = file.read().strip()

    # 如果上次记录的系统日期与当前日期不一致
    if last_date != today_date:
        # 清空相关任务记录文件
        # with open(handle_home_page_video_file_path, "w", encoding='utf-8') as file:
        #     file.write("")  # 清空文件内容
        with open(mutual_assistance_file_path, "w", encoding='utf-8') as file:
            file.write("")  # 清空文件内容

        # 更新系统日期记录文件为当前日期
        with open(date_file_path, "w", encoding='utf-8') as file:
            file.write(today_date)

        print("已重置任务完成记录")
        return True  # 表示日期已更改
    return False  # 表示日期未更改
