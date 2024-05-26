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

        time.sleep(15)  # 等待页面可能的自动刷新
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
                # 在点击前先获取并打印元素信息
                element_info = f"点击了右上角关闭按钮：{button.tag_name}, {button.location}, {button.size}"
                button.click()  # 执行点击操作

                # 打印元素信息
                # print(element_info)

                # 增加3秒等待时间，以确保页面状态稳定
                time.sleep(3)

                # 检查是否成功回到资产页
                if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))):
                    print("已成功回到资产页。")
                    return True
                else:
                    print("点击关闭按钮后未能返回资产页，继续尝试。")
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
            # 在异常处理中也添加3秒等待，保持一致
            time.sleep(3)
        # 每次循环尝试结束后增加等待时间
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

def find_right_top_button(driver):
    all_close_buttons = driver.find_elements(By.CLASS_NAME, "android.widget.ImageView")
    right_top_button = None
    min_distance = float('inf')
    for button in all_close_buttons:
        if button.size['width'] < 100 and button.size['height'] < 100:
            distance = (button.location['x'] - driver.get_window_size()['width'])**2 + button.location['y']**2
            if distance < min_distance:
                min_distance = distance
                right_top_button = button
    return right_top_button

def click_reward(driver, wait, long_wait):
    base_xpath = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"

    while True:
        found = False
        for i in range(1, 7):  # 假设有6个领取奖励
            xpath = base_xpath.format(i=i)  # 动态生成每个按钮的 XPath
            try:
                reward = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                if reward.get_attribute("selected") == "true":
                    reward.click()
                    print(f"点击了位于 {i} 的领取奖励。")
                    handle_display_page(driver, wait)  # 处理展示页的逻辑
                    long_wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
                    print("已成功回到资产页。")
                    found = True
                    break  # 成功点击后退出循环
            except TimeoutException:
                print(f"未能及时找到位于 {i} 的领取奖励。")
            except NoSuchElementException:
                print(f"未能定位到位于 {i} 的领取奖励。")
            except Exception as e:
                print(f"尝试点击位于 {i} 的领取奖励时发生异常：{str(e)}")
        if not found:
            print("未找到任何选中的‘领取奖励’按钮或已完成所有奖励领取。")
            break
        time.sleep(2)  # 循环间隔等待

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
