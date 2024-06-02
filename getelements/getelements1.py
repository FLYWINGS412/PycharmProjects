import re
import os
import time
import subprocess
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

def filter_elements(elements, attribute_type):
    """
    过滤不需要的元素，返回符合条件的元素列表和它们的索引列表。
    :param elements: 查找到的元素列表
    :param attribute_type: 元素属性类型（如class、resource-id等）
    :return: 符合条件的元素列表和索引列表
    """
    filtered_elements = []
    filtered_indices = []
    for index, element in enumerate(elements, start=1):
        try:
            location = element.location
            size = element.size
            class_name = element.get_attribute("class")  # 获取元素的类名

            if (location['x'] == 0 and location['y'] == 0) or (size['width'] > 100 or size['height'] > 100) or class_name in ["android.view.View", "android.widget.Image"]:
                continue

            if attribute_type == "class":
                attribute_value = class_name
            elif attribute_type == "xpath":
                attribute_value = element.get_attribute("text") if element.get_attribute("text") else "N/A"
            else:
                attribute_value = element.get_attribute(attribute_type)
                if attribute_value is None:
                    attribute_value = "Not available"

            filtered_elements.append((index, element, attribute_value, location, size))
            filtered_indices.append(index)
        except StaleElementReferenceException:
            continue
    return filtered_elements, filtered_indices

def print_elements_info(filtered_elements):
    """
    打印符合条件的元素信息。
    :param filtered_elements: 符合条件的元素列表
    """
    print(f"{'index':<6}{'element':<50}{'coordinate':<15}{'size':<15}{'time':<8}")
    for index, element, attribute_value, location, size in filtered_elements:
        coord_format = f"[{location['x']:>3},{location['y']:>3}]"
        size_format = f"[{size['width']:>3},{size['height']:>3}]"
        if attribute_value is None:
            attribute_value = "None"
        print(f"{index:<6}{attribute_value[:50]:<50}{coord_format:<15}{size_format:<15}{0.00:.2f}")

def get_elements_by_type(driver, attribute_type):
    """
    根据指定的属性类型查找元素，并打印它们的信息。
    :param driver: WebDriver对象
    :param attribute_type: 元素属性类型（如class、resource-id等）
    """
    try:
        elements = driver.find_elements(By.XPATH, "//*")
        filtered_elements, filtered_indices = filter_elements(elements, attribute_type)
        if not filtered_elements:
            print("没有找到任何元素。")
            return
        print(f"获取到元素数量: {len(filtered_elements)} (时间: {time.time():.2f})")
        print_elements_info(filtered_elements)
    except WebDriverException as e:
        print(f"在查找元素过程中发生错误: {e}")

def take_screenshot(driver):
    """
    截取当前屏幕，并将截图保存到指定路径。
    :param driver: WebDriver对象
    """
    screenshot_path = "E:\\桌面"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_file = os.path.join(screenshot_path, f"screenshot_{timestamp}.png")
    driver.save_screenshot(screenshot_file)
    print(f"截图已保存到: {screenshot_file}")

def get_current_activity_adb():
    """
    使用 adb 命令获取当前活动的 Activity 名称。
    """
    try:
        result = subprocess.run(["adb", "shell", "dumpsys", "window", "windows"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if 'u0' in line and '/' in line:
                match = re.search(r'([^\s/]+)/([^\s/]+)}', line)
                if match:
                    package_name = match.group(1)
                    activity_name = match.group(2)
                    return f"当前页面名: {package_name}.{activity_name}"
        return "未找到当前焦点的 Activity。"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"

def main_menu(driver):
    """
    显示主菜单并处理用户选择的操作。
    """
    while True:
        print("选择要检测的元素类型:")
        print("1: Class    2: Resource-ID    3: Text    4: Content-Desc    5: XPath    6: 页面名    7: 截图    8: 退出")
        choice = input("请输入选项 (1-8)：")
        if choice == '8':
            print("退出程序。")
            break
        elif choice == '7':
            take_screenshot(driver)
        elif choice == '6':
            activity_name = get_current_activity_adb()
            print(activity_name)
        else:
            attribute_map = {
                '1': "class",
                '2': "resource-id",
                '3': "text",
                '4': "content-desc",
                '5': "xpath"
            }
            attribute_type = attribute_map.get(choice)
            if not attribute_type:
                print("选择无效，请重新输入。")
            else:
                get_elements_by_type(driver, attribute_type)

# 设置Desired Capabilities
desired_caps = {
    "platformName": "Android",
    "platformVersion": "12",
    "deviceName": "localhost:7555 device",
    "noReset": True,
    'settings[waitForIdleTimeout]': 10,  # 设置waitForIdleTimeout为50ms
    'settings[waitForSelectorTimeout]': 10,  # 设置waitForSelectorTimeout为50ms
    'newCommandTimeout': 300  # 设置新的命令超时时间为300秒
}

driver = None
try:
    # 启动WebDriver
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    main_menu(driver)
except WebDriverException as e:
    print(f"无法启动WebDriver: {e}")
finally:
    if driver:
        driver.quit()
