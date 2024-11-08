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

# 获取滑块背景图和拼图块图像
def get_slider_images(driver):
    # 等待并获取滑块验证背景图和小块图的元素
    background_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "cpc_img")]'))
    )

    small_piece_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[contains(@resource-id, "small_img")]'))
    )

    # 获取图片的Base64编码
    background_image_base64 = background_element.screenshot_as_base64
    small_piece_image_base64 = small_piece_element.screenshot_as_base64

    # 将Base64编码保存为图片文件
    with open("background.png", "wb") as f:
        f.write(base64.b64decode(background_image_base64))

    with open("small_piece.png", "wb") as f:
        f.write(base64.b64decode(small_piece_image_base64))

    print("图片已成功保存为 background.png 和 small_piece.png")

# 查找轮廓时，增加对边缘的过滤
def process_slider_images():
    # 读取图像
    background = cv2.imread('background.png')
    small_piece = cv2.imread('small_piece.png')

    if background is None or small_piece is None:
        print("无法读取图片文件")
        return

    # 转换为灰度图像
    background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    small_piece_gray = cv2.cvtColor(small_piece, cv2.COLOR_BGR2GRAY)

    # 模板匹配找到大致位置
    result = cv2.matchTemplate(background_gray, small_piece_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val > 0.5:
        h, w = small_piece_gray.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        # 提取匹配区域
        matched_area = background[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.imwrite('matched_area_optimized.png', matched_area)

        # 白色过滤
        hsv = cv2.cvtColor(matched_area, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 210])
        upper_white = np.array([180, 20, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        filtered_white = cv2.bitwise_and(matched_area, matched_area, mask=mask)
        cv2.imwrite('white_filtered_optimized.png', filtered_white)

        # 形态学操作，增强轮廓
        kernel = np.ones((3, 3), np.uint8)
        morphed_white = cv2.morphologyEx(filtered_white, cv2.MORPH_CLOSE, kernel, iterations=3)
        cv2.imwrite('morphology_result_optimized.png', morphed_white)

        # 边缘检测
        morphed_gray = cv2.cvtColor(morphed_white, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(morphed_gray, 50, 150)
        cv2.imwrite('edges_optimized.png', edges)

        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            best_match_value = float('inf')
            best_match = None

            small_piece_edges = cv2.Canny(small_piece_gray, 50, 150)
            small_piece_contours, _ = cv2.findContours(small_piece_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            small_piece_contour = max(small_piece_contours, key=cv2.contourArea)

            # 定义最小边距（如距离边缘小于10个像素则忽略）
            min_margin = 10

            # 遍历所有轮廓，找最佳匹配
            for contour in contours:
                x, y, width, height = cv2.boundingRect(contour)
                if x > min_margin and y > min_margin and (x + width < background.shape[1] - min_margin) and (y + height < background.shape[0] - min_margin):
                    match_value = cv2.matchShapes(small_piece_contour, contour, cv2.CONTOURS_MATCH_I1, 0.0)
                    if match_value < best_match_value:
                        best_match_value = match_value
                        best_match = contour

            if best_match is not None:
                # 将轮廓坐标转换为 background 图像的全局坐标
                best_match_shifted = best_match + np.array([[top_left[0], top_left[1]]])

                # 打印轮廓坐标
                print(f"轮廓坐标: {best_match_shifted}")

                # 在完整背景图上绘制轮廓
                cv2.drawContours(background, [best_match_shifted], -1, (0, 255, 0), 3)  # 红色轮廓，线条加粗
                cv2.imwrite('final_result_on_background.png', background)
                print("轮廓已在 background 上绘制，保存为 'final_result_on_background.png'")
            else:
                print("未找到合适的轮廓")
        else:
            print("未检测到任何轮廓")
    else:
        print("未找到拼图块的匹配位置")

# 主函数调用
if __name__ == '__main__':
    process_slider_images()
