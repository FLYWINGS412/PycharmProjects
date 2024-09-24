import re
import os
import time
from appium import webdriver
from datetime import datetime
from difflib import SequenceMatcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 刷新页面
def refresh_page(driver):
    try:
        loading_state_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.mmbox.xbrowser:id/btn_loading_state'))
        )
        loading_state_button.click()
        print("页面已刷新")
        time.sleep(5)  # 等待页面加载完成
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

# 提交任务
def submit_task_completion(driver, main_view):
    # 查找并点击 "任务完成" 按钮
    try:
        time.sleep(3)
        Task_Completed = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="任务完成"]'))
        )
        Task_Completed.click()
        print("成功点击'任务完成'按钮")
    except Exception as e:
        print(f"点击'任务完成'按钮失败")

    # 确定 "任务完成"
    try:
        # time.sleep(5)
        confirm_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@text="确定"]'))
        )
        confirm_button.click()
        print("成功点击全屏的'确定'按钮")
        time.sleep(5)
    except Exception as e:
        print(f"未找到全屏的'确定'按钮")

# 查找商店
def find_and_click_shop(driver, target_shop_name, main_view, max_attempts=5):
    attempts = 0
    shop_found = False

    while attempts < max_attempts and not shop_found:
        try:
            time.sleep(5)
            # 获取父容器，包含所有店铺项的列表
            parent_containers = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//android.view.View[contains(@resource-id, "pro_info_below_")]')
                )
            )

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

                        # # 打印店铺名称
                        # print(f"找到店铺名称: {shop_name}")

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
                if best_similarity > 0.91:
                    best_match_item.click()  # 成功点击店铺
                    print(f"成功点击最匹配的店铺: {shop_name}")
                    shop_found = True  # 设置为已找到
                    return True  # 成功找到并点击，返回 True
                else:
                    print("未找到高相似度的店铺，尝试翻页...")
                    perform_page_scroll(driver)
                    attempts += 1
            else:
                print("未找到任何店铺名称匹配")
                perform_page_scroll(driver)
                attempts += 1

        except Exception as e:
            print(f"查找店铺时出错")
            attempts += 1

    if not shop_found:
        print(f"经过 {max_attempts} 次尝试后仍未找到匹配的店铺")

        # 模拟按下返回键
        driver.press_keycode(AndroidKey.BACK)
        print("成功返回首页")

        # 提交任务
        submit_task_completion(driver, main_view)
        return False  # 未找到店铺，返回 False

# 执行任务
def perform_tasks():
    while True:  # 无限循环
        try:
            # 定位 dp-main 父容器
            try:
                main_view = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
                )
                print("成功找到dp-main父容器")
            except Exception as e:
                print(f"未找到dp-main父容器: {e}")

            # 在 dp-main 父容器下查找并点击 "回到首页" 按钮
            try:
                home_button = WebDriverWait(main_view, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="回到首页"]'))
                )
                home_button.click()
                print("成功点击'回到首页'按钮")
            except Exception as e:
                print(f"点击'回到首页'按钮失败: {e}")

            # 获取任务
            while True:
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

                # 查找是否存在 "明日再试" 或 "暂无任务" 或 "任务已达限额"
                try:
                    # time.sleep(5)
                    # 查找 "明日再试" 或 "暂无任务" 或 "任务已达限额"
                    message_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "明日再试") or contains(@text, "暂无任务") or contains(@text, "任务已达限额")]'))
                    )
                    # 如果找到 "明日再试" 或 "暂无任务" 或 "任务已达限额"，结束程序
                    text = message_button.text
                    if "明日再试" in text:
                        print("检测到 '明日再试' ，程序结束。")
                    elif "暂无任务" in text:
                        print("检测到 '暂无任务'，程序结束。")
                    elif "任务已达限额" in text:
                        print("检测到 '任务已达限额'，程序结束。")

                    driver.quit()  # 结束程序运行
                    exit()  # 终止脚本执行

                except Exception:
                    print("未检测到 '明日再试' 或 '暂无任务' 或 '任务已达限额'，继续任务。")

                # 查找并获取 dp-main 父容器下 "店铺名称"
                try:
                    shop_name_view = WebDriverWait(main_view, 10).until(
                        EC.presence_of_element_located((By.XPATH, './/android.view.View[6]'))
                    )
                    target_shop_name = shop_name_view.text  # 获取店铺名称
                    print(f"成功找到店铺: {target_shop_name}")

                    # 如果店铺名称包含 "-"，重新获取任务
                    if "-" in target_shop_name:
                        print("检测到店铺名称包含 '-'，重新获取任务")
                        continue  # 重新开始 while 循环，跳过后续操作
                    else:
                        print("成功获取任务")
                        break  # 店铺名称不包含 '-'，跳出循环，执行后续任务
                except Exception as e:
                    print(f"获取店铺名称失败，异常: {e}")
                    break  # 如果获取店铺名称失败，退出循环

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

                # 调用查找店铺的函数
                if not find_and_click_shop(driver, target_shop_name, main_view):
                    print("未找到店铺，重新执行任务")
                    perform_tasks()  # 如果未找到店铺，重新执行任务
                    return  # 确保函数不继续执行
                else:
                    # 进入店铺后，浏览商品
                    browse_items()  # 成功点击店铺后调用浏览商品函数

            except Exception as e:
                print(f"未找到包含 msKeyWord 的搜索栏: {e}")

        except Exception as e:
            print(f"执行任务时出现问题: {e}")

            # 暂停一段时间
            time.sleep(5)

