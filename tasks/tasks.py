import re
import time
import random
from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from utils import utils
from popups import popups


# 首页视频任务
def handle_home_page_video(driver, wait, width, height):
    # 首页红包
    popups.home_video_bonus(driver)

    try:
        while True:
            start_time = time.time()  # 记录循环开始时间

            # 执行滑动操作
            utils.swipe_to_scroll(driver, width, height)

            # 检查首页视频红包
            popups.home_video_bonus(driver)

            # 等待页面完成加载
            WebDriverWait(driver, 60).until(
                EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/text"))
            )
            print("页面已正常加载")

            # 翻页后的随机等待时间
            random_sleep = random.randint(0, 20)
            print(f"等待 {random_sleep} 秒")
            time.sleep(random_sleep)

            # 检查首页视频红包
            popups.home_video_bonus(driver)

            # 立即检查 layer_redbag 元素是否存在
            elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")
            if elements:
                print("找到了元素，继续循环")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
            else:
                # 第一次未找到元素时，再次处理弹窗并重新检查
                print("未找到元素，再次检查弹窗")

                # 检查首页视频红包
                popups.home_video_bonus(driver)

                # 立即检查 layer_redbag 元素是否存在
                elements = driver.find_elements(MobileBy.ID, "com.xiangshi.bjxsgc:id/layer_redbag")

                # 输出循环用时
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"用时: {elapsed_time} 秒")
                if not elements:
                    print("再次检查后仍未找到元素，退出循环")
                    break
    except Exception as e:
        print(f"在滑屏循环中发生错误：{e}")
        return False

    return True

