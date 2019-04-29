import camera
import read_signal
import threading


global camera_on
pre_signal = []
while 1:
    signal = read_signal.read_from_file('signal.txt')
    if signal != pre_signal:
        if signal.count('1') % 2:
            cam_id = 100
        else:
            cam_id = 1
        camera_thread = threading.Thread(target=camera.start_camera, args=(cam_id,))
