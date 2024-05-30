import os
import time
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from appium.webdriver.common.touch_action import TouchAction

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

            # 过滤掉坐标为[0,0] 或宽度或高度大于100的元素 以及android.view.View和android.widget.Image元素
            if (location['x'] == 0 and location['y'] == 0) or (size['width'] > 100 or size['height'] > 100) or class_name in ["android.view.View", "android.widget.Image"]:
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
        print(f"{index:<6}{attribute_value[:50]:<50}{coord_format:<15}{size_format:<15}{0.00:.2f}")  # 此处的时间用0.00表示占位符

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
            elements = driver.find_elements(By.XPATH, attribute_value)
        else:
            elements = driver.find_elements(By.XPATH, f"//*[@{attribute_type}]")

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
    获取当前页面的活动名称。

    :param driver: WebDriver对象
    """
    try:
        activity = driver.current_activity
        print(f"当前页面名: {activity}")
    except WebDriverException as e:
        print(f"获取当前页面名时发生错误: {e}")

def main_menu(driver):
    """
    显示主菜单并处理用户选择的操作。

    :param driver: WebDriver对象
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
            get_current_activity(driver)
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
    "deviceName": "192.168.0.247:5555 device",
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