# 资产页奖励任务
def collect_rewards(driver, wait, width, height, account):
    # 首页红包
    popups.home_video_bonus(driver)

    # 跳转到资产页
    assets_element = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='资产']")))
    assets_element.click()
    print("已找到并点击‘资产’。")
    time.sleep(random.randint(2, 5))

    # 每日股东分红
    popups.daily_dividend_distribution(driver, wait, width, height)

    # 点击领取
    try:
        while True:
            start_time = time.time()  # 记录循环开始时间

            # 整点红包
            popups.hourly_bonus(driver, wait, width, height)

            try:
                miss_bubble_element = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_miss_bubble")))
                click_to_collect_text = miss_bubble_element.text
                current, total = map(int, click_to_collect_text.replace(" ", "").strip('()').split('/'))

                if current >= total:
                    print("所有任务奖励已领取完毕。")
                    break

                receive_bubble = wait.until(EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_receive_bubble")))
                receive_bubble.click()
                print(f"点击了领取按钮，更新剩余次数：{current + 1}/{total}")

                if not handle_display_page(driver, wait, width, height):  # 处理展示页的逻辑
                    return False

                time.sleep(random.randint(1, 5))

                # 输出循环用时
                elapsed_time = round(time.time() - start_time, 2)
                print(f"用时: {elapsed_time} 秒")

            except StaleElementReferenceException:
                print("元素不再存在于 DOM 中，重新获取元素。")
                continue

    except (TimeoutException, NoSuchElementException):
        print("找不到 txt_miss_bubble 或 txt_receive_bubble 元素，无法点击。")

    # 领取奖励
    base_xpaths = [
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView",
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.FrameLayout[{i}]/android.widget.LinearLayout/android.widget.ImageView"
    ]

    last_successful_index = 1  # 从最后一次成功的位置开始
    while True:
        start_time = time.time()  # 记录循环开始时间

        # 整点红包
        if popups.hourly_bonus(driver, wait, width, height):
            print("已领取整点红包")
            # return True

        found = False
        for i in range(last_successful_index, 7):  # 假设有6个奖励按钮
            for base_xpath in base_xpaths:
                xpath = base_xpath.format(i=i)  # 动态生成每个按钮的 XPath
                try:
                    reward = wait.until(EC.presence_of_element_located((MobileBy.XPATH, xpath)))
                    if reward.get_attribute("selected") == "true":
                        reward.click()
                        print(f"点击了位于 {i} 的领取奖励，使用的XPath为: {xpath}")
                        if not handle_display_page(driver, wait, width, height):  # 处理展示页的逻辑
                            return False
                        last_successful_index = i + 1  # 更新最后成功的索引
                        found = True
                        break  # 成功点击后退出内循环
                except TimeoutException:
                    print(f"未能及时找到位于 {i} 的领取奖励，路径：{xpath}")
                except NoSuchElementException:
                    print(f"未能定位到位于 {i} 的领取奖励，路径：{xpath}")
                except Exception as e:
                    print(f"尝试点击位于 {i} 的领取奖励时发生异常，路径：{xpath}")
            if found:
                break  # 成功点击后退出外循环

        if not found:
            print("未找到任何选中的‘领取奖励’按钮，所有奖励领取完毕。")
            break

        time.sleep(random.randint(1, 5))

        # 输出循环用时
        elapsed_time = round(time.time() - start_time, 2)
        print(f"用时: {elapsed_time} 秒")

    # 获取并存储“我的享币”和“我的享点”
    utils.get_and_store_points(driver, account)

    return True

# 互助奖励任务
def mutual_assistance_reward(driver, wait, width, height):
    # 首页红包
    popups.home_video_bonus(driver)

    # 获取当前活动并检查是否已经在主界面
    current_activity = utils.get_current_activity()
    expected_main_activity = "com.xiangshi.main.activity.MainActivity"
    print(f"当前页面为: {current_activity}")

    # 如果不在主界面，则尝试返回到主界面
    if current_activity != expected_main_activity:
        print("不在主界面，尝试返回到主界面。")
        max_attempts = 5
        attempts = 0
        while current_activity != expected_main_activity and attempts < max_attempts:
            driver.press_keycode(AndroidKey.BACK)  # 发送物理返回键命令
            time.sleep(random.randint(2, 5))  # 等待2秒以观察效果
            current_activity = utils.get_current_activity()  # 再次获取当前活动
            attempts += 1
            print(f"尝试 {attempts}: 当前页面为 {current_activity}")
        if attempts == max_attempts:
            print("尝试返回主界面失败，请手动检查")
            return False
    else:
        print("已在主界面，无需返回。")

    # 个人页面
    my_tab = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='我的']")))
    my_tab.click()
    print("点击我的")
    time.sleep(random.randint(2, 5))

    # 点击关注
    follow_tab = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='关注']")))
    follow_tab.click()
    print("点击关注")
    time.sleep(random.randint(2, 5))

    # 检查是否在我的关注
    current_activity = utils.get_current_activity()
    expected_setting_activity = "com.xiangshi.main.activity.FollowActivity"
    if expected_setting_activity not in current_activity:
        print("未能加载到我的关注，退出登出流程。")
        return False
    print("我的关注")

    # 我的关注
    my_following = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "//android.widget.TextView[@text='罗亿凡（万股）']")))
    my_following.click()
    print("选择罗亿凡")
    time.sleep(random.randint(2, 5))

    # 检查是否在用户主页
    current_activity = utils.get_current_activity()
    expected_setting_activity = "com.xiangshi.main.activity.UserHomeActivity"
    if expected_setting_activity not in current_activity:
        print("未能加载到用户主页，退出登出流程。")
        return False
    print("用户主页")

    # 选择作品
    portfolio_elements = wait.until(EC.presence_of_all_elements_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/thumb")))
    if portfolio_elements:
        selected_element = random.choice(portfolio_elements)
        selected_element.click()
        print("随机点击一个作品")
    else:
        print("未找到任何作品元素")
    time.sleep(random.randint(2, 5))

    while True:
        start_time = time.time()  # 记录循环开始时间

        # 检查激励广告
        try:
            reward_layer = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((MobileBy.ID, "com.xiangshi.bjxsgc:id/txt_reward_ad"))
            )
            time.sleep(random.randint(2, 5))
            reward_layer.click()
            print("点击了激励广告")

            time.sleep(2)
            WebDriverWait(driver, 120).until(
                EC.invisibility_of_element_located((MobileBy.XPATH, "//*[contains(@text, '加载中')]"))
            )
            print("页面已正常加载")

            # 检查头像是否消失
            try:
                WebDriverWait(driver, 2).until(
                    EC.invisibility_of_element_located((MobileBy.ID, "com.xiangshi.bjxsgc:id/avatar"))
                )
                print("没检查到头像，加载展示页。")
                handle_display_page(driver, wait, width, height)
                # 检查是否存在包含“每日”文本的元素
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((MobileBy.XPATH, "//*[contains(@text, '每日20次')]"))
                    )
                    print("检测到'每日20次'文本，程序终止并退出到系统桌面。")
                    break
                except TimeoutException:
                    print("未检测到'每日20次'文本，继续执行。")
            except TimeoutException:
                print("检查到头像，继续执行滑动操作。")
        except Exception as e:
            print("未找到或不可点击激励广告。")

        # 首页红包
        popups.home_video_bonus(driver)

        # 执行滑动操作
        utils.swipe_to_scroll(driver, width, height)

        time.sleep(random.randint(2, 5))

        # 输出循环用时
        elapsed_time = round(time.time() - start_time, 2)
        print(f"用时: {elapsed_time} 秒")

    return True

