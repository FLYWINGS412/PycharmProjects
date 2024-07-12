import multiprocessing
import time
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

def setup_driver():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'udid': '8RYBB18404152438',
        'automationName': 'UiAutomator2',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }
    # 启动WebDriver
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver

def find_elements_process(by, value, output_queue):
    driver = setup_driver()  # 在每个进程中单独创建WebDriver实例
    try:
        elements = driver.find_elements(by, value)
        output_queue.put(elements)  # 将查找到的元素放入队列
    except Exception as e:
        output_queue.put([])  # 发生错误时返回空列表
        print(f"查找元素过程中发生错误：{e}")
    finally:
        driver.quit()  # 确保每个进程结束时关闭其WebDriver

def get_close_button():
    output_queue = multiprocessing.Queue()
    processes = [
        multiprocessing.Process(target=find_elements_process, args=(By.CLASS_NAME, "android.widget.ImageView", output_queue)),
        multiprocessing.Process(target=find_elements_process, args=(By.XPATH, "//android.widget.TextView[contains(@text, '跳过')]", output_queue))
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join(30)
        if process.is_alive():
            print("一个查找进程超时，正在终止该进程。")
            process.terminate()
            process.join()

    elements = []
    while not output_queue.empty():
        elements.extend(output_queue.get())

    close_button = None
    min_distance = float('inf')
    for element in elements:
        if element.size['height'] > 90 or element.size['width'] < 15 or element.size['width'] > 120:
            continue
        x_right_top = element.location['x'] + element.size['width']
        y_right_top = element.location['y']
        if x_right_top < driver.width * 0.8 or y_right_top > driver.height * 0.15:
            continue
        if not (element.is_displayed() and element.is_enabled()):
            continue
        distance = ((driver.width - x_right_top) ** 2 + y_right_top ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            close_button = element

    if close_button:
        print(f"找到最合适的右上角关闭按钮：类别-{close_button.get_attribute('className')}, 位置-{close_button.location}, 大小-{close_button.size}")
    else:
        print("未能找到合适的右上角关闭按钮。")

    return close_button

def main():
    close_button = get_close_button()
    if close_button:
        print("已找到并准备进行操作。")
    else:
        print("未找到关闭按钮。")

if __name__ == "__main__":
    main()