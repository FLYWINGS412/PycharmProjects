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
        time.sleep(1)
        WebDriverWait(driver, 120).until(
            EC.invisibility_of_element_located((MobileBy.XPATH, "//*[contains(@text, '加载中')]"))
        )
        print("页面已正常加载")
        time.sleep(10)  # 先等待页面可能的加载时间

        start_time = time.time()
        timeout = 120
        popup_texts = [ "放弃福利", "残忍离开","放弃奖励离开"]
        handled_popup = False

        while time.time() - start_time < timeout:
            if not handled_popup:
                for text in popup_texts:
                    try:
                        xpath_expression = f"//*[contains(@text, '{text}')]"
                        popup_button = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((MobileBy.XPATH, xpath_expression))
                        )
                        time.sleep(random.randint(2, 5))
                        popup_button.click()
                        print(f"关闭了‘{text}’弹窗。")
                        time.sleep(1)  # 点击后等待页面可能的自动刷新
                        handled_popup = True
                        break  # 处理一个弹窗后退出内部循环
                    except TimeoutException:
                        continue
                    except NoSuchElementException:
                        continue

            # 检查“后”或自定义倒计时元素是否不可见
            try:
                WebDriverWait(driver, 5).until(
                    lambda x: not any([
                        x.find_element_by_xpath("//*[contains(@text, '后')]").is_displayed(),
                        x.find_element_by_id("com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id").is_displayed()
                    ])
                )
                print("倒计时结束。")
                time.sleep(random.randint(2, 5))
                break  # 倒计时不可见，退出循环
            except TimeoutException:
                continue  # 倒计时仍可见，继续循环

        if not handled_popup:
            print("未找到任何弹窗。")

        # 调用点击元素函数
        if not retry_click_right_top_button(driver, wait):
            return False

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
        return False
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))
        return False
    return True

# 点击元素
def retry_click_right_top_button(driver, wait):
    attempts = 0
    while attempts < 5:
        # 检查是否当前在桌面
        if ".launcher3.Launcher" in driver.current_activity:
            print("检测到应用异常退回到桌面，需要重新开始。")
            return False  # 这将提示 main 函数重新启动应用

        try:
            button = find_right_top_button(driver)
            if button:
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable(button))
                print(f"尝试点击右上角关闭按钮：类别-{button.get_attribute('className')}, 位置-{button.location}, 大小-{button.size}")
                button.click()

                # 直接调用 is_on_assets_page 函数来检测是否已成功回到资产页
                if is_on_assets_page(driver):
                    return True
            else:
                print("未找到符合条件的右上角关闭按钮。")
        except StaleElementReferenceException:
            print("元素状态已改变，正在重新获取元素。")
        except NoSuchElementException:
            print("未能定位到元素，可能页面已更新。")
        except Exception as e:
            print(f"尝试点击右上角关闭按钮时发生错误：{str(e)}")
        attempts += 1
    print("尝试多次后仍未成功点击按钮。")
    return False

# 获取元素
def find_right_top_button(driver):
    try:
        time.sleep(2)  # 间隔等待再次尝试
        elements = []

        # 等待并查找 关闭按钮 元素
        try:
            elements = WebDriverWait(driver, 120).until(lambda d: d.find_elements(MobileBy.CLASS_NAME, "android.widget.ImageView") +
                                            d.find_elements(MobileBy.CLASS_NAME, "android.widget.TextView") +
                                            d.find_elements(MobileBy.XPATH, "//*[contains(@text, '跳过')]") +
                                            d.find_elements(MobileBy.XPATH, "//*[contains(@text, '取消')]"))
        except TimeoutException:
            print("等待 关闭按钮 超时")

        right_top_button = None
        min_distance = float('inf')

        # 遍历找到的元素，选择最符合条件的右上角按钮
        for element in elements:
            if element.size['width'] < 100 and element.size['height'] < 100:
                distance = (element.location['x'] - driver.get_window_size()['width'])**2 + element.location['y']**2
                if distance < min_distance:
                    min_distance = distance
                    right_top_button = element

        return right_top_button
    except Exception as e:
        print(f"获取右上角按钮时发生错误")
        return None

