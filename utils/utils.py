import re
import os
import time
import uuid
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
def click_close_button(driver):
    attempts = 0
    while attempts < 5:
        try:
            button = get_close_button(driver)  # 调用时传递driver
            if button:
                driver.wait.until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()
                time.sleep(1)  # 等待加载页面

                assets_page_result = [False]
                ad_page_result = [False]
                event = threading.Event()

                def check_assets_page():
                    assets_page_result[0] = is_on_assets_page(driver)
                    if assets_page_result[0]:
                        event.set()

                def check_ad_page():
                    ad_page_result[0] = is_on_ad_page(driver)
                    if ad_page_result[0]:
                        event.set()

                assets_page_thread = threading.Thread(target=check_assets_page)
                ad_page_thread = threading.Thread(target=check_ad_page)

                assets_page_thread.start()
                ad_page_thread.start()

                # 设置超时避免无限等待
                event.wait(timeout=5)

                assets_result = assets_page_result[0]
                ad_result = ad_page_result[0]

                if assets_result or ad_result:
                    if assets_result:
                        print("已成功到达资产页。")
                    if ad_result:
                        print("已成功到达激励视频页")
                    return True
                else:
                    print("未成功到达任何预期页面。")
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
def get_close_button(driver):
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
        )

        for element in elements:
            try:
                # 输出元素的基本信息
                # KEEP: print(f"检查元素：类别-{element.get_attribute('className')}, 位置-{element.location}, 大小-{element.size}")

                # 先进行尺寸过滤，如果元素的宽度或高度大于等于50，则跳过该元素
                if element.size['width'] >= 120 or element.size['height'] >= 80:
                    # KEEP: print("跳过元素：尺寸超过限制")
                    continue

                # 计算元素右上角到屏幕右上角的距离
                x_right_top = element.location['x'] + element.size['width']
                y_right_top = element.location['y']

                # 过滤掉不在屏幕顶部范围内的元素
                if y_right_top > driver.height * 0.15:
                    # KEEP: print("跳过元素：不在顶部范围内")
                    continue

                # 优先检查元素是否可见和可点击，如果不可见或不可点击，则跳过该元素
                if not (element.is_displayed() and element.is_enabled()):
                    # KEEP: print("跳过元素：不可见或不可点击")
                    continue

                # 计算元素右上角到屏幕右上角的距离
                distance = ((driver.width - x_right_top) ** 2 + y_right_top ** 2) ** 0.5

                # 如果距离更近，更新最小距离和右上角按钮
                if distance < min_distance:
                    min_distance = distance
                    close_button = element
                    # KEEP: print("更新最合适的右上角按钮")
            except StaleElementReferenceException:
                # print("元素状态已改变，正在重新获取元素。")
                break  # 退出内部循环，将触发外部循环重新获取元素

        attempts += 1

        elapsed_time = round(time.time() - start_time, 2)
        print(f"本次查找用时: {elapsed_time} 秒")

    if close_button:
        # KEEP: print(f"找到最合适的右上角关闭按钮：类别-{close_button.get_attribute('className')}, 位置-{close_button.location}, 大小-{close_button.size}")
        pass
    else:
        print("未能找到合适的右上角关闭按钮。")

    return close_button

