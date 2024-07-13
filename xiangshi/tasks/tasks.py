import re
import os
import time
import json
import random
import threading
import subprocess
from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError, CancelledError
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from auth import auth
from tasks import tasks
from utils import utils
from popups import popups

# 首页红包奖励
def handle_home_page_video(driver, account):
    # 首页红包奖励
    if not popups.home_video_bonus(driver):
        return False

    try:
        while True:
            start_time = time.time()  # 记录循环开始时间

            # 执行滑动操作
            utils.swipe_to_scroll(driver)

            # 检查首页红包奖励
            if not popups.home_video_bonus(driver):
                return False

            # 等待页面完成加载
            time.sleep(1)
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
            )
            print("页面已正常加载")

            # 翻页后的随机等待时间
            random_sleep = random.randint(0, 20)
            print(f"等待 {random_sleep} 秒")
            time.sleep(random_sleep)

            # 检查首页红包奖励
            if not popups.home_video_bonus(driver):
                return False

            # 立即检查首页红包奖励是否存在
            elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
            if elements:
                print("找到了首页红包奖励，继续循环")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
            else:
                # 第一次未找到首页红包奖励时，再次处理弹窗并重新检查
                print("未找到首页红包奖励，再次检查弹窗")

                # 检查首页红包奖励
                if not popups.home_video_bonus(driver):
                    return False

                # 立即检查首页红包奖励是否存在
                elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
                if not elements:
                    print("再次检查后仍未找到首页红包奖励，退出循环")
                    break
    except Exception as e:
        print(f"在滑屏循环中发生错误：{e}")
        return False

    return True

# 激励视频奖励
def mutual_assistance_reward(driver, account):
    # 检查首页红包奖励是否完成
    elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
    if elements:
        print("首页红包奖励未完成，执行首页红包奖励任务")
        handle_home_page_video(driver, account)
        print("首页红包奖励已完成，继续下一步")
    else:
        print("首页红包奖励已完成，继续下一步")

    # 个人页面
    my_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='我的']")))
    my_tab.click()
    print("点击我的")
    time.sleep(random.randint(2, 5))

    # 点击关注
    follow_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='关注']")))
    follow_tab.click()
    print("点击关注")
    time.sleep(random.randint(2, 5))

    # 检查是否在我的关注
    current_activity = utils.get_current_activity(driver)
    expected_setting_activity = "com.xiangshi.main.activity.FollowActivity"
    if expected_setting_activity not in current_activity:
        print("未能加载到我的关注，退出登出流程。")
        return False
    print("我的关注")

    # 我的关注
    my_following = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[contains(@text, '罗亿凡')]")))
    my_following.click()
    print("选择罗亿凡")
    time.sleep(random.randint(2, 5))

    # 检查是否在用户主页
    current_activity = utils.get_current_activity(driver)
    expected_setting_activity = "com.xiangshi.main.activity.UserHomeActivity"
    if expected_setting_activity not in current_activity:
        print("未能加载到用户主页，退出登出流程。")
        return False
    print("用户主页")
    time.sleep(10)

    # 选择作品
    portfolio_elements = driver.wait.until(EC.presence_of_all_elements_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/thumb")))
    if portfolio_elements:
        # 点击第一排的第一个作品
        first_element = portfolio_elements[0]
        first_element.click()
        print("点击了第一排的第一个作品")
    else:
        print("未找到任何作品元素")

    # 等待页面完成加载
    time.sleep(1)
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
    )
    print("页面已正常加载")

    while True:
        start_time = time.time()  # 记录循环开始时间

        # 检查激励视频奖励
        try:
            # 激励视频奖励
            reward_layer = driver.wait.until(
                EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_reward_ad"))
            )
            time.sleep(random.randint(2, 5))
            reward_layer.click()
            print("点击了激励视频奖励")

            # 等待页面完成加载
            time.sleep(1)
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
            )

            # 检查头像是否消失
            try:
                WebDriverWait(driver, 3).until(
                    EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
                )
                print("没检查到头像，加载展示页。")
                if not handle_display_page(driver):
                    return False

                # 检查是否存在包含“每日”文本的元素
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((MobileBy.XPATH, "//*[contains(@text, '每日20次')]"))
                    )
                    print("检查到'每日20次'文本，程序终止并退出到系统桌面。")
                    utils.log_mutual_assistance_reward(driver, account)
                    break
                except TimeoutException:
                    print("未检查到'每日20次'文本，继续执行。")
            except TimeoutException:
                print("检查到头像，继续执行滑动操作。")
        except Exception as e:
            print("未找到或不可点击激励广告。")

        # 执行滑动操作
        utils.swipe_to_scroll(driver)

        # 输出循环用时
        elapsed_time = round(time.time() - start_time, 2)
        print(f"用时: {elapsed_time} 秒")

    return True

