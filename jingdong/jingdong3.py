import os
import time
import difflib
from appium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 定义函数，获取截图编号
def get_screenshot_number(folder_path, current_date):
    screenshot_number = 1
    if os.path.exists(folder_path):
        existing_files = [f for f in os.listdir(folder_path) if f.startswith(current_date) and f.endswith(".png")]
        if existing_files:
            existing_files.sort()
            last_file = existing_files[-1]
            last_number = int(last_file.split('-')[-1].split('.')[0])
            screenshot_number = last_number + 1
    return screenshot_number

# 定义函数，截图并保存
def take_screenshot_with_date(driver, folder_path):
    current_date = datetime.now().strftime("%Y%m%d")

    # 获取或创建目录
    screenshot_folder = os.path.join(folder_path, 'screenshot', current_date)
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    # 生成文件名并保存截图
    screenshot_number = get_screenshot_number(screenshot_folder, current_date)
    screenshot_filename = f"{current_date}-{screenshot_number}.png"
    screenshot_path = os.path.join(screenshot_folder, screenshot_filename)
    driver.save_screenshot(screenshot_path)
    print(f"截图保存为: {screenshot_path}")

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
        TouchAction(driver).press(x=start_x, y=start_y).wait(1000).move_to(x=start_x, y=end_y).release().perform()
        print("成功模拟全屏向上翻页动作")
    except Exception as e:
        print(f"全屏翻页失败: {e}")

def find_and_click_shop(driver, shop_name, max_attempts=5):
    attempts = 0
    shop_found = False
    shop_main_part = shop_name[:3]  # 获取店铺名称的前三个字

    while attempts < max_attempts and not shop_found:
        try:
            time.sleep(5)

            # 重新获取所有 TextView 元素，避免 StaleElementReferenceException
            text_views = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'android.widget.TextView'))
            )

            matches = []

            # 遍历所有找到的 TextView 元素，计算与目标文本的相似度，并匹配至少连续3个字
            for element in text_views:
                current_text = element.text
                if current_text:
                    # 优先匹配店铺名称的前三个字，确保它是店铺而非商品
                    if shop_main_part in current_text and ('旗舰店' in current_text or '专营店' in current_text or '自营' in current_text):
                        similarity = difflib.SequenceMatcher(None, shop_main_part, current_text[:len(shop_main_part)]).ratio()
                        matches.append((element, similarity))

            # 按相似度排序，匹配度最高的排在前面
            matches = sorted(matches, key=lambda x: x[1], reverse=True)

            # 如果找到足够的匹配元素，点击第二个匹配度最高的
            if len(matches) > 1:
                second_best_match = matches[1][0]
                print(f"点击了匹配度第二高的店铺，文本为: {second_best_match.text}")

                # 尝试使用 TouchAction 点击
                location = second_best_match.location
                size = second_best_match.size
                center_x = location['x'] + size['width'] // 2
                center_y = location['y'] + size['height'] // 2

                TouchAction(driver).tap(x=center_x, y=center_y).perform()
                print("使用 TouchAction 成功点击店铺")

                # 添加等待，确认页面跳转成功
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.ListView'))
                )
                shop_found = True
                break  # 成功点击后，立即退出循环
            else:
                print("未找到足够匹配的店铺，尝试翻页...")
                attempts += 1
                perform_page_scroll(driver)
                print(f"当前第 {attempts} 次翻页")

        except Exception as e:
            print(f"查找店铺或点击失败: {e}")
            break

    if not shop_found:
        print(f"经过 {max_attempts} 次翻页后仍未找到匹配的店铺，程序终止")

# 执行任务
def perform_tasks():
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
            time.sleep(5)
            home_button = main_view.find_element(By.XPATH, './/android.widget.Button[@text="回到首页"]')
            home_button.click()
            print("成功点击'回到首页'按钮")
        except Exception as e:
            print(f"点击'回到首页'按钮失败: {e}")

        # 在 dp-main 父容器下查找并点击 "获取任务" 按钮
        try:
            time.sleep(10)
            Get_Task = main_view.find_element(By.XPATH, './/android.widget.Button[@text="获取任务"]')
            Get_Task.click()
            print("成功点击'获取任务'按钮")
        except Exception as e:
            print(f"点击'获取任务'按钮失败: {e}")

        # 查找并获取 dp-main 父容器下 "店铺名称"
        try:
            time.sleep(10)
            shop_name_view = main_view.find_element(By.XPATH, './/android.widget.TextView[5]')
            shop_name = shop_name_view.text  # 获取店铺名称
            print(f"成功找到店铺名称，其文本值为: {shop_name}")
        except Exception as e:
            print(f"获取店铺名称失败: {e}")

        # 查找并点击包含 msCancelBtn 的按钮
        try:
            time.sleep(5)
            cancel_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(@resource-id, "msCancelBtn")]'))
            )
            cancel_button.click()
            print("成功点击包含 msCancelBtn 的按钮")
        except Exception as e:
            print("未找到包含 msCancelBtn 的按钮")

        # 在搜索栏搜索店铺名称
        try:
            time.sleep(5)
            keyword_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[contains(@resource-id, "msKeyWord")]'))
            )
            keyword_button.click()
            print("成功点击包含 msKeyWord 的搜索栏")
            keyword_button.send_keys(shop_name)
            print(f"成功输入店铺名称: {shop_name}")
            time.sleep(5)
            driver.press_keycode(AndroidKey.ENTER)

            # 调用查找店铺的函数
            time.sleep(10)
            find_and_click_shop(driver, shop_name)
        except Exception as e:
            print(f"未找到包含 msKeyWord 的搜索栏: {e}")

        # 调用查找店铺的函数
            find_and_click_shop(driver, shop_name)
        except Exception as e:
            print(f"未找到包含 msKeyWord 的搜索栏: {e}")

        # 进入店铺后，浏览商品
        browse_items()  # 确保进入店铺后不再执行搜索逻辑

    except Exception as e:
        print(f"执行任务时出现问题: {e}")

