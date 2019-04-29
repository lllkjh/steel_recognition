from kafka import KafkaProducer
import cv2
import json
import sys
import imutils
from imutils.video import VideoStream
import time
import base64
import numpy as np
import argparse

VIDEO_PATH = 'E:/CISDI/1.mp4'

parser = argparse.ArgumentParser()
parser.add_argument('-P', '--path', default=VIDEO_PATH)
cmdline_args = parser.parse_args()

topic = 'video_test'
producer = KafkaProducer(bootstrap_servers='47.100.26.79:9092')

cap = cv2.VideoCapture(cmdline_args.path)
# vs = VideoStream(src=0).start()
# time.sleep(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # frame = vs.read()
    # frame = imutils.resize(frame, width=800)
    _, img_encode = cv2.imencode('.jpg', frame)
    str_encode = np.array(img_encode).tostring()
    img_base64 = base64.b64encode(str_encode)

    millis = int(round(time.time() * 1000))

    msg_dict = {
        "cameraId": "1",
        "position": "开卷机",
        "timestamp": millis,
        "data": str(img_base64, 'ASCII')
    }
    message = json.dumps(msg_dict).encode('utf-8')
    # send to kafka topic
    future = producer.send(topic, message)
    print(future.get())
    # print(message)
    print(sys.getsizeof(message))

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# vs.stop()
producer.flush()
producer.close()
