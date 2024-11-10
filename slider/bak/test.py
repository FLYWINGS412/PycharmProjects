import cv2
import numpy as np

def process_slider_images():
    # 读取图片
    image = cv2.imread('background.png')

    # 转换为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化
    threshold_value = 235  # 调整阈值以获得不同的效果
    _, binary_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    # 查找轮廓
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    cv2.imwrite('binary_result.png', binary_image)
    cv2.imwrite('contour_result_filtered.png', contour_image)
    print("二值化结果已保存为 'binary_result.png'")
    print("带目标轮廓的图像已保存为 'contour_result_filtered.png'")

process_slider_images()
