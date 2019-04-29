import camera
import read_signal

while 1:
    signal = read_signal.read_from_file('signal.txt')
    print(signal.count('1'))
    if signal.count('1') % 2:
        cap = camera.start_camera(100)
    else:
        cap = camera.start_camera(1)

