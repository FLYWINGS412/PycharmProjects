import re
import os
import sys
import time
import json
import random
import portalocker
import tkinter as tk
from appium import webdriver
from datetime import datetime
from difflib import SequenceMatcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 定义函数，截图并保存
def take_screenshot_with_date(driver, folder_path):
    current_date = datetime.now().strftime("%Y%m%d")

    # 从 desired_caps 中获取设备名称
    device_name = desired_caps.get('deviceName', 'UnknownDevice')

    # 获取或创建目录，将设备名称和日期包含在路径中
    screenshot_folder = os.path.join(folder_path, 'screenshot', current_date)
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    # 生成文件名并保存截图
    screenshot_number = get_screenshot_number(screenshot_folder, current_date)
    screenshot_filename = f"{current_date}-{screenshot_number}.png"
    screenshot_path = os.path.join(screenshot_folder, screenshot_filename)
    driver.save_screenshot(screenshot_path)
    print(f"截图保存为: {screenshot_path}")

# 定义函数，获取截图编号
def get_screenshot_number(folder_path, current_date):
    screenshot_number = 1
    if os.path.exists(folder_path):
        existing_files = [f for f in os.listdir(folder_path) if f.startswith(current_date) and f.endswith(".png")]
        if existing_files:
            # 按照数字部分排序文件名
            existing_files.sort(key=lambda f: int(re.search(r'-(\d+)', f).group(1)))
            last_file = existing_files[-1]
            last_number = int(re.search(r'-(\d+)', last_file).group(1))
            screenshot_number = last_number + 1
    return screenshot_number

# 更换账号
def switch_account(main_view):
    # 在 dp-main 父容器下查找并点击 "回到首页" 按钮
    try:
        time.sleep(5)
        home_button = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="回到首页"]'))
        )
        home_button.click()
        print("成功点击'回到首页'按钮")
    except Exception as e:
        print(f"点击'回到首页'按钮失败")

    # 查找并点击 "我的" 按钮
    try:
        time.sleep(5)
        mcommon_my_view = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "mCommonMy")]'))
        )
        mcommon_my_view.click()  # 直接点击 mCommonMy 父容器
        print("成功点击'我的'按钮")
    except Exception as e:
        print(f"点击'我的'按钮失败")

    # 在 dp-main 父容器下查找并点击 "更换账号" 按钮
    try:
        time.sleep(5)
        switch_account_button = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="更换账号"]'))
        )
        switch_account_button.click()
        print("成功点击'更换账号'按钮")
    except Exception as e:
        print(f"点击'更换账号'按钮失败")

# 刷新页面
def refresh_page(driver):
    try:
        loading_state_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.mmbox.xbrowser:id/btn_loading_state'))
        )
        loading_state_button.click()
        print("页面已刷新")
        time.sleep(8)  # 等待页面加载完成
    except Exception as e:
        print(f"刷新页面失败")

# 执行翻页
def perform_page_scroll(driver):
    try:
        # 获取设备屏幕的尺寸
        window_size = driver.get_window_size()
        screen_width = window_size['width']
        screen_height = window_size['height']

        # 计算滑动的起点和终点（从屏幕底部向上滑动）
        start_x = screen_width // 2  # 横向居中
        start_y = screen_height * 9 // 10  # 滑动起点靠近屏幕底部
        end_y = screen_height * 1 // 10  # 滑动终点靠近屏幕顶部

        # 使用 TouchAction 执行全屏向上滑动操作
        TouchAction(driver).press(x=start_x, y=start_y).wait(500).move_to(x=start_x, y=end_y).release().perform()
        print("成功模拟全屏向上翻页动作")
    except Exception as e:
        print(f"全屏翻页失败")