# 领取奖励
def click_reward(driver, wait):
    base_xpaths = [
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"
    ]

    last_successful_index = 1  # 从最后一次成功的位置开始
    while True:
        found = False
        for i in range(last_successful_index, 7):  # 假设有6个奖励按钮
            for base_xpath in base_xpaths:
                xpath = base_xpath.format(i=i)  # 动态生成每个按钮的 XPath
                try:
                    reward = wait.until(EC.presence_of_element_located((MobileBy.XPATH, xpath)))
                    if reward.get_attribute("selected") == "true":
                        reward.click()
                        print(f"点击了位于 {i} 的领取奖励，使用的XPath为: {xpath}")
                        if not handle_display_page(driver, wait):  # 处理展示页的逻辑
                            return False
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

        # 随机等待2-5秒
        time.sleep(random.randint(2, 5))
    return True

# 点击领取
def click_miss_bubble(driver, wait):
    try:
        while True:  # 使用无限循环，直到所有奖励被领取或发生异常
            miss_bubble_text = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_miss_bubble"))).text
            current, total = map(int, miss_bubble_text.replace(" ", "").strip('()').split('/'))
            print(f"当前状态：{current}/{total}")

            if current >= total:
                print("所有奖励已领取完毕。")
                break

            receive_bubble = wait.until(EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
            receive_bubble.click()
            print(f"点击了领取按钮，更新剩余次数：{current+1}/{total}")

            if not handle_display_page(driver, wait):  # 处理展示页的逻辑
                return False

            # 随机等待2-5秒
            time.sleep(random.randint(2, 5))

    except (TimeoutException, NoSuchElementException):
        print("找不到 txt_miss_bubble 或 txt_receive_bubble 元素，无法点击。")
        return False
    return True

# 跳转资产页
def navigate_to_assets_page(driver, wait):
    """尝试导航到资产页面，并关闭可能出现的弹窗。"""
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        try:
            assets_element = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//*[contains(@text, '资产')]")))
            assets_element.click()
            print("已找到并点击‘资产’。")
            time.sleep(random.randint(2, 5))

            try:
                close_button = wait.until(
                    EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
                )
                close_button.click()
                print("已关闭弹窗。")
                time.sleep(random.randint(2, 5))
            except TimeoutException:
                print("没有找到关闭弹窗的按钮。")

            if is_on_assets_page(driver):
                return True
            else:
                print("未成功到达资产页，尝试再次点击。")
        except TimeoutException:
            print("未找到‘资产’元素或未成功到达资产页。")
        except Exception as e:
            print(f"检查‘资产’时发生错误: {e}")
        attempts += 1
        time.sleep(2)

    print("尝试多次后仍未成功访问资产页。")
    return False

# 检查资产页
def is_on_assets_page(driver):
    try:
        # 检查是否存在资产页的特定元素
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
        print("已成功到达资产页。")
        return True
    except TimeoutException:
        print("未成功到达资产页。")
        return False

def main():
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'localhost:7555 device',
        "appPackage": "com.xiangshi.bjxsgc",
        "appActivity": "com.xiangshi.bjxsgc.activity.LauncherActivity",
        'settings[waitForIdleTimeout]': 100,
        'settings[waitForSelectorTimeout]': 100,
        # 'newCommandTimeout': 300,  # 设置新的命令超时时间为300秒
        'noReset': True
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    wait = WebDriverWait(driver, 10)
    # long_wait = WebDriverWait(driver, 60)
    time.sleep(30)  # 等待APP完全加载

    # 等待页面完成加载
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
    )
    print("首次加载页面已完成")

    # 获取设备的屏幕大小
    size = driver.get_window_size()
    width = size['width']
    height = size['height']

    try:
        # 跳转资产页
        if not navigate_to_assets_page(driver, wait):
            print("未能导航到资产页面，程序终止。")
            return False

        # 点击领取
        time.sleep(random.randint(2, 5))
        if not is_on_assets_page(driver) or not click_miss_bubble(driver, wait):
            return False  # 不在资产页或领取气泡失败，重新尝试

        # 领取奖励
        time.sleep(random.randint(2, 5))
        if not is_on_assets_page(driver) or not click_reward(driver, wait):
            return False  # 不在资产页或领取奖励失败，重新尝试

        print("所有操作完成，准备退出应用。")
        return True  # 返回 True 表示成功完成操作

    except Exception as e:
        print(f"处理中发生异常：{str(e)}")
        return False

    finally:
        # driver.quit()
        print("驱动已关闭，应用退出。")

if __name__ == "__main__":
    while not main():
        print("操作失败，重新尝试。")
