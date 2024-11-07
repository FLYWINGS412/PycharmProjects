import time
import pygame
import threading
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.extensions.android.nativekey import AndroidKey

# 刷新页面
def refresh_page(driver):
    try:
        loading_state_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'com.mmbox.xbrowser:id/btn_loading_state'))
        )
        loading_state_button.click()
        print("页面已刷新")
        time.sleep(8)  # 等待页面加载完成
    except Exception as e:
        print(f"刷新页面失败")

# 音乐循环播放的函数
def play_music_loop():
    pygame.mixer.init()
    pygame.mixer.music.load("song.mp3")
    pygame.mixer.music.play(-1)  # -1 表示无限循环播放

# 默认配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'udid': 'emulator-5556',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,
    'noReset': True,
}

# 启动 Appium 驱动
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

refresh_page(driver)

# 定位 dp-main 父容器
try:
    main_view = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "dp-main")]'))
    )
    print("成功找到dp-main父容器")
except Exception as e:
    print(f"未找到dp-main父容器")
    # continue

# 获取任务
while True:
    # 在 dp-main 父容器下查找并点击 "获取任务" 按钮
    try:
        time.sleep(5)
        Get_Task = WebDriverWait(main_view, 5).until(
            EC.presence_of_element_located((By.XPATH, './/android.widget.Button[@text="获取任务"]'))
        )

        Get_Task.click()
        print("成功点击'获取任务'按钮")
    except Exception as e:
        print(f"点击'获取任务'按钮失败")

    # 检查获取任务弹窗
    try:
        time.sleep(10)
        # 查找包含消息的弹窗元素
        message_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "android:id/message")]'))
        )

        # 打印弹窗消息的文本内容
        print("弹窗信息:", message_button.text)

        # 检测到弹窗后执行返回操作并等待
        print("执行返回并等待 10 分钟。")
        driver.press_keycode(AndroidKey.BACK)  # 按下返回键关闭弹窗
        time.sleep(600)  # 等待 10 分钟后继续
        continue

    except Exception:
        print("未检测到获取任务弹窗，继续任务。")

    # 查找并获取 dp-main 父容器下 "店铺名称"
    try:
        shop_name_view = WebDriverWait(main_view, 5).until(
            EC.presence_of_element_located((By.XPATH, './/android.view.View[6]'))
        )
        target_shop_name = shop_name_view.text  # 获取店铺名称
        print(f"成功找到店铺: {target_shop_name}")

        # 如果店铺名称只有 "-"，重新获取任务
        if target_shop_name == "-":
            print("检测到店铺名称为 '-'，重新获取任务")
            continue  # 重新开始 while 循环，跳过后续操作
        else:
            print("成功获取任务")
            # 启动循环播放音乐的线程
            music_thread = threading.Thread(target=play_music_loop, daemon=True)
            music_thread.start()
            break  # 店铺名称不为 '-'，跳出循环，执行后续任务

    except Exception as e:
        print(f"获取店铺名称失败")