# 定义函数：保存浏览商品的数量到同一个文件中
def save_browsed_item_count(count):
    # 从 desired_caps 中获取设备名称，假设 deviceName 是手机号
    device_name = desired_caps.get('deviceName', 'UnknownDevice')

    # 在函数内部定义目录路径
    log_directory = os.path.join(os.getcwd(), "logs")

    # 确保目录存在，如果不存在则创建
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    current_date = datetime.now().strftime("%Y%m%d")
    file_name = f"{current_date}.txt"
    file_path = os.path.join(log_directory, file_name)

    # 初始化数据列表
    data_lines = []
    total_count = 0  # 用于存储总浏览数量

    # 使用文件锁，确保只有一个进程可以访问文件
    with open(file_path, 'a+') as f:
        portalocker.lock(f, portalocker.LOCK_EX)  # 加锁

        f.seek(0)  # 移动到文件开头
        data_lines = f.readlines()  # 读取现有数据

        # 更新当前 deviceName 的数据
        updated = False
        f.seek(0)  # 再次移动到开头，准备重写文件
        f.truncate(0)  # 清空文件内容

        for line in data_lines:
            # 如果当前行包含该设备名称，更新其数量
            if line.startswith(device_name):
                f.write(f"{device_name}: {count}\n")
                updated = True
            # 如果是记录总浏览数量的行，跳过（我们稍后重新计算）
            elif line.startswith("Total:"):
                continue
            else:
                f.write(line)

        # 如果未更新，说明是新设备，追加数据
        if not updated:
            f.write(f"{device_name}: {count}\n")

        # 重新计算总浏览数量
        f.flush()  # 确保之前的写操作已完成
        f.seek(0)
        new_data_lines = f.readlines()

        total_count = 0
        # 此处已经更新设备的数据，因此用最新的文件内容来重新计算总数
        for line in new_data_lines:
            if ":" in line and not line.startswith("Total:"):
                try:
                    _, value = line.split(":")
                    total_count += int(value.strip())
                except ValueError:
                    print(f"无效的计数格式: {line.strip()}")

        # 写入新的总浏览数量
        f.write(f"Total: {total_count}\n")
        portalocker.unlock(f)  # 解锁

# 定义函数：从文件中加载已浏览商品的数量
def load_browsed_item_count():
    # 从 desired_caps 中获取设备名称
    device_name = desired_caps.get('deviceName', 'UnknownDevice')

    # 在函数内部定义目录路径
    log_directory = os.path.join(os.getcwd(), "logs")

    # 确保目录存在
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    current_date = datetime.now().strftime("%Y%m%d")
    file_name = f"{current_date}.txt"  # 文件名为当前日期
    file_path = os.path.join(log_directory, file_name)

    # 如果文件不存在，创建文件并返回初始计数为 0
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("")  # 创建空文件
        return 0

    # 初始化计数
    count = 0

    # 使用文件锁，确保只有一个进程可以访问文件
    with open(file_path, 'r') as f:
        portalocker.lock(f, portalocker.LOCK_SH)  # 共享锁
        data_lines = f.readlines()
        for line in data_lines:
            if line.startswith(device_name):
                try:
                    _, value = line.split(":")
                    count = int(value.strip())
                except ValueError:
                    print(f"无效的计数格式: {line.strip()}")
                break
        portalocker.unlock(f)  # 解锁

    return count

