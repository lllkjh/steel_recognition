import base64
import json
import time
import cv2
from kafka import KafkaProducer
import numpy as np

user_name = ["admin", "admin", "admin"]
password = ["cisdi123456", "cisdi123456", "cisdi123456"]
address = ["192.168.3.102", "192.168.3.102", "192.168.3.102"]


def start_camera(camera_id):
    if camera_id == 100:  # 100 for testing PC camera
        cap = cv2.VideoCapture(0)
    else:
        # cap = cv2.VideoCapture("rtsp://" + user_name[camera_id] + ":" + password[camera_id] + "@" + address[
        #     camera_id] + ":554//h264/ch33/main/av_stream")
        cap = cv2.VideoCapture('1.mp4')
    yield cap

    producer = KafkaProducer(bootstrap_servers='47.100.26.79:9092')
    topic = 'video_test'
    while 1:
        ret, frame = cap.read()
        _, img_encode = cv2.imencode('.jpg', frame)
        str_encode = np.array(img_encode).tostring()
        img_base64 = base64.b64encode(str_encode)

        millis = int(round(time.time() * 1000))

        msg_dict = {
            "cameraId": camera_id,
            "position": "开卷机",
            "timestamp": millis,
            "data": str(img_base64, 'ASCII')
        }
        message = json.dumps(msg_dict).encode('utf-8')
        # send to kafka topic
        # future = producer.send(topic, message)
        # print(future.get())

        print(camera_id)  # for debug


def stop_camera(capture):
    capture.release()
