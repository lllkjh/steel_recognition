# -*- coding: utf-8 -*-
"""
author: pangsy
date: 25th March 2019
"""

import os
import cv2
import numpy as np


# function: calculate the ratio of (white area/whole area)
# input: binary image
def calculate_white_ratio(binary):
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(binary,contours,-1,(0,0,255),3)
    # cv2.imshow('test result',binary)
    # cv2.waitKey(1)

    # calculate the total area of contours
    total_white_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        total_white_area = total_white_area + area

    # calculate the area ratio
    (h, w) = binary.shape[:2]
    total_area = h * w
    ratio = total_white_area / total_area
    ratio = np.round(ratio, 2)
    # print(ratio)

    return ratio


# function: get the centre point of white area
# input: binary image
def draw_center_point(binary, h, w):
    binary = cv2.bitwise_not(binary, binary)  # 反转黑白
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(binary,contours,-1,(0,0,255),3)
    # cv2.imshow('test result',binary)
    # cv2.waitKey(1)

    centre_points = []
    boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1500 * w * h / (1920 * 1080 / 4):
            # 找到中心点
            Moments = cv2.moments(contour)
            # print(Moments)
            m00 = Moments['m00']
            m01 = Moments['m01']
            m10 = Moments['m10']
            m11 = Moments['m11']
            if m00 != 0:
                x = int(m10 / m00)
                y = int(m01 / m00)
                if 100 * w / (1920 / 2) <= x <= 500 * w / (1920 / 2):
                    # print(x,y)
                    centre_points.append((x, y))

            # 框出矩形框
            rect = cv2.minAreaRect(contour)
            # 返回 Box2D结构，包括了左上角坐标(x,y),(width, height)和旋转角度
            box = cv2.boxPoints(rect)  # Rectangle的四个角
            box = np.int0(box)
            boxes.append(box)

    return centre_points, boxes