# 提交第一行商品任务
def submit_first_item_task(main_view, first_item):
    first_item_completed = False  # 第一行商品标记为“未完成”

    while True:  # 无限循环
        # 在第一行商品下查找 "提交" 按钮并点击
        try:
            submit_button = WebDriverWait(first_item, 5).until(
                EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "提交")]'))
            )  # 注意这里的括号关闭
            submit_button.click()  # 这一行要缩进到try块内部
            print("成功点击第一行商品的'提交'按钮")
        except Exception as e:
            print(f"未找到第一行商品的'提交'按钮")

        # 确定提交商品
        try:
            time.sleep(5)
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, '//android.widget.TextView | //android.widget.Button'))
            )

            # 遍历找到的所有元素，检查是否包含 "确定提交商品" 或 "确定"
            for element in elements:
                text = element.text

                # 1. 检查是否存在 "确定提交商品"
                if "确定提交商品" in text:
                    print(f"检测到 '确定提交商品'，完整文本为: {text}")

                    # 查找并点击 "确定" 按钮
                    for btn in elements:
                        if "确定" == btn.text:
                            btn.click()
                            print("成功点击 '确定' 按钮，提交商品")
                            break  # 点击后跳出内层循环
                    break  # 点击 '确定' 后跳出外层循环，避免元素引用失效导致的异常

                # 2. 检查是否存在 "活动太火爆啦"
                elif "活动太火爆啦" in text:
                    print("检测到 '活动太火爆啦'，进入等待循环")

                    # 持续检查 "活动太火爆啦" 是否消失
                    while True:
                        time.sleep(5)  # 等待3秒，避免频繁操作
                        try:
                            # 重新检测 "活动太火爆啦" 提示
                            over_activity_message = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "活动太火爆啦")]'))
                            )

                            if over_activity_message:
                                continue  # 如果仍然存在 "活动太火爆啦"，继续循环等待
                        except Exception:
                            print("检测到 '活动太火爆啦' 消失，准备返回并执行后续操作")
                            break  # 退出循环，继续执行后面的代码

                    # 提示消失后，执行返回操作
                    time.sleep(5)  # 等待5秒，确保返回操作完成
                    submit_task_completion(driver, main_view)  # 提交任务完成的状态
                    exit()  # 终止程序

                # 3. 检查是否存在 "请检查您的账号状态"
                elif "请检查您的账号状态" in text:
                    print("检测到 '请检查您的账号状态'，终止程序。")
                    exit()  # 终止程序

        except Exception as e:
            print(f"'确定提交商品'时出现异常")

        # 处理“提交商品”时的异常
        try:
            # 点击 "确定" 按钮后再检查是否有异常
            time.sleep(5)  # 等待可能的弹出窗口
            new_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, '//android.widget.TextView | //android.widget.Button | //android.view.View'))
            )

            # 遍历新元素，检查是否有异常
            for new_element in new_elements:
                new_text = new_element.text

                # 检查是否存在 "任务不匹配"
                if "任务不匹配" in new_text:
                    print(f"检测到 '任务不匹配'，完整文本为: {new_text}")
                    driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                    return False  # 返回 False，表示任务不匹配

                # 检查是否存在 "当前账号暂时无法做任务"
                elif "当前账号暂时无法做任务" in new_text:
                    print("当前账号暂时无法做任务")
                    exit()  # 终止程序

                # 检查是否存在 "任务不合格"
                elif "任务不合格" in new_text:
                    print("任务不合格")
                    exit()  # 终止程序

                # 检查是否存在 "任务已过期"
                elif "任务已过期" in new_text:
                    print("检测到 '任务已过期'，重新获取任务")
                    driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                    return False  # 返回 False，表示任务已过期

                # 检查是否存在 "BAD REQUEST"
                elif "BAD REQUEST" in new_text:
                    print("检测到 'BAD REQUEST'，准备返回")
                    driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                    continue  # 重新进入 while True 循环

                # 检查是否存在 "正在提交"
                elif "正在提交" in new_text:
                    print("检测到 '正在提交'，准备返回")
                    driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                    continue  # 重新进入 while True 循环

        except Exception as e:
            print(f"处理'提交商品'时出现异常")

        # 检查第一行商品是否 "已完成"
        try:
            WebDriverWait(first_item, 8).until(
                EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "已完成")]'))
            )
            print("'已完成'第一行商品任务")

            # 更新浏览数量
            browsed_item_count = load_browsed_item_count()  # 重新加载计数
            browsed_item_count += 1
            print(f"浏览商品数量更新为：{browsed_item_count}")

            try:
                save_browsed_item_count(browsed_item_count)
            except Exception as e:
                print(f"保存浏览商品数量时出错")

            return True  # 返回检查第一行商品 "已完成"

        except Exception:
            print("'未完成'第一行商品任务，继续提交任务")
            refresh_page(driver)

# 提交任务
def submit_task_completion(driver, main_view):
    # 查找并点击 "任务完成" 按钮
    while True:  # 使用循环以防任务未完成时反复点击
        try:
            time.sleep(5)
            Task_Completed = WebDriverWait(main_view, 10).until(
                EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="任务完成"]'))
            )
            Task_Completed.click()
            print("成功点击'任务完成'按钮")
        except Exception as e:
            print(f"点击'任务完成'按钮失败")
            break  # 如果点击任务失败，退出循环

        # 确定 "任务完成"
        try:
            time.sleep(5)
            confirm_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@text="确定"]'))
            )
            confirm_button.click()
            print("成功点击全屏的'确定'按钮")

            time.sleep(10)
            refresh_page(driver)

            # 检查 "任务完成" 是否消失
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.XPATH, './/android.widget.Button[@text="任务完成"]'))
                )
                print("'任务完成'按钮已消失")
                break  # 如果"任务完成"已消失，退出循环
            except TimeoutException:
                print("'任务完成'按钮未消失，重新尝试点击")
                continue  # 继续循环，重新点击"任务完成"按钮

        except Exception as e:
            print(f"未找到全屏的'确定'按钮")
            break  # 如果找不到"确定"按钮，退出循环

