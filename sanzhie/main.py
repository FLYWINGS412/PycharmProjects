import json
import time
import random
import threading
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.touch_action import TouchAction
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

# 用于存储正确的关闭按钮元素信息
stored_close_buttons = []

# 存储正确的关闭按钮元素信息到文件
def store_close_button_info(element):
    global stored_close_buttons
    button_info = {
        'size': element.size,
        'location': element.location,
        'class_name': element.get_attribute("class")
    }
    stored_close_buttons.append(button_info)
    storage_file = 'close_buttons.json'

    # 将存储的数据保存到 JSON 文件，按行写入
    with open(storage_file, 'w') as file:
        for button in stored_close_buttons:
            file.write(json.dumps(button) + '\n')

# 从文件中加载关闭按钮元素信息
def load_close_button_info():
    global stored_close_buttons
    storage_file = 'MI 10/close_buttons.json'

    stored_close_buttons = []  # 初始化为空列表

    try:
        with open(storage_file, 'r') as file:
            for line in file:
                if line.strip():  # 跳过空行
                    button_info = json.loads(line.strip())
                    stored_close_buttons.append(button_info)
    except FileNotFoundError:
        # 如果文件不存在，则继续使用空列表
        stored_close_buttons = []

# 匹配当前查找到的关闭按钮元素是否与存储的信息一致
def match_close_button(found_elements):
    global stored_close_buttons
    matched_elements = []
    for element in found_elements:
        for button_info in stored_close_buttons:
            if (
                    element.size == button_info['size'] and
                    element.location == button_info['location'] and
                    element.get_attribute("class") == button_info['class_name']
            ):
                matched_elements.append(element)
                break
    return matched_elements

# 查找关闭按钮
def find_close_button(driver):
    screen_height = driver.get_window_size()['height']  # 使用get_window_size获取屏幕高度
    max_attempts = 5
    attempts = 0
    found_elements = []
    skip_start_time = time.time()  # 记录“跳过”按钮首次检测到的时间

    # 循环查找“跳过”按钮，直到未找到为止
    while True:
        skip_elements = driver.find_elements(By.XPATH, "//android.widget.TextView[contains(@text, '跳过')]")
        if skip_elements:
            # 检测是否超过2分钟
            elapsed_time = time.time() - skip_start_time
            if elapsed_time > 120:  # 超过2分钟
                print(f"[DEBUG] 检测到'跳过'按钮超过2分钟，点击跳过...")
                skip_elements[0].click()  # 点击第一个“跳过”按钮
                break  # 退出循环
            else:
                # print(f"[DEBUG] '跳过'按钮存在，等待 {elapsed_time} 秒...")
                time.sleep(5)  # 等待5秒继续检查
                continue  # 继续查找“跳过”按钮
        else:
            # print("[DEBUG] 未检测到'跳过'按钮，继续查找其他元素...")
            time.sleep(5)
            break  # 退出查找“跳过”按钮的循环

    # 查找其他关闭按钮元素
    while attempts < max_attempts:
        # print(f"[DEBUG] 尝试次数: {attempts + 1}/{max_attempts}")
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = []

            # 只查找 `android.widget.ImageView` 元素
            futures.append(executor.submit(
                lambda: WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "android.widget.ImageView"))
                )
            ))

            for future in as_completed(futures):
                try:
                    elements = future.result()
                    # print(f"[DEBUG] 找到的元素数量: {len(elements)}")
                    for element in elements:
                        try:
                            size = element.size
                            location = element.location
                            class_name = element.get_attribute("class")
                            # print(f"[DEBUG] 检查元素: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")

                            # 筛选符合条件的元素
                            if (15 < size['width'] < 90 and 15 < size['height'] < 90 and location['y'] < screen_height / 2):
                                # 手动排除一些不需要的元素
                                class_name = element.get_attribute("class")

                                # 手动排除指定元素
                                if (
                                    (class_name == "android.widget.ImageView" and size['height'] == 69 and size['width'] == 69 and location['x'] == 69 and location['y'] == 804) or
                                    (class_name == "android.widget.ImageView" and size['height'] == 69 and size['width'] == 69 and location['x'] == 69 and location['y'] == 955) or
                                    (class_name == "android.widget.ImageView" and size['height'] == 69 and size['width'] == 69 and location['x'] == 69 and location['y'] == 1106)
                                ):
                                    # print(f"[DEBUG] 排除指定元素: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")
                                    continue  # 跳过这两个元素

                                # 如果元素符合条件，且不被排除，添加到列表中
                                found_elements.append(element)
                                # print(f"[DEBUG] 添加符合条件的元素: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")
                        except StaleElementReferenceException:
                            # print("[DEBUG] 元素已失效，跳过...")
                            continue
                except (NoSuchElementException, TimeoutException):
                    # print("[DEBUG] 查找元素时发生异常")
                    continue

        if found_elements:
            # print(f"[DEBUG] 找到符合条件的元素: {found_elements}")
            break

        attempts += 1  # 确保每次循环都增加 attempts

    # 如果超过最大尝试次数未找到符合条件的元素，重新查找
    if not found_elements and attempts >= max_attempts:
        print(f"[DEBUG] 未找到符合条件的元素，重新尝试查找...")
        time.sleep(5)  # 等待5秒再重新查找
        return find_close_button(driver)  # 递归调用，重新开始查找

    return found_elements