# 资产页广告奖励
def collect_rewards(driver, account):
    try:
        # 检查首页红包奖励是否完成
        elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
        if elements:
            print("首页红包奖励未完成，执行首页红包奖励任务")
            handle_home_page_video(driver, account)
            print("首页红包奖励已完成，继续下一步")
        else:
            print("首页红包奖励已完成，继续下一步")

        # 跳转到资产页
        assets_element = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='资产']")))
        assets_element.click()
        print("已找到并点击‘资产’。")
        time.sleep(random.randint(2, 5))

        # 每日股东分红
        if not popups.daily_dividend_distribution(driver):
            return False

        # 点击领取
        try:
            while True:
                start_time = time.time()  # 记录循环开始时间

                # 整点红包奖励
                if not popups.hourly_bonus(driver):
                    return False

                try:
                    miss_bubble_element = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_miss_bubble")))
                    click_to_collect_text = miss_bubble_element.text
                    current, total = map(int, click_to_collect_text.replace(" ", "").strip('()').split('/'))

                    if current >= total:
                        print("所有‘点击领取’已领取完毕。")
                        break

                    receive_bubble = driver.wait.until(EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
                    receive_bubble.click()
                    print(f"点击了领取按钮，更新剩余次数：{current + 1}/{total}")

                    if not handle_display_page(driver):
                        return False

                    # 输出循环用时
                    elapsed_time = round(time.time() - start_time, 2)
                    print(f"用时: {elapsed_time} 秒")

                except StaleElementReferenceException:
                    print("元素不再存在于 DOM 中，重新获取元素。")
                    continue
                except Exception as e:
                    print(f"在点击领取时发生异常：{e}")
                    continue

        except (TimeoutException, NoSuchElementException) as e:
            print(f"找不到 txt_miss_bubble 或 txt_receive_bubble 元素，无法点击：{e}")

        # 领取奖励
        base_xpaths = [
            "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
            "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
            "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"
        ]

        last_successful_index = 1  # 从最后一次成功的位置开始
        while True:
            start_time = time.time()  # 记录循环开始时间

            # 整点红包
            if not popups.hourly_bonus(driver):
                return False

            found = False
            for i in range(last_successful_index, 7):  # 假设有6个奖励按钮
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(utils.check_xpath, driver, base_xpath.format(i=i), idx, i) for idx, base_xpath in enumerate(base_xpaths)]
                    for future in as_completed(futures):
                        result = future.result()
                        if result and "成功点击" in result:  # 检查是否是成功点击的消息
                            print(result)
                            if not handle_display_page(driver):  # 处理展示页的逻辑
                                return False
                            found = True
                            break  # 成功点击后退出内循环
                    if not found:  # 如果在这一轮检查中没有找到并点击成功
                        print(f"第 {i} 个领取奖励，不能点击。")

                last_successful_index = i + 1  # 更新最后成功的索引
                if found:
                    break  # 成功点击后退出外循环

            if not found:
                print("所有‘领取奖励’领取完毕。")
                break

            # 输出循环用时
            elapsed_time = round(time.time() - start_time, 2)
            print(f"用时: {elapsed_time} 秒")

        # 获取并存储“我的享币”和“我的享点”
        utils.get_and_store_points(driver, account)

        return True

    except Exception as e:
        print(f"处理资产页广告奖励时发生异常：{e}")
        return False