# 查找商店
def find_and_click_shop(driver, target_shop_name, main_view, max_attempts=3):
    attempts = 0
    shop_found = False

    while attempts < max_attempts and not shop_found:
        try:
            time.sleep(5)
            # 获取父容器，包含所有店铺项的列表
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[contains(@resource-id, "pro_info_below_") or contains(@text, "验证")]')
                )
            )
            parent_containers = [el for el in elements if 'pro_info_below_' in el.get_attribute('resource-id')]
            verify_elements = [el for el in elements if '验证' in el.text]

            if parent_containers:
                print(f"找到 {len(parent_containers)} 个店铺项")
                matches = []

                # 遍历每个父容器，查找店铺名称
                for index, parent_container in enumerate(parent_containers, start=1):
                    try:
                        # 在父容器下查找所有具有 text 属性的 android.view.View 元素
                        shop_name_elements = WebDriverWait(parent_container, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, './/android.view.View[@text]'))
                        )

                        # 遍历每个具有 text 的元素
                        for shop_name_element in shop_name_elements:
                            shop_name = shop_name_element.get_attribute('text').strip()

                            # 计算与目标店铺名称的相似度
                            similarity = SequenceMatcher(None, target_shop_name, shop_name).ratio()

                            # 将 shop_name_element 添加到匹配列表
                            matches.append((shop_name_element, similarity, shop_name, index))

                    except NoSuchElementException:
                        print(f"在店铺项 {index} 中未找到店铺名称元素")
                        continue

                # 如果找到匹配项，按相似度排序
                if matches:
                    matches.sort(key=lambda x: x[1], reverse=True)
                    best_match_item, best_similarity, shop_name, index = matches[0]

                    print(f"最匹配的店铺名称: {shop_name}, 相似度: {best_similarity}")

                    # 如果相似度超过阈值，则点击店铺名称元素
                    if best_similarity > 0.94:
                        best_match_item.click()  # 成功点击店铺

                        # 检查父容器是否已消失，最大等待5秒
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.invisibility_of_element_located((By.XPATH, '//android.view.View[contains(@resource-id, "pro_info_below_")]'))
                            )
                            print(f"成功点击最匹配的店铺: {shop_name}")
                            shop_found = True  # 设置为已找到
                            return True  # 成功找到并点击，返回 True
                        except TimeoutException:
                            print("父容器未消失，刷新页面重新查找店铺...")
                            refresh_page(driver)  # 调用页面刷新函数
                            continue  # 重新开始 while 循环

                    else:
                        print("未找到高相似度的店铺，尝试翻页...")
                        perform_page_scroll(driver)
                        attempts += 1
                else:
                    print("未找到任何店铺名称匹配")
                    perform_page_scroll(driver)
                    attempts += 1

            elif verify_elements:
                print("检测到 '验证'，进入等待循环")

                # 持续检查 "验证" 是否消失
                while True:
                    time.sleep(10)  # 等待10秒，避免频繁操作
                    try:
                        # 重新检测 "验证" 提示
                        verify_message = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "验证")]'))
                        )
                        if verify_message:
                            continue  # 如果仍然存在 "验证"，继续循环等待
                    except Exception:
                        print("检测到 '验证' 消失，继续执行后续操作")
                        break  # 退出循环，继续执行后面的代码

        except Exception as e:
            print(f"查找店铺时出错")
            refresh_page(driver)  # 刷新页面
            attempts += 1

    if not shop_found:
        print(f"经过 {max_attempts} 次尝试后仍未找到匹配的店铺")

        # 模拟按下返回键
        driver.press_keycode(AndroidKey.BACK)
        print("成功返回首页")

        # 提交任务
        submit_task_completion(driver, main_view)
        return False  # 未找到店铺，返回 False

