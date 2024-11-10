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
    'udid': 'emulator-5658',
    'automationName': 'UiAutomator2',
    'settings[waitForIdleTimeout]': 10,
    'settings[waitForSelectorTimeout]': 10,
    'newCommandTimeout': 21600,
    'ignoreHiddenApiPolicyError': True,
    'dontStopAppOnReset': True,
    'noReset': True,
}

# # 初始化Appium driver连接
# driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
#
# # 获取滑块背景图和拼图块图像
# def get_slider_images():
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

    return valid_contours, image

# 处理小块图像的函数
def process_small_piece():
    contours, contour_image = extract_target_contour('small_piece.png', output_prefix='small_piece', threshold_value=240)
    if contours:
        # 根据面积和形状过滤小块轮廓，找出最接近目标的轮廓
        target_contour = max(contours, key=cv2.contourArea)
        return target_contour, contour_image
    return None, None

# 处理背景图像的函数
def process_background():
    return extract_target_contour('background.png', output_prefix='background', threshold_value=190)

# 匹配轮廓并加强相似度和 Y 坐标过滤
def match_multiple_contours(small_contour, background_contours, background_image, score_threshold=0.1, area_tolerance=0.1, y_tolerance=10):
    matches = []
    match_result_image = background_image.copy()

    # 获取小块轮廓的面积和中心点 Y 坐标，以便后续进行面积和 Y 坐标的比对
    small_contour_area = cv2.contourArea(small_contour)
    _, _, _, small_center_y = cv2.boundingRect(small_contour)

    for contour in background_contours:
        # 使用 Hu 矩特征计算形状相似度
        score = cv2.matchShapes(small_contour, contour, cv2.CONTOURS_MATCH_I1, 0.0)
        contour_area = cv2.contourArea(contour)

        # 获取当前背景轮廓的中心点 Y 坐标
        _, _, _, contour_center_y = cv2.boundingRect(contour)

        # 计算面积差，排除面积不在容差范围内的轮廓
        area_diff_ratio = abs(contour_area - small_contour_area) / small_contour_area

        # 双重条件过滤：形状相似度、面积比对和 Y 坐标
        if score < score_threshold and area_diff_ratio < area_tolerance and abs(contour_center_y - small_center_y) < y_tolerance:
            matches.append((contour, score))

    # 绘制所有符合条件的匹配轮廓
    for match_contour, score in matches:
        cv2.drawContours(match_result_image, [match_contour], -1, (0, 255, 0), 2)

    # 保存匹配结果
    cv2.imwrite("best_match_result.png", match_result_image)
    print("最佳匹配结果已保存为 'best_match_result.png'")
    print("找到的匹配轮廓数量：", len(matches))

    return matches

# 调用函数
small_piece_contour, small_piece_image = process_small_piece()
background_contours, background_image = process_background()

# 进行多重匹配
if small_piece_contour is not None and background_contours:
    match_multiple_contours(small_piece_contour, background_contours, background_image, score_threshold=0.1, area_tolerance=0.1, y_tolerance=10)