# 展示页
def handle_display_page(driver):
    # 等待页面完成加载
    time.sleep(1)
    WebDriverWait(driver, 60).until(
        EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
    )

    element_to_wait = None  # 初始化 element_to_wait 为 None
    event = threading.Event()  # 用于同步倒计时结束的事件

    # 第一种检查倒计时的方法
    def check_countdown_by_text_view():
        nonlocal element_to_wait
        text_views = driver.find_elements(MobileBy.XPATH,
                                          "//android.widget.TextView[contains(@text, 's')] | //android.view.View[contains(@text, 's')]")
        for text_view in text_views:
            location = text_view.location
            size = text_view.size
            top_y = location['y']
            if top_y < driver.height * 0.15:
                element_to_wait = text_view
                print("找到倒计时元素（'S'）")
                event.set()
                break

    # 第二种检查倒计时的方法（长度为1或3的纯数字倒计时）
    def check_countdown_by_numeric():
        nonlocal element_to_wait
        text_views = driver.find_elements(MobileBy.XPATH,
                                          "//android.widget.TextView[string-length(@text) <= 3 and @text = number(@text)] | //android.view.View[string-length(@text) <= 3 and @text = number(@text)]")
        for text_view in text_views:
            location = text_view.location
            size = text_view.size
            top_y = location['y']
            if top_y < driver.height * 0.15:
                element_to_wait = text_view
                print("找到倒计时元素（'数字'）")
                event.set()
                break

    # 检查其他可能的倒计时元素
    def check_countdown_by_id():
        nonlocal element_to_wait
        countdown_element = driver.find_elements(MobileBy.ID,
                                                           "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")
        if countdown_element:
            element_to_wait = countdown_element[0]
            print("找到倒计时元素（'ID'）")
            event.set()

    try:
        start_time = time.time()
        timeout = 35
        time.sleep(2)
        popup_texts = ["放弃", "离开", "取消"]

        while True:
            # 检查是否已超过最大等待时间
            current_time = time.time()
            if current_time - start_time > timeout:
                print("已超过最大等待时间，终止倒计时监控。")
                break

            # 展示页弹窗
            popups.display_page_popup(driver, popup_texts)

            # 如果已经找到倒计时元素，则只检查其状态
            if element_to_wait and isinstance(element_to_wait, WebElement):
                try:
                    WebDriverWait(driver, 0).until(
                        lambda driver: re.match(r"0\s*s?", element_to_wait.text) is not None
                    )
                    print("倒计时结束。")
                    break  # 结束while循环
                except TimeoutException:
                    continue  # 继续while循环
                except StaleElementReferenceException:
                    print("倒计时元素已从DOM中移除，倒计时结束。")
                    break  # 退出循环，认为倒计时结束

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(check_countdown_by_text_view),
                    executor.submit(check_countdown_by_numeric),
                    executor.submit(check_countdown_by_id)
                ]

                event.wait(timeout=5)  # 等待任一检查线程找到倒计时元素

                for future in as_completed(futures):
                    future.cancel()  # 取消未完成的任务

            if not element_to_wait:
                print("未找到倒计时元素，可能页面已刷新。")
                break

    except NoSuchElementException:
        print("未找到倒计时元素，等待剩余时间后退出。")
        remaining_time = start_time + timeout - time.time()
        if remaining_time > 0:
            time.sleep(remaining_time)
    except Exception as e:
        print(f"发生错误: {e}")

    # 展示页弹窗
    popups.display_page_popup(driver, popup_texts)

    # 调用点击元素函数
    if not utils.click_close_button(driver):
        return False

    return True

