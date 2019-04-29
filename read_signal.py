import snap7
import time


# get video switch signal from file(for testing)
def read_from_file(path):
    with open(path) as f:
        data = f.readlines()
        for i in range(len(data)):
            data[i] = data[i].rstrip('\n')
    return data


# get switch signal from PLC
def read_from_plc():
    pass


if __name__ == '__main__':
    file_path = 'signal.txt'
    while 1:
        signal_data = read_from_file(file_path)
        print(signal_data)
        time.sleep(0.5)