# 展示页
def handle_display_page(driver, wait, width, height):
    try:
        start_time = time.time()
        timeout = 70
        popup_texts = ["放弃", "离开", "取消"]

        while time.time() - start_time < timeout:
            # 展示页弹窗
            popups.display_page_popup(driver, popup_texts)

            # 检查返回按钮
            # utils.check_back_button(driver, width, height)

            # 检查倒计时是否消失
            try:
                element_to_wait = None
                # print("开始检查倒计时...")

                # 第一种检查倒计时的方法
                text_views = driver.find_elements(By.XPATH, "//android.widget.TextView[contains(@text, 's')]")
                if text_views:
                    for text_view in text_views:
                        location = text_view.location
                        size = text_view.size
                        top_y = location['y']
                        # print(f"检查元素: 文本='{text_view.text}', 位置='{location}', 大小='{size}'")
                        if top_y < height * 0.15:
                            element_to_wait = text_view
                            # print(f"找到倒计时元素: {element_to_wait.text}")
                            break

                    if element_to_wait and isinstance(element_to_wait, WebElement):
                        try:
                            # print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                            WebDriverWait(driver, 3).until(
                                lambda driver: not element_to_wait.is_displayed() or re.match(r"0\s*s?", element_to_wait.text) is not None
                            )
                            print("倒计时结束。")
                            break  # 结束while循环
                        except TimeoutException:
                            # print("等待倒计时结束超时（第一种方法）。")
                            continue  # 继续while循环
                        except StaleElementReferenceException:
                            # print("倒计时元素在DOM中已不可访问。")
                            break  # 结束while循环

                else:
                    # 第二种检查倒计时的方法（长度为1或2的纯数字倒计时）
                    text_views = driver.find_elements(By.XPATH, "//android.widget.TextView[string-length(@text) <= 2 and @text = number(@text)]")
                    if text_views:
                        for text_view in text_views:
                            location = text_view.location
                            size = text_view.size
                            top_y = location['y']
                            # print(f"检查元素: 文本='{text_view.text}', 位置='{location}', 大小='{size}'")
                            if top_y < height * 0.15:
                                element_to_wait = text_view
                                # print(f"找到倒计时元素: {element_to_wait.text}")
                                break

                        if element_to_wait and isinstance(element_to_wait, WebElement):
                            try:
                                # print(f"等待倒计时元素消失前的状态: 可见性={element_to_wait.is_displayed()}, 文本='{element_to_wait.text}'")
                                WebDriverWait(driver, 3).until(
                                    lambda driver: not element_to_wait.is_displayed() or element_to_wait.text == '0'
                                )
                                print("倒计时结束。")
                                break  # 结束while循环
                            except TimeoutException:
                                # print("等待倒计时结束超时（第二种方法）。")
                                continue  # 继续while循环
                                # except StaleElementReferenceException:
                                # print("倒计时元素在DOM中已不可访问。")
                                break  # 结束while循环

                    else:
                        # 检查其他可能的倒计时元素
                        countdown_element = driver.find_elements(By.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")
                        if countdown_element:
                            element_to_wait = countdown_element[0]
                            try:
                                WebDriverWait(driver, 3).until(EC.invisibility_of_element_located((By.ID, "com.xiangshi.bjxsgc:id/anythink_myoffer_count_down_view_id")))
                                print("特定ID的倒计时元素已消失。")
                                break  # 结束while循环
                            except TimeoutException:
                                # print("等待特定ID倒计时元素消失超时。")
                                continue  # 继续while循环
                                # 如果所有检查方法都未找到倒计时元素，跳出while循环

                if element_to_wait is None:
                    print("未找到倒计时元素，可能页面已刷新。")
                    break  # 结束while循环

            except NoSuchElementException:
                print("未找到倒计时元素。")
                continue  # 继续while循环
            except Exception as e:
                print(f"发生错误: {str(e)}")
                break  # 结束while循环

        # 展示页弹窗
        popups.display_page_popup(driver, popup_texts)

        # 调用点击元素函数
        if not utils.click_close_button(driver, wait, width, height):
            return False

    except TimeoutException as e:
        print("处理展示页时发生超时异常: ", str(e))
        return False
    except Exception as e:
        print("处理展示页时发生错误: ", str(e))
        return False
    return True