# 滑屏翻页
def swipe_to_scroll(driver):
    start_x = random.randint(driver.width * 4 // 10, driver.width * 5 // 10)
    start_y = random.randint(driver.height * 8 // 10, driver.height * 8 // 10)
    end_x = random.randint(driver.width * 5 // 10, driver.width * 6 // 10)
    end_y = random.randint(driver.height * 1 // 10, driver.height * 1 // 10)
    duration = random.randint(200, 500)
    action = TouchAction(driver)
    action.press(x=start_x, y=start_y).wait(duration).move_to(x=end_x, y=end_y).release().perform()
    print(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y}) with duration {duration}ms")

# 获取当前页名
def get_current_activity(driver):
    try:
        # 确保 driver 不为 None
        if driver is None:
            raise ValueError("Driver is None")

        udid = driver.capabilities.get('udid', '')
        if not udid:
            raise ValueError("UDID is not available in driver capabilities.")

        # 执行ADB命令，获取窗口管理的详细信息
        result = subprocess.run(["adb", "-s", udid, "shell", "dumpsys", "window", "windows"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ADB命令执行失败，返回码: {result.returncode}")
            print(f"错误信息: {result.stderr}")
            return "ADB命令执行失败"

        lines = result.stdout.splitlines()
        for line in lines:
            if 'mActivityRecord' in line or 'mCurrentFocus' in line:
                # print("原始行:", line)  # 输出原始行以供检查
                match = re.search(r'([^\s/]+)/([^\s/}]+)', line)
                if match:
                    package_name = match.group(1)
                    activity_name = match.group(2)
                    if activity_name.startswith('.'):
                        activity_name = package_name + activity_name
                    full_activity_name = f"{activity_name}".replace('..', '.')
                    # print("当前页面为:", full_activity_name)  # 在控制台输出获取到的当前页面
                    return full_activity_name
        print("未找到当前焦点的 Activity。")
        return "无法获取当前页面"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"

# 检查资产广告页
def is_on_assets_page(driver):
    try:
        # 尝试获取并点击关闭弹窗
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            close_element.click()
        except TimeoutException:
            pass

        # 检查是否存在资产页的特定元素
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))
        )
        # KEEP: print("已成功到达资产广告页。")
        return True
    except TimeoutException:
        # KEEP: print("未成功到达资产广告页。")
        return False

# 检查激励视频页
def is_on_ad_page(driver):
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
        )
        # print("已成功到达激励视频页")
        return True
    except TimeoutException:
        # print("未成功到达激励视频页")
        return False

# 获取我的享币和享点
def get_and_store_points(driver, account):
    try:
        # 获取“我的享币”
        try:
            coin_element = driver.find_element(MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_coin")
            my_coin = coin_element.text
        except NoSuchElementException:
            print("未找到'我的享币'元素")
            my_coin = "未知"

        # 获取“我的享点”
        try:
            point_element = driver.find_element(MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_point")
            my_point = point_element.text
        except NoSuchElementException:
            print("未找到'我的享点'元素")
            my_point = "未知"

        # 构造文件路径
        directory = os.path.join("record", driver.device_name)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
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
        print(f"获取并存储 {account['phone']} 的享币和享点时发生异常：{str(e)}")
        return False

# 激励视频奖励排除名单
def log_mutual_assistance_reward(driver, account):
    try:
        # 创建以 device_name 命名的目录
        directory = os.path.join("record", driver.device_name)
        os.makedirs(directory, exist_ok=True)
        file_name = os.path.join(directory, "mutual_assistance_reward.txt")

        with open(file_name, "a", encoding='utf-8') as file:
            file.write(f"账号：{account['phone']}\n")

        print(f"已成功记录账号：{account['phone']} 激励视频奖励完成")
    except Exception as e:
        print(f"记录账号 {account['phone']} 的激励视频奖励信息时发生异常：{e}")

# 检查是否已经完成激励视频奖励
def has_completed_mutual_assistance_reward(account, device_name):
    file_path = os.path.join("record", device_name, "mutual_assistance_reward.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding='utf-8') as file:
            for line in file:
                if account['phone'] in line:
                    return True
    return False

# 初始化系统日期
def initialize_system_date(device_name):
    try:
        # 定义设备特定的记录目录
        directory = os.path.join("record", device_name)
        # 创建记录目录，如果不存在
        os.makedirs(directory, exist_ok=True)

        # 定义系统日期记录文件的路径
        date_file_path = os.path.join(directory, "system_date.txt")
        # 获取当前系统日期
        today_date = time.strftime("%Y-%m-%d")

        # 打开系统日期记录文件，并将当前日期写入文件
        with open(date_file_path, "w", encoding='utf-8') as file:
            file.write(today_date)
            print(f"当前系统日期: {today_date} 已写入文件: {date_file_path}")

    except Exception as e:
        print(f"初始化系统日期时发生错误: {str(e)}")

# 检查并重置系统日期
def check_and_reset_system_date(device_name):
    # 定义设备特定的记录目录
    directory = os.path.join("record", device_name)
    date_file_path = os.path.join(directory, "system_date.txt")
    mutual_assistance_file_path = os.path.join(directory, "mutual_assistance_reward.txt")

    # 获取当前系统日期
    today_date = time.strftime("%Y-%m-%d")

    # 读取上次记录的系统日期
    with open(date_file_path, "r", encoding='utf-8') as file:
        last_date = file.read().strip()

    # 如果上次记录的系统日期与当前日期不一致
    if last_date != today_date:
        with open(mutual_assistance_file_path, "w", encoding='utf-8') as file:
            file.write("")  # 清空文件内容

        # 更新系统日期记录文件为当前日期
        with open(date_file_path, "w", encoding='utf-8') as file:
            file.write(today_date)

        print("已重置任务完成记录")
        return True  # 表示日期已更改
    return False  # 表示日期未更改
