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

# 提取有效图片轮廓，进行多重阈值测试并优化选择
def extract_target_contour(image_path, output_prefix, threshold_values, area_range, target_contour=None):
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片文件: {image_path}")
        return None, None

    # 转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    best_contour = None
    best_contour_area = 0
    best_binary_image = None
    best_score = float('inf')
    best_threshold = None

    # 多重阈值测试，从最大值到最小值
    for threshold_value in threshold_values:
        _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            contour_area = cv2.contourArea(contour)
            # 检查轮廓面积是否在指定范围内
            if area_range[0] <= contour_area <= area_range[1]:
                # 计算轮廓复杂度和形状相似性（如果目标轮廓存在）
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)  # 近似多边形
                complexity = len(approx)

                # 形状相似性评分
                shape_similarity = 0
                if target_contour is not None:
                    shape_similarity = cv2.matchShapes(target_contour, contour, cv2.CONTOURS_MATCH_I1, 0.0)

                # 综合评分：面积、复杂度、形状相似性
                score = abs(complexity - 4) + abs(best_contour_area - contour_area) + shape_similarity

                # 更新最佳轮廓
                if score < best_score or (score == best_score and contour_area > best_contour_area):
                    best_score = score
                    best_contour = contour
                    best_contour_area = contour_area
                    best_binary_image = binary_image.copy()
                    best_threshold = threshold_value  # 记录最佳阈值

    # 在原图上绘制最佳轮廓
    if best_contour is not None:
        contour_image = image.copy()
        cv2.drawContours(contour_image, [best_contour], -1, (0, 255, 0), 2)
        cv2.imwrite(f'{output_prefix}_best_binary.png', best_binary_image)
        cv2.imwrite(f'{output_prefix}_best_contour.png', contour_image)
        print(f"最佳轮廓已保存为 '{output_prefix}_best_contour.png'，选用阈值: {best_threshold}")
    else:
        print("未找到符合条件的轮廓")

    return best_contour, best_binary_image

# 调用此函数时，确保 threshold_values 按从大到小顺序传入
small_piece_contour, small_piece_image = extract_target_contour(
    'small_piece.png',
    output_prefix='small_piece',
    threshold_values=[250, 240, 230, 220, 210, 200, 190, 180],
    area_range=(500, 5000)
)

background_contour, background_image = extract_target_contour(
    'background.png',
    output_prefix='background',
    threshold_values=[250, 240, 230, 220, 210, 200, 190, 180],
    area_range=(500, 5000),
    target_contour=small_piece_contour
)

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

# 调用匹配函数
if small_piece_contour is not None and background_contour is not None:
    match_multiple_contours(small_piece_contour, [background_contour], background_image, score_threshold=0.1, area_tolerance=0.1, y_tolerance=10)