# 获取任务
def perform_tasks(driver):
    while True:  # 无限循环
        try:
            # 获取任务
            while True:
                # 定位 dp-main 父容器
                try:
                    main_view = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
                    )
                    print("成功找到dp-main父容器")
                except Exception as e:
                    print(f"未找到dp-main父容器")

                # 在 dp-main 父容器下查找并点击 "回到首页" 按钮
                try:
                    home_button = WebDriverWait(main_view, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="回到首页"]'))
                    )
                    home_button.click()
                    print("成功点击'回到首页'按钮")
                except Exception as e:
                    print(f"点击'回到首页'按钮失败")

                # 在 dp-main 父容器下查找并点击 "获取任务" 按钮
                try:
                    time.sleep(3)
                    Get_Task = WebDriverWait(main_view, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="获取任务"]'))
                    )

                    Get_Task.click()
                    print("成功点击'获取任务'按钮")
                except Exception as e:
                    print(f"点击'获取任务'按钮失败")

                # 查找是否存在 "任务不合格" 或 "暂无任务" 或 "提交已限额"
                try:
                    time.sleep(5)
                    # 查找 "任务不合格" 或 "暂无任务" 或 "提交已限额"
                    message_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "任务不合格") or contains(@text, "提交已限额") or contains(@text, "已轮休") or contains(@text, "任务已暂停") or contains(@text, "暂无任务")]'))
                    )
                    # 如果找到 "任务不合格" 或 "暂无任务" 或 "提交已限额"，结束程序
                    text = message_button.text
                    if "任务不合格" in text:
                        print("任务不合格")
                        exit()  # 终止程序
                    elif "提交已限额" in text:
                        print("检测到 '提交已限额'，程序结束。")
                        exit()  # 终止脚本执行
                    elif "已轮休" in text:
                        print("检测到 '已轮休'，程序结束。")
                        exit()  # 终止脚本执行
                    elif "任务已暂停" in text:
                        print("检测到 '任务已暂停'，程序结束。")
                        exit()  # 终止脚本执行
                    elif "暂无任务" in text:
                        print("检测到 '暂无任务'，程序结束。")
                        exit()  # 终止脚本执行

                except Exception:
                    print("未检测到任务异常，继续任务。")

                # 查找并获取 dp-main 父容器下 "店铺名称"
                try:
                    shop_name_view = WebDriverWait(main_view, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/android.view.View[6]'))
                    )
                    target_shop_name = shop_name_view.text  # 获取店铺名称
                    print(f"成功找到店铺: {target_shop_name}")

                    # 如果店铺名称只有 "-"，重新获取任务
                    if target_shop_name == "-":
                        print("检测到店铺名称为 '-'，重新获取任务")
                        continue  # 重新开始 while 循环，跳过后续操作
                    else:
                        print("成功获取任务")
                        break  # 店铺名称不为 '-'，跳出循环，执行后续任务

                except Exception as e:
                    print(f"获取店铺名称失败")

            # 查找并点击包含 m_common_tip_x_0 的按钮
            try:
                # time.sleep(5)
                cancel_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "m_common_tip_x_0")]'))
                )
                cancel_button.click()
                print("成功点击包含 m_common_tip_x_0 的按钮")
            except Exception as e:
                print("未找到包含 m_common_tip_x_0 的按钮")

            # 在搜索栏搜索店铺名称
            try:
                time.sleep(3)
                keyword_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "msKeyWord")]'))
                )
                keyword_button.click()
                print("成功点击包含 msKeyWord 的搜索栏")
                keyword_button.send_keys(target_shop_name)
                print(f"成功输入店铺名称: {target_shop_name}")
                time.sleep(1)
                driver.press_keycode(AndroidKey.ENTER)

            except Exception as e:
                print(f"未找到包含 msKeyWord 的搜索栏")

            # 调用查找店铺的函数
            if not find_and_click_shop(driver, target_shop_name, main_view):
                print("未找到店铺，重新执行任务")
                perform_tasks()  # 如果未找到店铺，重新执行任务
                return  # 确保函数不继续执行
            else:
                # 进入店铺后，浏览商品
                browse_items()  # 成功点击店铺后调用浏览商品函数

        except Exception as e:
            print(f"执行任务时出现问题")

            # 暂停一段时间
            time.sleep(5)

