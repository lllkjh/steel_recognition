# coding=utf-8
import time
from camera_thread import CameraThread
import read_signal
import configparser

conf = configparser.ConfigParser()
conf.read('config.ini', encoding='utf-8')
is_demo = conf.getboolean('env', 'demo')


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
    camera_thread = CameraThread(camera_id, 'head', in_use=True)
    camera_thread.start()
    next_id = camera_id + 1 if camera_id < cam_num else 1
    next_camera_thread = CameraThread(next_id, 'head', in_use=False)
    next_camera_thread.start()
    # pre_signal = signal
    pre_cam_id = camera_id
    pre_time = time.time()
    while 1:
        # Keep updating the signal
        if is_demo:
            current_time = time.time()
            if current_time - pre_time > 10:
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
            new_thread = CameraThread(next_id, 'head', in_use=False)
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
