import time
import random
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import find_element_with_retry, swipe_to_scroll, get_progress_bar_value, check_and_return_to_home

# 首页看视频
def watch_home_videos(driver):
    print("开始首页看视频")
    prev_progress_value = None
    loop_count = 0

    # 检查并点击“点击翻倍”按钮
    try:
        double_button = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                                'new UiSelector().text("点击翻倍")', retries=1)
        double_button.click()
        print("点击了'点击翻倍'按钮")
    except Exception:
        pass  # 如果找不到“点击翻倍”按钮，就继续执行下面的代码

    start_time = time.time()
    while True:

        # 检查进度条
        try:
            progress_bar = find_element_with_retry(driver, By.ID, "com.kuaishou.nebula:id/circular_progress_bar", retries=1)

            if loop_count % 1 == 0:  # 每200秒进行连续截图比较
                progress_value_1 = get_progress_bar_value(driver)
                time.sleep(10)
                progress_value_2 = get_progress_bar_value(driver)

                if progress_value_1 == progress_value_2:
                    print("进度条没有变化，翻页...")
                    swipe_to_scroll(driver)
                    loop_count = 0  # 重置计数器
                else:
                    print("进度条有变化，继续等待...")
            else:
                print("进度条存在，继续等待...")

            # 增加循环次数
            loop_count += 1
            end_time = time.time()
            loop_duration = end_time - start_time
            print(f"本次用时: {loop_duration:.2f} 秒")

        except Exception as e:
            print(f"进度条不存在，翻页...")
            swipe_to_scroll(driver)
            loop_count = 0  # 重置计数器

# 看精选直播
def watch_featured_live_stream(driver):
    loop_count = 0

    while True:
        start_time = time.time()
        try:
            # 切换到 WebView 上下文
            for context in driver.contexts:
                if 'WEBVIEW' in context:
                    driver.switch_to.context(context)
                    break

            # 尝试查找“去看看”按钮并点击
            element = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                              'new UiSelector().text("去看看")', retries=10, wait_time=10)
            element.click()
            print("开始看直播")

            # 等待15秒
            time.sleep(15)

            # 检查是否有“看播中”元素
            try:
                follow_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("看播中")'))
                )
                pass
            except Exception as e:
                print("未找到'看播中'，返回任务页")
                check_and_return_to_home(driver)
                continue

            # 查找并点击'去关注'的TextView，如果找不到就按返回键并检查当前页面
            try:
                follow_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("去关注")'))
                )
                follow_element.click()
                print("点击了去关注")
            except Exception as e:
                print("未找到'去关注'按钮")
                driver.press_keycode(AndroidKey.BACK)

            # 等待15分钟
            time.sleep(15 * 60)

            check_and_return_to_home(driver)

            # 增加循环次数
            loop_count += 1
            end_time = time.time()
            loop_duration = end_time - start_time
            print(f"完成看直播: 第 {loop_count} 次，本次用时: {loop_duration:.2f} 秒")

        except Exception as e:
            print(f"Error: {e}")
            break

# 取消关注
def cancel_following(driver):
    # 滚动到最上方
    driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                        'new UiScrollable(new UiSelector().scrollable(true)).scrollToBeginning(1)')
    print("滚动到最上方")

    # 检查并点击关注按钮
    following_button = find_element_with_retry(driver, By.ID, "com.kuaishou.nebula:id/following_layout")
    following_button.click()
    print("点击关注按钮")
    time.sleep(random.randint(2, 5))

    # 开始循环
    while True:
        try:
            # 检查并点击三点按钮
            more_button = find_element_with_retry(driver, By.ID, "com.kuaishou.nebula:id/more_btn")
            more_button.click()
            print("点击三点按钮")
            time.sleep(random.randint(1, 3))

            # 检查并点击取消关注按钮
            unfollow_button = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                                      'new UiSelector().resourceId("com.kuaishou.nebula:id/text").text("取消关注")')
            unfollow_button.click()
            print("点击取消关注按钮")
            time.sleep(random.randint(1, 3))

            # 检查并点击确定取消关注按钮
            confirm_button = find_element_with_retry(driver, By.ANDROID_UIAUTOMATOR,
                                                     'new UiSelector().resourceId("com.kuaishou.nebula:id/qlist_alert_dialog_item_text").text("取消关注")')
            confirm_button.click()
            print("点击确定取消关注按钮")
            time.sleep(random.randint(1, 3))

        except Exception as e:
            print("未找到更多按钮，结束循环")
            break

    # 返回任务页
    check_and_return_to_home(driver)
