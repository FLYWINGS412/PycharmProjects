import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

def handle_display_page(driver, wait):
    try:
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((MobileBy.XPATH, "//*[@text='加载中']"))
        )
        print("页面已正常加载")
        time.sleep(15)  # 先等待页面可能的加载时间

        WebDriverWait(driver, 60).until_not(
            EC.presence_of_all_elements_located((By.XPATH, "//android.widget.TextView[@width<100 and @height<100]"))
        )
        print("倒计时结束。")

        time.sleep(10)  # 等待页面可能的自动刷新
        retry_click_right_top_button(driver)

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))

def retry_click_right_top_button(driver):
    attempts = 0
    while attempts < 3:
        try:
            button = find_right_top_button(driver)
            if button:
                button.click()
                # 确保点击后打印元素信息
                print(f"点击了右上角关闭按钮：类别-{button.tag_name}, 位置-{button.location}, 大小-{button.size}")
                # 检查是否成功回到资产页
                if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))):
                    print("已成功回到资产页。")
                    return
                else:
                    print("点击关闭按钮后未能返回资产页，继续尝试。")
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
            time.sleep(1)  # 等待1秒后再次尝试
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")

def find_right_top_button(driver):
    # 获取所有的关闭按钮元素
    all_close_buttons = driver.find_elements(By.CLASS_NAME, "android.widget.ImageView")
    right_top_button = None  # 用于存储最终选择的右上角按钮
    min_distance = float('inf')  # 初始化最小距离为无限大

    # 遍历所有关闭按钮，寻找位于右上角的按钮
    for button in all_close_buttons:
        if button.size['width'] < 100 and button.size['height'] < 100:
            # 计算每个按钮到屏幕右上角的欧氏距离
            distance = (button.location['x'] - driver.get_window_size()['width'])**2 + button.location['y']**2
            # 如果当前按钮的距离比之前记录的最小距离还小，更新最小距离并记录该按钮
            if distance < min_distance:
                min_distance = distance
                right_top_button = button

    # 返回找到的位于右上角的按钮，如果没有找到符合条件的按钮则返回None
    return right_top_button

def click_reward(driver, wait, long_wait):
    while True:
        try:
            # reward = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive")))
            # reward = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_bubble")))
            reward = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//*[@text='领取奖励']")))
            reward.click()
            print("点击了奖励，进入展示页。")
            handle_display_page(driver, wait)  # 处理展示页的逻辑
            long_wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
            print("返回主页面。")
            time.sleep(2)
        except TimeoutException:
            print("找不到奖励元素或未能及时返回主页，可能已完成所有奖励领取。")
            break
        except NoSuchElementException:
            print("页面元素不可访问，可能正在加载。")
            time.sleep(5)

def click_miss_bubble(driver, wait):
    try:
        miss_bubble_text = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_miss_bubble"))).text
        current, total = map(int, miss_bubble_text.replace(" ", "").strip('()').split('/'))
        print(f"当前状态：{current}/{total}")
        while current < total:
            receive_bubble = wait.until(EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
            receive_bubble.click()
            print(f"点击了领取按钮，更新剩余次数：{current+1}/{total}")
            handle_display_page(driver, wait)  # 处理展示页的逻辑
            current += 1
            time.sleep(5)
    except (TimeoutException, NoSuchElementException):
        print("找不到 txt_miss_bubble 或 txt_receive_bubble 元素，无法点击。")

desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': '192.168.0.34:5555 device',
    'settings[waitForIdleTimeout]': 100,
    'settings[waitForSelectorTimeout]': 100,
    'newCommandTimeout': 300, # 设置新的命令超时时间为300秒
    'noReset': True
}

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
wait = WebDriverWait(driver, 10)
long_wait = WebDriverWait(driver, 60)

try:
    click_reward(driver, wait, long_wait)
    click_miss_bubble(driver, wait)
    print("所有操作完成，准备退出应用。")
except (TimeoutException, NoSuchElementException):
    print("处理中发生异常，退出应用。")
finally:
    try:
        long_wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
        time.sleep(5)  # 确保页面稳定后退出
    except Exception as e:
        print(f"在关闭前确认状态时发生异常：{str(e)}")
    driver.quit()
    print("驱动已关闭，应用退出。")