# 浏览商品
def browse_items():
    time.sleep(5)
    task_mismatch_detected = False  # 用于检测任务不匹配的标志

    # 定位 dp-main 父容器
    try:
        main_view = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
        )
        print("成功找到dp-main父容器")
    except Exception as e:
        print("未找到dp-main父容器")

    # 在 dp-main 容器下查找第一行商品
    try:
        first_item = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[1]'))
        )
        print("成功找到第一行商品")
    except Exception as e:
        print("未找到第一行商品")

    # 在 dp-main 容器下查找第二行商品，如果没有找到则标记
    second_item_found = True  # 预先将变量设置为 True
    try:
        second_item = WebDriverWait(main_view, 10).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[2]'))
        )
        print("成功找到第二行商品")
    except Exception as e:
        print(f"未找到第二行商品")
        second_item_found = False  # 没有找到第二行商品，设置标记

    while True:
        if task_mismatch_detected:
            break  # 退出最外层的循环

        try:
            # 在第一行商品下查找 "详情" 按钮并点击
            try:
                time.sleep(5)
                detail_button = WebDriverWait(first_item, 5).until(
                    EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "详情")]'))
                )
                detail_button.click()
                print("成功点击第一行商品的'详情'按钮")

                # 点击 "详情" 后，检查是否有 "活动太火爆啦"
                try:
                    time.sleep(3)
                    over_activity_message = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[contains(@text, "活动太火爆啦")]'))
                    )
                    if over_activity_message:
                        print("检测到 '活动太火爆啦'，准备返回并截图")
                        driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                        time.sleep(5)
                        take_screenshot_with_date(driver, os.getcwd())  # 截图操作
                        print("已返回并截图")
                        submit_task_completion(driver, main_view)
                        exit()  # 终止程序

                except Exception as e:
                    print("未检测到 '活动太火爆啦'，继续执行后续操作")

            except Exception as e:
                print(f"未找到第一行商品的'详情'按钮")

            # 在第一行商品下查找 "提交" 按钮并点击
            try:
                attempt = 0  # 初始化计数器
                max_attempts = 3  # 最大尝试次数

                while attempt < max_attempts:
                    try:
                        submit_button = WebDriverWait(first_item, 10).until(
                            EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "提交")]'))
                        )  # 注意这里的括号关闭
                        submit_button.click()  # 这一行要缩进到try块内部
                        print("成功点击第一行商品的'提交'按钮")
                        time.sleep(5)
                        break  # 找到并点击后，跳出循环
                    except Exception:
                        attempt += 1  # 增加计数器
                        print(f"未找到第一行商品的'提交'按钮，重试查找 ({attempt}/{max_attempts})")

                        if attempt < max_attempts:
                            # 刷新页面
                            refresh_page(driver)
                        else:
                            print("已达到最大尝试次数，停止查找 '提交' 按钮")
            except Exception as e:
                print(f"在第一行商品下查找 '提交' 按钮时出错")

            # 处理“提交”时的异常
            try:
                elements = WebDriverWait(driver, 10).until(
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

                        # 点击 "确定" 按钮后，界面可能发生变化，避免使用旧的元素
                        time.sleep(3)  # 等待可能的弹出窗口

                        # 点击 "确定" 按钮后再检查是否有 "任务不匹配"
                        new_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//android.widget.TextView | //android.widget.Button | //android.view.View'))
                        )

                        # 遍历新元素，检查是否有 "任务不匹配" 和 "确定"
                        for new_element in new_elements:
                            new_text = new_element.text

                            # 检查是否存在 "任务不匹配"
                            if "任务不匹配" in new_text:
                                print(f"检测到 '任务不匹配'，完整文本为: {new_text}")
                                driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                                task_mismatch_detected = True  # 设置标志以退出最外层循环
                                break  # 跳出当前循环

                            # 检查是否存在 "任务已过期"
                            elif "任务已过期" in new_text:
                                print("检测到 '任务已过期'，重新获取任务")
                                driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                                task_mismatch_detected = True  # 设置标志以退出最外层循环
                                break  # 跳出当前循环

                            # 检查是否存在 "BAD REQUEST"
                            elif "BAD REQUEST" in new_text:
                                print("检测到 'BAD REQUEST'，准备返回")
                                driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                                break  # 跳出当前循环

                        break  # 跳出 "确定提交商品" 检查循环

                    # 2. 检查是否存在 "活动太火爆啦"
                    elif "活动太火爆啦" in text:
                        print("检测到 '活动太火爆啦'，准备返回并截图")
                        driver.press_keycode(AndroidKey.BACK)  # 模拟返回操作
                        time.sleep(5)
                        take_screenshot_with_date(driver, os.getcwd())  # 截图操作
                        print("已返回并截图")
                        submit_task_completion(driver, main_view)
                        exit()  # 终止程序

                    # 3. 检查是否存在 "请检查您的账号状态"
                    elif "请检查您的账号状态" in text:
                        print("检测到 '请检查您的账号状态'，终止程序。")
                        exit()  # 终止程序

                if task_mismatch_detected:
                    break  # 跳出处理“提交”时的异常的 try 块

            except Exception as e:
                print(f"处理提交时出现异常: {e}")

            # 检查第一行商品是否 "已完成"
            first_item_completed = False
            try:
                # 循环检查5次
                max_attempts = 5
                attempt = 0
                first_item_completed = False

                while attempt < max_attempts:
                    try:
                        # time.sleep(5)
                        WebDriverWait(first_item, 3).until(
                            EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "已完成")]'))
                        )
                        print("'已完成'第一行商品任务")
                        first_item_completed = True
                        break  # 找到后跳出循环
                    except Exception:
                        attempt += 1
                        print(f"'未完成'第一行商品任务，重试第 {attempt} 次")

                if not first_item_completed:
                    print("超过最大尝试次数，第一行商品仍未完成")

            except Exception as e:
                print(f"检查第一行商品状态时出现错误")

            # 如果第一行商品完成且没有第二行商品，退出循环
            if first_item_completed and not second_item_found:
                print("第一行商品已完成且没有找到第二行商品，退出循环")
                take_screenshot_with_date(driver, os.getcwd())  # 调用截图函数
                break

            # 检查第二行商品是否 "已完成"
            second_item_completed = False
            try:
                WebDriverWait(second_item, 0).until(
                    EC.presence_of_element_located((By.XPATH, './/*[contains(@text, "已完成")]'))
                )
                print("'已完成'第二行商品任务")
                second_item_completed = True
            except Exception:
                print("'未完成'第二行商品任务")

            # 如果两行商品都完成了，截图并退出循环
            if first_item_completed and second_item_completed:
                print("所有商品任务均已完成，退出循环并截图")
                take_screenshot_with_date(driver, os.getcwd())  # 调用截图函数
                break  # 退出循环

            # 模拟按下返回键
            driver.press_keycode(AndroidKey.BACK)
            print("成功返回店铺")

        except Exception as e:
            print(f"浏览商品出现问题: {e}")

    # 提交任务
    submit_task_completion(driver, main_view)

# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': 'WY',
    'udid': 'emulator-5566',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    # 'unicodeKeyboard': False,
    # 'resetKeyboard': False,
    'noReset': True,  # 不重置应用
}

# 启动 Appium 驱动，不重新启动浏览器
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# 刷新页面
refresh_page(driver)

# 调用执行任务函数
perform_tasks()
