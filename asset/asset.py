import time
import random
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# 展示页
def handle_display_page(driver, wait):
    try:
        time.sleep(3)
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((MobileBy.XPATH, "//*[@text='加载中']"))
        )
        print("页面已正常加载")
        time.sleep(10)  # 先等待页面可能的加载时间

        WebDriverWait(driver, 70).until_not(
            EC.presence_of_all_elements_located((By.XPATH, "//android.widget.TextView[@width<100 and @height<100]"))
        )
        print("倒计时结束。")

        time.sleep(5)  # 等待页面可能的自动刷新

        try:
            cruel_leave_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@text, '残忍离开')]"))
            )
            cruel_leave_button.click()
            print("点击了‘残忍离开’按钮。")
        except TimeoutException:
            print("未在规定时间内找到‘残忍离开’按钮。")
        except NoSuchElementException:
            print("页面上不存在‘残忍离开’按钮。")
        except Exception as e:
            print(f"尝试点击‘残忍离开’时发生异常：{str(e)}")

        # 调用点击元素函数
        retry_click_right_top_button(driver)

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))

# 获取元素
def find_right_top_button(driver):
    # 搜索 ImageView 和 TextView 类型的元素
    elements = driver.find_elements(By.CLASS_NAME, "android.widget.ImageView") + \
               driver.find_elements(By.CLASS_NAME, "android.widget.TextView") + \
               driver.find_elements(By.CLASS_NAME, "android.widget.RelativeLayout")
    right_top_button = None
    min_distance = float('inf')
    for element in elements:
        if element.size['width'] < 100 and element.size['height'] < 100:
            distance = (element.location['x'] - driver.get_window_size()['width'])**2 + element.location['y']**2
            if distance < min_distance:
                min_distance = distance
                right_top_button = element
    return right_top_button

# 点击元素
def retry_click_right_top_button(driver):
    attempts = 0
    while attempts < 5:
        try:
            button = find_right_top_button(driver)
            if button:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()
                if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))):
                    # print("已成功回到资产页。")
                    return True
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新定位元素。")
            driver.refresh()  # 刷新页面可以帮助重置页面状态
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
            driver.refresh()  # 刷新页面，尝试重新定位元素
        except Exception as e:
            print(f"尝试点击右上角关闭按钮时发生异常：{str(e)}")
        time.sleep(1)  # 在尝试之间稍作等待
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

# 领取奖励
def click_reward(driver, wait, long_wait):
    base_xpaths = [
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"
    ]

    # 从最后一次成功的位置开始
    last_successful_index = 1
    while True:
        found = False
        for i in range(last_successful_index, 7):  # 假设有6个奖励按钮
            for base_xpath in base_xpaths:
                xpath = base_xpath.format(i=i)  # 动态生成每个按钮的 XPath
                try:
                    reward = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    if reward.get_attribute("selected") == "true":
                        reward.click()
                        print(f"点击了位于 {i} 的领取奖励，使用的XPath为: {xpath}")
                        handle_display_page(driver, wait)  # 处理展示页的逻辑
                        if long_wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble"))):
                            print("已成功回到资产页。")
                            last_successful_index = i + 1  # 更新最后成功的索引
                            found = True
                            break  # 成功点击后退出内循环
                except TimeoutException:
                    print(f"未能及时找到位于 {i} 的领取奖励，路径：{xpath}")
                except NoSuchElementException:
                    print(f"未能定位到位于 {i} 的领取奖励，路径：{xpath}")
                except Exception as e:
                    print(f"尝试点击位于 {i} 的领取奖励时发生异常：{str(e)}，路径：{xpath}")
            if found:
                break  # 成功点击后退出外循环
        if not found:
            print("未找到任何选中的‘领取奖励’按钮或已完成所有奖励领取。")
            break
        time.sleep(2)  # 循环间隔等待

# 点击领取
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
    'platformVersion': '7',
    'deviceName': '192.168.0.35:5555 device',
    'settings[waitForIdleTimeout]': 100,
    'settings[waitForSelectorTimeout]': 100,
    'newCommandTimeout': 300, # 设置新的命令超时时间为300秒
    'noReset': True
}

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
wait = WebDriverWait(driver, 10)
long_wait = WebDriverWait(driver, 60)

try:
    click_miss_bubble(driver, wait)
    click_reward(driver, wait, long_wait)
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