# 浏览商品
def browse_items():
    while True:
        try:
            # # 刷新页面
            # try:
            #     loading_state_button = WebDriverWait(driver, 10).until(
            #         EC.element_to_be_clickable((By.ID, 'com.mmbox.xbrowser.pro:id/btn_loading_state'))
            #     )
            #     loading_state_button.click()
            #     print("页面已刷新")
            # except Exception:
            #     print("刷新页面失败")

            # 定位 dp-main 父容器
            try:
                time.sleep(5)
                main_view = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
                )
                print("成功找到dp-main父容器")
            except Exception:
                print("未找到dp-main父容器")

            # 在 dp-main 容器下查找第一行商品
            try:
                first_item = WebDriverWait(main_view, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[1]'))
                )
                print("成功找到第一行商品")
            except Exception:
                print("未找到第一行商品")

            # 在 dp-main 容器下查找第二行商品
            try:
                second_item = WebDriverWait(main_view, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.ListView/android.view.View[2]'))
                )
                print("成功找到第二行商品")
            except Exception as e:
                print(f"未找到第二行商品: {e}")

            # # 在 dp-main 父容器下查找 "前往店铺" 按钮
            # try:
            #     time.sleep(5)
            #     shop_button = main_view.find_element(By.XPATH, './/android.widget.Button[@text="前往店铺"]')
            #     shop_button.click()
            #     print("成功点击'前往店铺'按钮")
            # except Exception:
            #     print("未找到'前往店铺'按钮")

            # 在第一行商品下查找 "详情" 按钮并点击
            try:
                time.sleep(5)
                detail_button = WebDriverWait(first_item, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.TextView[contains(@text, "详情")]'))
                )
                detail_button.click()
                print("成功点击第一行商品的'详情'按钮")
            except Exception as e:
                print(f"未找到第一行商品的'详情'按钮: {e}")

            # 在第一行商品下查找 "提交" 按钮并点击
            try:
                time.sleep(10)
                submit_button = WebDriverWait(first_item, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.TextView[@text="提交"]'))
                )  # 注意这里的括号关闭
                submit_button.click()  # 这一行要缩进到try块内部
                print("成功点击第一行商品的'提交'按钮")
            except Exception:
                print("未找到第一行商品的'提交'按钮")

            # 确定提交商品
            try:
                time.sleep(5)
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@text="确定"]'))
                )
                confirm_button.click()
                print("成功点击全屏的'确定'按钮")
            except Exception as e:
                print(f"未找到全屏的'确定'按钮: {e}")

            # 检查第一行商品是否 "已完成"
            first_item_completed = False
            try:
                time.sleep(5)
                WebDriverWait(first_item, 30).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.TextView[@text="已完成"]'))
                )
                print("'已完成'第一行商品任务")
                first_item_completed = True
            except Exception:
                print("'未完成'第一行商品任务")

            # 检查第二行商品是否 "已完成"
            second_item_completed = False
            try:
                WebDriverWait(second_item, 5).until(
                    EC.presence_of_element_located((By.XPATH, './/android.widget.TextView[@text="已完成"]'))
                )
                print("'已完成'第二行商品任务")
                second_item_completed = True
            except Exception:
                print("'未完成'第二行商品任务")

            # 如果两行商品都完成了，截图并退出循环
            if first_item_completed and second_item_completed:
                print("所有商品任务均已完成，退出循环并截图")
                take_screenshot_with_date(driver, os.getcwd())  # 调用截图函数

                # 查找并点击 "任务完成" 按钮
                try:
                    time.sleep(10)
                    Task_Completed = main_view.find_element(By.XPATH, './/android.widget.Button[@text="任务完成"]')
                    Task_Completed.click()
                    print("成功点击'任务完成'按钮")
                except Exception as e:
                    print(f"点击'任务完成'按钮失败: {e}")

                # 确定 "任务完成"
                try:
                    time.sleep(5)
                    confirm_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//android.widget.Button[@text="确定"]'))
                    )
                    confirm_button.click()
                    print("成功点击全屏的'确定'按钮")
                except Exception as e:
                    print(f"未找到全屏的'确定'按钮: {e}")

                break  # 退出循环

        except Exception as e:
            print(f"浏览商品出现问题: {e}")

        # 模拟按下返回键
        time.sleep(2)  # 等待页面加载稳定
        driver.press_keycode(AndroidKey.BACK)
        print("成功返回店铺")

        # 暂停一段时间
        time.sleep(5)

# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '12',
    'deviceName': 'MI 10',
    'udid': '192.168.0.213:38425',
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

# 刷新页面
try:
    loading_state_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'com.mmbox.xbrowser.pro:id/btn_loading_state'))
    )
    loading_state_button.click()
    print("页面已刷新")
    time.sleep(5)
except Exception:
    print("刷新页面失败")

# 调用执行任务函数
perform_tasks()
