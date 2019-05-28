import base64
import json
import logging
import threading
import time
import cv2
import configparser
from kafka import KafkaProducer
from kafka.errors import KafkaError


class CameraThread(threading.Thread):
    def __init__(self, camera_id, topic, in_use):
        super(CameraThread, self).__init__()
        self._stop_event = threading.Event()
        self.camera_id = camera_id
        self.topic = topic
        self.in_use = in_use
        self.started = False

    def stop(self):
        self._stop_event.set()

    def _stopped(self):
        return self._stop_event.is_set()

    def run(self):
        # TODO  Confirm camera connection method
        conf = configparser.ConfigParser()
        conf.read('config.ini', encoding='utf-8')
        servers = conf.get('kafka', 'servers')
        # producer = KafkaProducer(bootstrap_servers=servers)
        # Connect to the camera
        cap = self.get_camera(self.camera_id, conf)
        # check if camera is opened
        # while 1:
        #     if cap.isOpened():
        self.started = True
        logging.warning('Cam {0} start'.format(self.camera_id))
                # break
        # --------------------------
        while not self._stopped():
            if self.in_use:
                start = time.time()
                ret, frame = cap.read()
                end_1 = time.time()
                print('time for image read {0}'.format(end_1 - start))
                if ret:
                    # showing the image for testing
                    cv2.imshow(self.topic + str(self.camera_id), cv2.resize(frame, (800, 450)))
                    if cv2.waitKey(5) == 27:
                        break
                    end_2 = time.time()
                    print('time for image show {0}'.format(end_2 - end_1))
                    # encode the image and send to Kafka
                    _, img_encode = cv2.imencode('.jpg', frame)
                    img_base64 = base64.b64encode(img_encode)
                    millis = int(round(time.time() * 1000))
                    msg_dict = {
                        "cameraId": self.camera_id,
                        "position": conf.get('position', str(self.camera_id)),
                        "timestamp": millis,
                        "data": str(img_base64, 'ASCII')
                    }
                    message = json.dumps(msg_dict).encode('utf-8')
                    end_3 = time.time()
                    print('time for encode {0}'.format(end_3 - end_2))
                    # print(message.decode())  # for debug
                    # try:
                    #     producer.send(self.topic, message)
                    # except KafkaError as e:
                    #     logging.error(e)
                else:
                    logging.warning('Video {0} not available, reconnecting ... '.format(self.camera_id))
                    cap = self.get_camera(self.camera_id, conf)
                end = time.time()
                seconds = end - start
                fps = int(1 / seconds)
                logging.warning("Estimated frames per second : {0}".format(fps))
        cap.release()
        # cv2.destroyAllWindows()
        cv2.destroyWindow(self.topic + str(self.camera_id))
        print('Cam {0} quit'.format(self.camera_id))

    @staticmethod
    def get_camera(cam_id, configure):
        # test code using PC camera and mp4 file
        # if cam_id == 2:  # 2 for testing PC camera
        #     capture = cv2.VideoCapture(0)
        # elif cam_id == 1000:  # 1000 for test video
        #     capture = cv2.VideoCapture('1.mp4')
        # # ----------------------------------------
        # else:
        source = configure.get('camera', str(cam_id))
        capture = cv2.VideoCapture(source)
        return capture