# 浏览商品
def browse_items():
    time.sleep(5)
    second_item_found = True

    while True:
        # 定位 dp-main 父容器
        try:
            main_view = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
            )
            print("成功找到dp-main父容器")
        except Exception as e:
            print("未找到dp-main父容器，继续尝试...")
            refresh_page(driver)
            continue  # 未找到 dp-main，重新进入 while 循环

        # 在 dp-main 容器下查找第一行商品
        try:
            first_item = WebDriverWait(main_view, 10).until(
                EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[1]'))
            )
            print("成功找到第一行商品")
            break  # 找到第一行商品，退出 while 循环
        except Exception as e:
            print("未找到第一行商品，继续尝试...")
            refresh_page(driver)
            continue  # 未找到第一行商品，重新进入 while 循环

    # 在 dp-main 容器下查找第二行商品，如果没有找到则标记
    try:
        second_item = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[2]'))
        )
        print("成功找到第二行商品")
    except Exception as e:
        print(f"未找到第二行商品")
        second_item_found = False  # 没有找到第二行商品，设置标记

    while True:  # 无限循环，直到第一行商品完成
        time.sleep(10)
        # 在第一行商品下查找 "详情" 按钮
        try:
            details_button = WebDriverWait(first_item, 5).until(
                EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "详情")]'))
            )
            details_button.click()
            print("成功点击第一行商品的 '详情' 按钮")
        except Exception as e:
            print("未找到第一行商品的 '详情' 按钮")
            refresh_page(driver)
            continue

        # 点击 "详情" 后，检查是否有 "活动太火爆啦" 或 "验证"
        try:
            # 使用 WebDriverWait 检查是否存在 "活动太火爆啦" 或 "验证" 提示
            time.sleep(5)
            message_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[contains(@text, "活动太火爆啦") or contains(@text, "验证")]'))
            )

            # 检查文本内容
            message_text = message_element.text

            # 如果第一次检查到 "活动太火爆啦"
            if "活动太火爆啦" in message_text:
                print("检测到 '活动太火爆啦'，进入等待循环")

                # 持续检查 "活动太火爆啦" 是否消失
                while True:
                    time.sleep(10)  # 等待10秒，避免频繁操作
                    try:
                        # 重新检测 "活动太火爆啦" 提示
                        over_activity_message = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "活动太火爆啦")]'))
                        )

                        if over_activity_message:
                            continue  # 如果仍然存在 "活动太火爆啦"，继续循环等待
                    except Exception:
                        print("检测到 '活动太火爆啦' 消失，准备返回并执行后续操作")
                        break  # 退出循环，继续执行后面的代码

                # 提示消失后，执行返回操作
                time.sleep(5)  # 等待5秒，确保返回操作完成
                submit_task_completion(driver, main_view)  # 提交任务完成的状态
                exit()  # 终止程序

            # 如果第一次检查到 "验证"
            elif "验证" in message_text:
                print("检测到 '验证'，进入等待循环")

                # 持续检查 "验证" 是否消失
                while True:
                    time.sleep(10)  # 等待10秒，避免频繁操作
                    try:
                        # 重新检测 "验证" 提示
                        verify_message = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "验证")]'))
                        )

                        if verify_message:
                            continue  # 如果仍然存在 "验证"，继续循环等待
                    except Exception:
                        print("检测到 '验证' 消失，继续执行后续操作")
                        break  # 退出循环，继续执行后面的代码

        except Exception as e:
            print("未检测到 '活动太火爆啦' 或 '验证'，继续执行后续操作")

        # 提交第一行商品任务，更新任务完成标志
        first_item_completed = submit_first_item_task(main_view, first_item)

        # 如果返回 False，表示任务失败，退出循环
        if not first_item_completed:
            print("第一行商品任务失败，退出循环")
            break

        # 如果第一行商品完成且没有第二行商品，退出循环
        if first_item_completed and not second_item_found:
            print("第一行商品已完成且没有找到第二行商品，退出循环")
            break

        # 检查第二行商品是否 "已完成"
        second_item_completed = False
        try:
            WebDriverWait(second_item, 5).until(
                EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "已完成")]'))
            )
            print("'已完成'第二行商品任务")
            second_item_completed = True
        except Exception:
            second_item_text = second_item.text if second_item else "未能获取文本"
            print(f"'未完成'第二行商品任务")

        # 如果两行商品都完成了，截图并退出循环
        if first_item_completed and second_item_completed:
            print("所有商品任务均已完成")
            break  # 退出循环

        # 模拟按下返回键
        driver.press_keycode(AndroidKey.BACK)
        print("成功返回店铺")

    # 提交任务
    submit_task_completion(driver, main_view)

# 默认配置参数
default_desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': '01-13883122290',
    'udid': 'emulator-5556',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    'noReset': True,  # 不重置应用
}

# 检查命令行参数，是否传入 desired_caps
if len(sys.argv) > 1:
    try:
        desired_caps = json.loads(sys.argv[1])  # 从命令行参数中解析 JSON 字符串
    except json.JSONDecodeError:
        print("所提供的 desired capabilities 格式无效，请检查 JSON 格式是否正确。")
        sys.exit(1)
else:
    # 使用默认的配置参数
    print("未提供命令行参数，使用默认的设备配置。")
    desired_caps = default_desired_caps

# 启动 Appium 驱动
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 调用刷新页面和执行任务函数
refresh_page(driver)
perform_tasks(driver)
