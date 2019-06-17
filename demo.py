# -*- coding: utf-8 -*-
"""
author: pangsy
date: 25th March 2019
"""
import os
import cv2
from utils import *

# signal
NO_STEEL_FLAG = True
NO_STEEL_count = 0
NO_STEEL_count_threshold = 10

input_dir = '1.mp4'
output_dir = 'result.avi'
window_name = 'result'

# get the total number of frames
frame_number = 0
frame_count = 0
frame_rate = 0

# # Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
# out = cv2.VideoWriter(output_dir, fourcc, frame_rate, (960,540))
# print('result video saved in:' + output_dir)

# callback function of trackbar
# read the frame loaction from the value of trackbar
trackbarname = 'frame number'


def get_current_frame(obj):
    global trackbarname, trackbarname, frame_rate
    frame_location = cv2.getTrackbarPos(trackbarname, window_name)
    # print(frame_location*frame_rate)
    # video.set(cv2.CAP_PROP_POS_FRAMES, frame_location*frame_rate)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_location)


# # create a trackbar to control the location of a frame on this video
# cv2.namedWindow(window_name)
# cv2.createTrackbar(trackbarname, window_name, 0, frame_number, get_current_frame)
# cv2.setTrackbarPos(trackbarname, window_name, 43000)
def run(frame):
    global NO_STEEL_FLAG, NO_STEEL_count, NO_STEEL_count_threshold
    # get the height and width of a frame
    (h, w) = frame.shape[:2]
    # # print(h,w)
    # w = w // 2
    # h = h // 2
    # frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
    # print(w,h)
    # cv2.imshow(window_name,frame)
    # -----------------------------------image processing part-----------------------------------------
    # setting ROI
    image = frame[h // 2:h, w // 3:w]
    # change into gray image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_analysis = image.copy()
    # binary
    threshold, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)

    # 计算白色区域占比
    ratio = calculate_white_ratio(image)
    # ratio = 0.3
    # 根据上述比值确定是否开始检测工作
    if ratio >= 0.35:
        cv2.rectangle(frame, (w // 3, h // 2), (w, h), (255, 0, 0), 2)
        return False, frame, False
    else:
        warning = False
        cv2.rectangle(frame, (w // 3, h // 2), (w, h), (0, 255, 0), 10)
        cv2.rectangle(frame, (w // 3 - 5, h // 2 - 40), (w // 3 + 400, h // 2), (0, 255, 0), -1)
        cv2.putText(frame, 'DETECTING PROCESSING', (w // 3, h // 2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        if NO_STEEL_FLAG:
            NO_STEEL_count = 0
        # Canny边缘检测
        # image_analysis = cv2.GaussianBlur(image_analysis,(3,3),0)
        image_analysis = cv2.Canny(image_analysis, 25, 75)
        # 膨胀
        kernel = np.ones((35, 35), np.uint8)
        image_analysis = cv2.dilate(image_analysis, kernel)
        # 中值滤波
        # image_analysis = cv2.medianBlur(image_analysis, 35)
        # 去除画面边缘杂光影响
        (h_, w_) = image_analysis.shape[:2]
        cv2.rectangle(image_analysis, (0, 0), (w_, h_), (255, 255, 255), 50)
        # # 腐蚀
        # image_analysis = cv2.erode(image_analysis, kernel)
        # 找到带钢中心点和外接框并标出
        centre_points, boxes = draw_center_point(image_analysis, h, w)
        for centre_point in centre_points:
            (x, y) = centre_point
            # print(x,y)
            # cv2.circle(frame,(x+w//3,y+h//2),3,(0,0,255),5)
        if len(boxes) > 0:
            for box in boxes:
                # print(box)
                NO_STEEL_FLAG = True
                for point in box:
                    point[0] = point[0] + w // 3
                    point[1] = point[1] + h // 2
                frame = cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)
        # 连续NO_STEEL_count_threshold帧以上没有出钢，则报警
        elif NO_STEEL_count >= NO_STEEL_count_threshold:
            cv2.rectangle(frame, (w // 3, h // 2), (w, h), (0, 0, 255), 10)
            cv2.putText(frame, 'NO STEEL', (w // 3 + 5, h // 2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            NO_STEEL_count = NO_STEEL_count + 1
            print('warning')
            # NO_STEEL_FLAG = False
            warning = True
        else:
            NO_STEEL_count = NO_STEEL_count + 1
            # print(NO_STEEL_count)
            NO_STEEL_FLAG = False
        return NO_STEEL_FLAG, frame, warning


if __name__ == '__main__':
    # load the video file
    video = cv2.VideoCapture(input_dir)
    # check if video loaded successfully
    if not video.isOpened():
        print('Error loading video file')

    # get the total number of frames
    frame_number = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    while video.isOpened():
        # capture video frame-by-frame
        ret, frame = video.read()

        if ret:
            NO_STEEL_FLAG, frame = run(frame)
            frame = cv2.resize(frame, (800, 450))
            cv2.imshow(window_name, frame)
            # cv2.imshow('image_processing',image_analysis)
            # out.write(frame)
            # ----------------------------------------------------------------------------

            if cv2.waitKey(1) == 27:
                break
        else:
            break

    video.release()
    # out.release()
    cv2.destroyAllWindows()
