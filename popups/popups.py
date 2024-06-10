import time
import random
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from tasks import tasks
from utils import utils


# 首页视频红包
def home_video_bonus(driver):
    found_and_handled = False  # 初始化标记，假定没有找到或处理弹窗
    try:
        # 直接尝试获取接收弹窗元素
        bg_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
        )
        time.sleep(random.randint(2, 5))  # 随机等待2-5秒
        bg_element.click()
        print("点击了接收弹窗")
        found_and_handled = True  # 更新标记为已找到并处理弹窗

        # 尝试获取并点击关闭弹窗，仅在元素存在时执行
        try:
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            close_element.click()
            print("点击了关闭弹窗")
            time.sleep(random.randint(2, 5))  # 随机等待2-5秒
            found_and_handled = True  # 确认找到并处理了关闭弹窗
        except TimeoutException:
            print("未找到关闭弹窗元素，不执行关闭操作")
    except TimeoutException:
        print("未找到弹窗或等待关闭弹窗超时")

    return found_and_handled

# 每日股东分红
def daily_dividend_distribution(driver, wait, width, height):
    try:
        # 检测每日股东分红
        try:
            receive_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_watch_ad"))
            )
            time.sleep(random.randint(2, 5))
            receive_button.click()
            print("已领取每日股东分红。")

            # 处理展示页
            if not tasks.handle_display_page(driver, wait, width, height):
                print("处理展示页时出错。")
                return False

        except TimeoutException:
            print("未找到每日股东分红，跳过此部分。")

    except Exception as e:
        print(f"处理活动时发生异常")
        return False

    # 检测是否已成功回到资产页
    return utils.is_on_assets_page(driver, wait, width, height)

# 整点红包
def hourly_bonus(driver, wait, width, height):
    try:
        try:
            receive_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_receive"))
            )
            time.sleep(random.randint(2, 5))
            receive_button.click()
            print("已领取整点红包。")

            # 处理展示页
            if not tasks.handle_display_page(driver, wait, width, height):
                print("处理展示页时出错。")
                return False

            # 尝试获取并点击关闭弹窗
            close_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/iv_close"))
            )
            time.sleep(random.randint(1, 5))  # 随机等待1-5秒
            close_element.click()
            print("点击了关闭弹窗")
        except TimeoutException:
            print("未找到整点红包按钮，跳过此部分。")

    except Exception as e:
        print(f"处理活动时发生异常")
        return False

    # 检测是否已成功回到资产页
    return utils.is_on_assets_page(driver, wait, width, height)

# 展示页弹窗
def display_page_popup(driver, popup_texts):
    handled_popup = False
    for text in popup_texts:
        try:
            xpath_expression = f"//*[contains(@text, '{text}')]"
            popup_button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, xpath_expression))
            )
            time.sleep(random.randint(2, 5))
            popup_button.click()
            print(f"关闭了‘{text}’弹窗。")
            handled_popup = True
            break
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            continue
    return handled_popup