# 关注
def follow(driver, account, follow_list):
    # 首页红包奖励
    if not popups.home_video_bonus(driver):
        return False

    # 检查首页红包奖励是否完成
    elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
    if elements:
        print("首页红包奖励未完成，执行首页红包奖励任务")
        handle_home_page_video(driver, account)
        print("首页红包奖励已完成，继续下一步")
    else:
        print("首页红包奖励已完成，继续下一步")

    try:
        # 查找并点击搜索按钮
        search_button = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_search")))
        search_button.click()
        print("点击了搜索按钮")
        time.sleep(random.randint(2, 5))

        for user_id in follow_list:
            # 查找并点击搜索框
            search_box = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/edit")))
            search_box.click()
            print("点击了搜索框")
            time.sleep(random.randint(2, 5))

            # 输入用户ID
            search_box.send_keys(user_id)
            print(f"输入了用户ID {user_id}")
            time.sleep(random.randint(2, 5))

            # 查找并点击关注按钮
            follow_button = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_follow")))
            follow_button.click()
            print(f"点击了关注按钮 {user_id}")
            time.sleep(random.randint(2, 5))

        # 查找并点击返回按钮
        back_button = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_back")))
        back_button.click()
        print("点击了返回按钮")
        time.sleep(random.randint(2, 5))

        return True
    except TimeoutException:
        print("查找元素时超时")
        return False
    except NoSuchElementException:
        print("未找到元素")
        return False
    except Exception as e:
        print(f"执行关注操作时发生错误：{e}")
        return False

