import cv2
import base64
import numpy as np
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置参数
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '9',
    'deviceName': '01',
    'udid': 'emulator-5628',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,
    'noReset': True,
}

# # 获取滑块背景图和拼图块图像
# def get_slider_images(driver):
#     # 等待并获取滑块验证背景图和小块图的元素
#     background_element = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "cpc_img")]'))
#     )
#
#     small_piece_element = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "small_img")]'))
#     )
#
#     # 获取图片的Base64编码
#     background_image_base64 = background_element.screenshot_as_base64
#     small_piece_image_base64 = small_piece_element.screenshot_as_base64
#
#     # 将Base64编码保存为图片文件
#     with open("background.png", "wb") as f:
#         f.write(base64.b64decode(background_image_base64))
#
#     with open("small_piece.png", "wb") as f:
#         f.write(base64.b64decode(small_piece_image_base64))
#
#     print("图片已成功保存为 background.png 和 small_piece.png")

# 提取有效图片轮廓
def extract_target_contour(image_path, output_prefix='result', threshold_value=190):
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片文件: {image_path}")
        return None

    # 转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    # 查找轮廓
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 设置最小边距，排除靠近边缘的轮廓
    min_margin = 5
    height, width = binary_image.shape
    valid_contours = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # 检查轮廓是否靠近图像边缘
        if x > min_margin and y > min_margin and (x + w < width - min_margin) and (y + h < height - min_margin):
            valid_contours.append(contour)

    # 在原图上绘制有效的轮廓
    contour_image = image.copy()
    cv2.drawContours(contour_image, valid_contours, -1, (0, 255, 0), 2)  # 使用绿色描边

    # 保存结果
    cv2.imwrite(f'{output_prefix}_binary.png', binary_image)
    cv2.imwrite(f'{output_prefix}_contour.png', contour_image)
    print(f"二值化结果已保存为 '{output_prefix}_binary.png'")
    print(f"带目标轮廓的图像已保存为 '{output_prefix}_contour.png'")

    return valid_contours

# 处理小块图像的函数
def process_small_piece():
    return extract_target_contour('small_piece.png', output_prefix='small_piece', threshold_value=235)

# 处理背景图像的函数
def process_background():
    return extract_target_contour('background.png', output_prefix='background', threshold_value=190)

# 调用函数
small_piece_contour = process_small_piece()
background_contour = process_background()