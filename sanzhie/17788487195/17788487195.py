import json
import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support import expected_conditions as EC
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
    storage_file = 'close_buttons.json'

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
    screen_height = driver.height
    max_attempts = 20
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
        with ThreadPoolExecutor(max_workers=2) as executor:
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
                            if (15 < size['width'] < 80 and 15 < size['height'] < 80 and location['y'] < screen_height / 2):
                                found_elements.append(element)
                                # print("[DEBUG] 添加符合条件的元素到found_elements列表中")
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

    return found_elements

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
                # 随机等待 30 到 60 秒
                sleep_duration = random.randint(10, 30)
                print(f"[DEBUG] 成功匹配广告，等待 {sleep_duration} 秒")
                time.sleep(sleep_duration)

                selected_element = matched_elements[0]
                class_name = selected_element.get_attribute("class")
                size = selected_element.size
                location = selected_element.location
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
                    print("[DEBUG] 未匹配到任何存储的关闭按钮元素，重新查找一次...")
                    retry_count += 1
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
        'deviceName': '192.168.0.213:43359',
        'udid': '192.168.0.40:42635',
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
