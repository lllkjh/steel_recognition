import base64
import json
import logging
import time
import cv2
import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError
import demo


def detect(queue, lock, config):
    url = 'http://10.75.4.42:10595/v1/malfunction/addMalfunctionRecord'
    malfunction_topic = 'bao_malfunction_steel'
    malfunction_status = False
    malfunction_count = 0
    malfunction_count_threshold = 40
    normal_count = 0
    normal_count_threshold = 30
    video_duration = 5  # record for 5 seconds
    video_timer = 0
    video_num = 0
    record_on = False

    # record timer for test purpose
    record_timer = 0

    millis = int(round(time.time() * 1000))
    servers = config.get('kafka', 'servers')
    producer = KafkaProducer(bootstrap_servers=servers)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')

    while True:
        start = time.time()
        # lock.acquire()
        if queue.full():
            logging.error('detect queue full')
        if not queue.empty():
            data = queue.get()
            frame = data['data']
            # lock.release()
            print('detecting the image')
            _, processed_frame, warning = demo.run(frame)

            if warning:
                malfunction_count += 1
                # report malfunction if count > threshold
                if malfunction_count > malfunction_count_threshold:
                    if not malfunction_status:
                        print('malfunction recognized')
                        malfunction_status = True
                        current_time = int(time.time())
                        # set a gap period of 15 minuets for recording to avoid too much testing data
                        if current_time - record_timer > 15 * 60:
                            print('recording start')
                            record_timer = current_time
                            record_on = True
                            file_name = 'malfunction_{0}.mp4'.format(video_num)
                            video_num += 1
                            out = cv2.VideoWriter('video/' + file_name, fourcc, 25, (1024, 576))
                    else:
                        # send the malfunction image stream to kafka
                        _, img_encode = cv2.imencode('.jpg', processed_frame)
                        img_base64 = base64.b64encode(img_encode)
                        msg_dict = {
                            "type": "卡钢",
                            "position": data['position'],
                            "timestamp": millis,
                            "data": str(img_base64, 'ASCII'),
                            "complete": 1,
                            "desc": data['position'] + "卡钢"
                        }
                        message = json.dumps(msg_dict).encode('utf-8')
                        try:
                            producer.send(malfunction_topic, message)
                        except KafkaError as e:
                            logging.error(e)
            elif malfunction_status:
                # check malfunction stop
                if normal_count < normal_count_threshold:
                    # keep malfunction status and send the malfunction image stream to kafka
                    _, img_encode = cv2.imencode('.jpg', processed_frame)
                    img_base64 = base64.b64encode(img_encode)
                    msg_dict = {
                        "type": "卡钢",
                        "position": data['position'],
                        "timestamp": millis,
                        "data": str(img_base64, 'ASCII'),
                        "complete": 1,
                        "desc": data['position'] + "卡钢"
                    }
                    message = json.dumps(msg_dict).encode('utf-8')
                    try:
                        producer.send(malfunction_topic, message)
                    except KafkaError as e:
                        logging.error(e)
                    normal_count += 1
                else:
                    # malfunction stop, send the last frame to kafka with complete flag of 0
                    _, img_encode = cv2.imencode('.jpg', processed_frame)
                    img_base64 = base64.b64encode(img_encode)
                    msg_dict = {
                        "type": "卡钢",
                        "position": data['position'],
                        "timestamp": millis,
                        "data": str(img_base64, 'ASCII'),
                        "complete": 0,
                        "desc": data['position'] + "卡钢"
                    }
                    # msg_dict['data'] = str(img_base64, 'ASCII')
                    message = json.dumps(msg_dict).encode('utf-8')
                    try:
                        for i in range(2):  # Simply send two times for frontend to stop the malfunction image
                            producer.send(malfunction_topic, message)
                    except KafkaError as e:
                        logging.error(e)
                    malfunction_status = False
                    # print('{0} frames in this malfunction'.format(malfunction_count))
                    malfunction_count = 0
                    print('malfunction stop')
                    normal_count = 0
            else:
                malfunction_count = 0
            # Record the malfunction video for a period of time
            if record_on and video_timer < video_duration * 25:
                out.write(processed_frame)
                video_timer += 1
            elif video_timer >= video_duration * 25:
                # recording finished
                print('recording stop')
                video_timer = 0
                out.release()
                record_on = False
                # save the malfunction record
                params = {
                    "cameraId": 1,
                    "desc": data['position'] + "卡钢",
                    "eventTime": millis,
                    "position": data['position'],
                    "type": "卡钢",
                    "videoPath": file_name
                }
                r = requests.put(url, json=params)
                response = json.loads(r.content)
                if response['success']:
                    print('Record saved')
                else:
                    print('Record save failed')
        # else:
        #     lock.release()
        end = time.time()
        print('time for detecting {0}'.format(end - start))