def unfollow(driver, account, follow_list):
    try:
        # 首页红包奖励
        if not popups.home_video_bonus(driver):
            return False

        # 检查首页红包奖励是否完成
        elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
        if elements:
            print("首页红包奖励未完成，执行首页红包奖励任务")
            handle_home_page_video(driver, account)
            print("首页红包奖励已完成，继续下一步")
        else:
            print("首页红包奖励已完成，继续下一步")

        # 个人页面
        my_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='我的']")))
        my_tab.click()
        print("点击我的")
        time.sleep(random.randint(2, 5))

        # 点击关注
        follow_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='关注']")))
        follow_tab.click()
        print("点击关注")
        time.sleep(random.randint(2, 5))

        # 检查是否在我的关注页面
        current_activity = utils.get_current_activity(driver)
        expected_setting_activity = "com.xiangshi.main.activity.FollowActivity"
        if expected_setting_activity not in current_activity:
            print("未能加载到我的关注，退出流程。")
            return False
        print("我的关注")

        for user_id in follow_list:
            print(f"开始取消关注 {user_id}")
            found = False

            # 遍历所有的 RelativeLayout 元素
            relative_layouts = driver.find_elements(MobileBy.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout")
            for layout in relative_layouts:
                try:
                    user_element = layout.find_element(MobileBy.XPATH, ".//android.widget.TextView[@resource-id='com.xiangshi.bjxsgc:id/id_val' and contains(@text, '" + user_id + "')]")
                    unfollow_button = layout.find_element(MobileBy.XPATH, ".//android.widget.RadioButton[@resource-id='com.xiangshi.bjxsgc:id/btn_follow']")
                    unfollow_button.click()
                    print(f"取消关注 {user_id} 成功")
                    time.sleep(random.randint(2, 5))
                    found = True
                    break
                except NoSuchElementException:
                    continue

            if not found:
                print(f"未找到享视号为 {user_id} 的关注项")

        return True

    except TimeoutException:
        print("查找元素时超时")
        return False
    except NoSuchElementException:
        print("未找到元素")
        return False
    except Exception as e:
        print(f"执行取消关注操作时发生错误：{e}")
        return False

# 点赞
def like(driver, account, follow_list):
    try:
        # 检查首页红包奖励是否完成
        elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
        if elements:
            print("首页红包奖励未完成，执行首页红包奖励任务")
            handle_home_page_video(driver, account)
            print("首页红包奖励已完成，继续下一步")
        else:
            print("首页红包奖励已完成，继续下一步")

        # 个人页面
        my_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='我的']")))
        my_tab.click()
        print("点击我的")
        time.sleep(random.randint(2, 5))

        # 点击关注
        follow_tab = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='关注']")))
        follow_tab.click()
        print("点击关注")
        time.sleep(random.randint(2, 5))

        # 检查是否在我的关注
        current_activity = utils.get_current_activity(driver)
        expected_setting_activity = "com.xiangshi.main.activity.FollowActivity"
        if expected_setting_activity not in current_activity:
            print("未能加载到我的关注，退出流程。")
            return False
        print("我的关注")

        for user_id in follow_list:
            print(f"开始点赞 {user_id}")
            try:
                # 我的关注
                my_following = driver.wait.until(EC.presence_of_element_located((MobileBy.XPATH, f"//android.widget.TextView[contains(@text, '{user_id}')]")))
                my_following.click()
                print(f"选择 {user_id}")
                time.sleep(random.randint(2, 5))

                # 检查是否在用户主页
                current_activity = utils.get_current_activity(driver)
                expected_setting_activity = "com.xiangshi.main.activity.UserHomeActivity"
                if expected_setting_activity not in current_activity:
                    print("未能加载到用户主页，退出流程。")
                    return False
                print("用户主页")

                # 选择作品
                portfolio_elements = driver.wait.until(EC.presence_of_all_elements_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/thumb")))
                if portfolio_elements:
                    # 点击第一排的第一个作品
                    first_element = portfolio_elements[0]
                    first_element.click()
                    print("点击了第一排的第一个作品")
                else:
                    print("未找到任何作品元素")
                    return False
                time.sleep(random.randint(2, 5))

                while True:
                    try:
                        # 查找并点击点赞按钮
                        like_button = driver.wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/btn_like")))
                        like_button.click()
                        print("点击了点赞按钮")
                        time.sleep(random.randint(2, 5))

                        # 检查是否存在包含“没有更多视频”文本的元素
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((MobileBy.XPATH, "//*[contains(@text, '没有更多视频')]"))
                            )
                            print("检查到'没有更多视频'文本，程序终止并返回到关注页面。")
                            break
                        except TimeoutException:
                            pass

                        # 执行滑动操作
                        utils.swipe_to_scroll(driver)

                        time.sleep(random.randint(2, 5))
                    except TimeoutException:
                        print("未找到点赞按钮或滑动操作超时，结束循环")
                        break

                # 返回到关注页面
                current_activity = utils.get_current_activity(driver)
                followactivity_activity = "com.xiangshi.main.activity.FollowActivity"
                print(f"当前页面为: {current_activity}")

                # 如果不在我的关注页，则尝试返回到主界面
                if current_activity != followactivity_activity:
                    print("不在我的关注页，尝试返回到我的关注页。")
                    max_attempts = 5
                    attempts = 0
                    while current_activity != followactivity_activity and attempts < max_attempts:
                        driver.press_keycode(AndroidKey.BACK)  # 发送物理返回键命令
                        time.sleep(random.randint(2, 5))  # 等待2秒以观察效果
                        current_activity = utils.get_current_activity(driver)  # 再次获取当前活动
                        attempts += 1
                        print(f"尝试 {attempts}: 当前页面为 {current_activity}")
                    if attempts == max_attempts:
                        print("尝试返回我的关注页失败，请手动检查")
                        return False
                else:
                    print("已在我的关注页，无需返回。")

            except TimeoutException:
                print(f"查找用户 {user_id} 的元素时超时")
                continue
            except NoSuchElementException:
                print(f"未找到用户 {user_id} 的元素")
                continue
            except Exception as e:
                print(f"执行点赞操作时发生错误：{e}")
                continue

        return True

    except TimeoutException:
        print("查找元素时超时")
        return False
    except NoSuchElementException:
        print("未找到元素")
        return False
    except Exception as e:
        print(f"执行点赞操作时发生错误：{e}")
        return False
