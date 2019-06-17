# coding=utf-8
import base64
import json
import logging
import time
import cv2
from kafka import KafkaProducer
from kafka.errors import KafkaError
from camera_thread import CameraThread
import read_signal
import steel_detection
import configparser
import queue
import threading

conf = configparser.ConfigParser()
conf.read('config.ini', encoding='utf-8')
is_demo = conf.getboolean('env', 'demo')
frame_queue = queue.Queue(100)
detect_queue = queue.Queue(100)
frame_lock = threading.Lock()
detect_lock = threading.Lock()


def data_process(data_queue, lock):
    servers = conf.get('kafka', 'servers')
    producer = KafkaProducer(bootstrap_servers=servers)
    while True:
        start = time.time()
        lock.acquire()
        if data_queue.full():
            logging.error('data queue full')
        if not data_queue.empty():
            data = data_queue.get()
            current_frame = data['data']
            _, img_encode = cv2.imencode('.jpg', current_frame)
            img_base64 = base64.b64encode(img_encode)
            millis = int(round(time.time() * 1000))
            msg_dict = {
                "cameraId": data['cameraId'],
                "position": data['position'],
                "timestamp": millis,
                "data": str(img_base64, 'ASCII')
            }
            message = json.dumps(msg_dict).encode('utf-8')
            try:
                producer.send('bao_steel', message)
            except KafkaError as e:
                logging.error(e)
            end = time.time()
            print('time for processing {0}'.format(end - start))
        lock.release()


def main():
    # # 打开实时故障检测摄像头，camera id 应该为B系列故障监控相机的id
    # monitoring_thread = CameraThread(1000, 'monitor', in_use=True)
    # monitoring_thread.start()
    # 打开带头跟踪摄像头
    # read the signal for the first time
    if is_demo:
        signal = read_signal.read_from_file('signal.txt')
    else:
        signal = read_signal.read_from_plc()
    cam_num = len(signal)
    camera_id = get_camera_id(signal)
    detect_thread = threading.Thread(target=steel_detection.detect, args=(detect_queue, detect_lock, conf))
    detect_thread.start()
    decode_thread = threading.Thread(target=data_process, args=(frame_queue, frame_lock))
    decode_thread.start()
    camera_thread = CameraThread(camera_id, 'head', in_use=True, q1=frame_queue, q2=detect_queue, lock1=frame_lock, lock2=detect_lock)
    camera_thread.start()
    next_id = camera_id + 1 if camera_id < cam_num else 1
    next_camera_thread = CameraThread(next_id, 'head', in_use=False, q1=frame_queue, q2=detect_queue, lock1=frame_lock, lock2=detect_lock)
    next_camera_thread.start()
    # pre_signal = signal
    pre_cam_id = camera_id
    pre_time = time.time()
    while 1:
        # Keep updating the signal
        if is_demo:
            current_time = time.time()
            if current_time - pre_time > 300000000000000000000000000:
                camera_id = id_switch(camera_id)
                pre_time = current_time
            # signal = read_signal.read_from_file('signal.txt')
        else:
            signal = read_signal.read_from_plc()
            camera_id = get_camera_id(signal)
        # check signal change then move to the next camera
        if camera_id == pre_cam_id:
            # if signal == pre_signal:
            time.sleep(1)
        else:
            # camera_id = get_camera_id(signal)
            print('new id ' + str(camera_id))
            # # 打开新的摄像头，再关闭旧的，有延时
            # new_thread = CameraThread(new_id, 'head', in_use=False)
            # new_thread.start()
            # while 1:
            #     if new_thread.started:
            #         camera_thread.stop()
            #         break
            # --------------------------------------------
            # 永远保持两个摄像头开启
            next_id = camera_id + 1 if camera_id < cam_num else 1
            print('new next id ' + str(next_id))
            new_thread = CameraThread(next_id, 'head', in_use=False, q1=frame_queue, q2=detect_queue, lock1=frame_lock, lock2=detect_lock)
            next_camera_thread.in_use = True
            camera_thread.stop()
            # camera_thread.join()
            camera_thread = next_camera_thread
            next_camera_thread = new_thread
            next_camera_thread.start()
            # pre_signal = signal
            pre_cam_id = camera_id


def get_camera_id(sig):
    # TODO get camera id from signal
    cam_id = len(sig)
    for i in reversed(range(len(sig))):
        if sig[i] == '1':
            cam_id = i + 1
            break
    return cam_id


# test for demo
def id_switch(cam_id):
    if cam_id == 4:
        cam_id = 1
    else:
        cam_id += 1
    return cam_id


if __name__ == '__main__':
    main()