# 查看广告详情
def view_details(driver):
    def find_element_by_text(text):
        # 查找包含指定文本的TextView元素
        return driver.find_elements(By.XPATH, f"//android.widget.TextView[contains(@text, '{text}')]")

    # 并行查找关键字
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(find_element_by_text, "立即安装"): "立即安装",
            executor.submit(find_element_by_text, "立即打开"): "立即打开",
            executor.submit(find_element_by_text, "支付宝"): "支付宝",
            executor.submit(find_element_by_text, "拼多多"): "拼多多",
            executor.submit(find_element_by_text, "抖音"): "抖音",
            executor.submit(find_element_by_text, "快手"): "快手",
            executor.submit(find_element_by_text, "百度"): "百度",
            executor.submit(find_element_by_text, "好看"): "好看",
            executor.submit(find_element_by_text, "善意"): "善意",
            executor.submit(find_element_by_text, "应用商店"): "应用商店"
        }

        # 等待结果
        for future in as_completed(futures):
            platform = futures[future]
            try:
                elements = future.result()
                if elements:
                    print(f"[DEBUG] 检测到'{platform}'元素，跳过查看详情。")
                    return  # 直接返回，不执行后续代码
            except Exception as e:
                print(f"[DEBUG] 查找'{platform}'元素时发生错误: {e}")

    # 获取屏幕的宽度和高度
    screen_width = driver.get_window_size()['width']
    screen_height = driver.get_window_size()['height']

    # 计算x轴和y轴的随机位置
    x = random.randint(screen_width // 4, 3 * screen_width // 4)
    y = random.randint(3 * screen_height // 5, 4 * screen_height // 5)
    # print(f"[DEBUG] 随机点击位置: x={x}, y={y}")

    # 使用TouchAction来点击该位置
    try:
        action = TouchAction(driver)
        action.tap(x=x, y=y).perform()
        print("[DEBUG] 点击查看详情")
    except Exception as e:
        print(f"[DEBUG] 点击时发生错误: {e}")

    # 随机等待10到20秒后返回
    sleep_time = random.randint(10, 20)
    print(f"[DEBUG] 等待 {sleep_time} 秒后返回广告页")
    time.sleep(sleep_time)

    # 模拟返回键
    try:
        driver.press_keycode(AndroidKey.BACK)
        # print("[DEBUG] 成功按下返回键")
        time.sleep(random.randint(2, 5))
    except Exception as e:
        print(f"[DEBUG] 返回时发生错误: {e}")

    # 查找是否出现“离开”按钮
    try:
        leave_elements = driver.find_elements(By.XPATH, "//android.widget.TextView[contains(@text, '离开')]")
        if leave_elements:
            print("[DEBUG] 检测到'离开'按钮，点击离开")
            leave_elements[0].click()  # 点击第一个“离开”按钮
    except Exception as e:
        print(f"[DEBUG] 查找或点击'离开'按钮时发生错误: {e}")

# 点击关闭按钮
def click_close_button(driver):
    retry_count = 0  # 用于记录未匹配到存储元素时的重试次数

    while True:
        try:
            found_elements = find_close_button(driver)
            if not found_elements:
                print("[DEBUG] 未找到任何符合条件的关闭按钮元素。")
                time.sleep(2)  # 等待2秒再试
                continue  # 继续循环，重新查找

            matched_elements = match_close_button(found_elements)
            print(f"[DEBUG] 匹配到的存储元素数量: {len(matched_elements)}")

            if len(matched_elements) == 1:
                # 随机等待一些时间
                sleep_duration = random.randint(5, 15)
                print(f"[DEBUG] 成功匹配广告，等待 {sleep_duration} 秒")
                time.sleep(sleep_duration)

                selected_element = matched_elements[0]
                class_name = selected_element.get_attribute("class")
                size = selected_element.size
                location = selected_element.location
                view_details(driver)
                selected_element.click()
                print(f"[DEBUG] 已点击: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")

            elif len(matched_elements) > 1:
                print("[DEBUG] 匹配到多个关闭按钮元素，请选择一个：")
                for i, element in enumerate(matched_elements, start=1):
                    size = element.size
                    location = element.location
                    class_name = element.get_attribute("class")
                    print(f"{i}: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")

                user_input = input("请选择要点击的元素序号（按回车键重新查找）：")
                if user_input.strip() == "":
                    print("[DEBUG] 重新查找关闭按钮元素...")
                    retry_count = 0  # 重置重试计数器
                    continue  # 如果用户按回车键，则重新进入循环，查找关闭按钮元素

                index = int(user_input)
                if 1 <= index <= len(matched_elements):
                    selected_element = matched_elements[index - 1]
                    class_name = selected_element.get_attribute("class")
                    size = selected_element.size
                    location = selected_element.location
                    selected_element.click()
                    print(f"[DEBUG] 已点击: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")
                else:
                    print("[DEBUG] 无效的选择，重新查找...")
                    continue
            else:
                if retry_count < 3:
                    retry_count += 1
                    print(f"[DEBUG] 未匹配到任何存储的关闭按钮元素，重试第 {retry_count} 次...")
                    time.sleep(2)  # 每次重试前等待
                    continue  # 重新查找一次

                else:
                    print("[DEBUG] 未匹配到任何存储的关闭按钮元素，请选择一个点击：")
                    for i, element in enumerate(found_elements, start=1):
                        size = element.size
                        location = element.location
                        class_name = element.get_attribute("class")
                        print(f"{i}: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")

                    user_input = input("请选择要点击的元素序号（按回车键重新查找）：")
                    if user_input.strip() == "":
                        print("[DEBUG] 重新查找关闭按钮元素...")
                        retry_count = 0  # 重置重试计数器
                        continue  # 如果用户按回车键，则重新进入循环，查找关闭按钮元素

                    index = int(user_input)
                    if 1 <= index <= len(found_elements):
                        selected_element = found_elements[index - 1]
                        class_name = selected_element.get_attribute("class")
                        size = selected_element.size
                        location = selected_element.location
                        store_close_button_info(selected_element)  # 存储新的关闭按钮信息
                        selected_element.click()
                        print(f"[DEBUG] 已点击: [元素名: {class_name}, 大小: {size}, 坐标: {location}]")
                    else:
                        print("[DEBUG] 无效的选择，重新查找...")
                        continue

        except Exception as e:
            # print(f"[DEBUG] 发生异常: {e}")
            time.sleep(2)  # 遇到错误时，等待一段时间再继续

def main():
    # 驱动参数
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '13',
        'deviceName': 'MI 10',
        'udid': '192.168.0.40:40509',
        # 'appPackage': 'com.guokun.darenzhushou',
        # 'appActivity': 'com.example.advertisinglibrary.activity.MainActivity',
        'automationName': 'UiAutomator2',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'ignoreHiddenApiPolicyError': True,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    driver.wait = WebDriverWait(driver, 10)
    size = driver.get_window_size()
    driver.width = size['width']
    driver.height = size['height']

    load_close_button_info()
    click_close_button(driver)

if __name__ == "__main__":
    main()
