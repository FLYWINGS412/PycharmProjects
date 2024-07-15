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
            class_name = element.get_attribute("class")

            # 过滤掉坐标为[0,0] 或宽度或高度大于40的元素 以及android.view.View和android.widget.Image元素
            # if (location['x'] == 0 and location['y'] == 0) or (size['width'] > 100 or size['height'] > 100) or class_name in ["android.view.View", "android.widget.Image"]:
            if (location['x'] == 0 and location['y'] == 0) or class_name in ["android.view.View", "android.widget.Image"]:
                continue

            if attribute_type == "xpath":
                attribute_value = element.get_attribute("outerHTML")
            else:
                attribute_value = element.get_attribute(attribute_type)

            filtered_elements.append((index, element, attribute_value, location, size))
            filtered_indices.append(index)
        except StaleElementReferenceException:
            # 跳过失效的元素
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
        print(f"{index:<6}{attribute_value[:50]:<50}{coord_format:<15}{size_format:<15}{0.00:.2f}")

def get_elements_by_type(driver, attribute_type):
    """
    根据指定的属性类型查找元素，并打印它们的信息。

    :param driver: WebDriver对象
    :param attribute_type: 元素属性类型（如class、resource-id等）
    """
    try:
        if attribute_type == "xpath":
            attribute_value = input("请输入XPath表达式：")
            if attribute_value.strip() == "":
                return  # 直接返回菜单
            elements = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located((By.XPATH, attribute_value)))
        else:
            elements = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located((By.XPATH, f"//*[@{attribute_type}]")))

        filtered_elements, filtered_indices = filter_elements(elements, attribute_type)
        print(f"获取到元素数量: {len(filtered_elements)} (时间: {time.time():.2f})")

        print_elements_info(filtered_elements)

        # 获取用户输入的要点击的元素索引
        input_indices = input("请输入要点击的元素索引：")
        if input_indices.strip() == "":
            return  # 直接返回菜单

        indices = [int(i.strip()) for i in input_indices.split(',')]

        for idx in indices:
            if idx in filtered_indices:
                element_to_click = filtered_elements[filtered_indices.index(idx)][1]
                location = element_to_click.location
                size = element_to_click.size
                x_position = location['x'] + size['width'] / 2
                y_position = location['y'] + size['height'] / 2
                TouchAction(driver).tap(x=x_position, y=y_position).perform()
                print(f"已点击元素索引: {idx}")
            else:
                print(f"索引 {idx} 超出范围")

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

def get_current_activity(driver):
    """
    选择使用 adb 命令或 driver.current_activity 获取当前活动的 Activity 名称。
    """
    print("选择获取当前活动页面的方式:")
    print("1: 使用 ADB 命令    2: 使用 driver.current_activity")
    choice = input("请输入选项 (1-2)：")

    if choice == '1':
        return get_current_activity_adb()
    elif choice == '2':
        try:
            current_activity = driver.current_activity
            return f"当前页面: {current_activity}"
        except WebDriverException as e:
            return f"获取当前活动页面时发生错误: {e}"
    else:
        return "无效的选择。"

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
                    return f"当前页面名: {activity_name}"
        return "未找到当前焦点的 Activity。"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取当前 Activity 时发生错误: {e}"

def get_device_resolution():
    """
    使用 adb 命令获取设备分辨率。
    """
    try:
        result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True)
        resolution_match = re.search(r'Physical size: (\d+x\d+)', result.stdout)
        if resolution_match:
            resolution = resolution_match.group(1)
            return f"设备分辨率: {resolution}"
        return "无法获取设备分辨率。"
    except subprocess.CalledProcessError as e:
        return f"执行 adb 命令时发生错误: {e}"
    except Exception as e:
        return f"获取设备分辨率时发生错误: {e}"

def get_all_contexts(driver):
    """
    获取所有可用的上下文并打印出来。

    :param driver: WebDriver对象
    """
    try:
        contexts = driver.contexts
        print("可用的上下文:")
        for context in contexts:
            print(context)
    except WebDriverException as e:
        print(f"获取上下文时发生错误: {e}")

def main_menu(driver):
    """
    显示主菜单并处理用户选择的操作。
    """
    while True:
        print("选择要检测的元素类型:")
        print("1: Class    2: Resource-ID    3: Text    4: Content-Desc    5: XPath    6: 页面名    7: 截图    8: 分辨率    9: 所有上下文    10: 退出")
        choice = input("请输入选项 (1-10)：")
        if choice == '10':
            print("退出程序。")
            break
        elif choice == '9':
            get_all_contexts(driver)
        elif choice == '8':
            resolution = get_device_resolution()
            print(resolution)
        elif choice == '7':
            take_screenshot(driver)
        elif choice == '6':
            activity_name = get_current_activity(driver)
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
    'platformName': 'Android',
    'platformVersion': '9',
    # 'deviceName': device_name,
    'udid': '8RYBB18404152438',
    # 'appPackage': 'com.xiangshi.bjxsgc',
    # 'appActivity': 'com.xiangshi.bjxsgc.activity.LauncherActivity',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'unicodeKeyboard': True,
    'resetKeyboard': True,
    'noReset': True
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
