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
    'dontStopAppOnReset': True,  # 保持浏览器运行状态
    # 'unicodeKeyboard': False,
    # 'resetKeyboard': False,
    'noReset': True,  # 不重置应用
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

# 提取面积最大的有效轮廓并保存结果的函数
def extract_target_contour(image_path, output_path='contour_result.png', threshold_value=230, use_adaptive=False):
    min_margin = 10  # 固定的最小边距

    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print("无法读取图片文件")
        return None

    # 转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用对比度有限的自适应直方图均衡化（CLAHE）
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_image = clahe.apply(gray_image)

    # 高斯模糊
    blurred_image = cv2.GaussianBlur(enhanced_image, (7, 7), 0)

    # 二值化
    if use_adaptive:
        binary_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 11, 2)
    else:
        _, binary_image = cv2.threshold(blurred_image, threshold_value, 255, cv2.THRESH_BINARY)

    # 可选的腐蚀操作，去除小噪声
    binary_image = cv2.erode(binary_image, None, iterations=1)

    # 保存二值化图像
    binary_output_path = output_path.replace('.png', '_binary.png')
    cv2.imwrite(binary_output_path, binary_image)
    print(f"二值化结果已保存为 '{binary_output_path}'")

    # 查找轮廓
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 设置图像的宽高，排除靠近边缘的轮廓
    height, width = binary_image.shape
    valid_contours = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if x > min_margin and y > min_margin and (x + w < width - min_margin) and (y + h < height - min_margin):
            valid_contours.append(contour)

    # 在原图上绘制所有有效的轮廓
    if valid_contours:
        contour_image = image.copy()
        cv2.drawContours(contour_image, valid_contours, -1, (0, 255, 0), 2)  # 使用绿色描边

        # 保存带有轮廓的结果图像
        cv2.imwrite(output_path, contour_image)
        print(f"带有目标轮廓的图像已保存为 '{output_path}'")

        return valid_contours  # 返回所有有效的轮廓
    else:
        print("未找到有效的目标轮廓")
        return None

# 调用小块和背景函数
small_piece_contour = extract_target_contour('small_piece.png', 'small_piece_contour.png', threshold_value=220, use_adaptive=True)
background_contour = extract_target_contour('background.png', 'background_contour.png', threshold_value=195)
