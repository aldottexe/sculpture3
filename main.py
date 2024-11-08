import torch
import numpy as np
from torchvision import models, transforms
import RPi.GPIO as GPIO

from multiprocessing import Process, Value
import time

import cv2
from PIL import Image

cap = cv2.VideoCapture(0)
    
mosfet_pin = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(mosfet_pin, GPIO.OUT)

model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

PINS = [25,8,7,1]

pulse_interval = Value('d', 0.1)

def pulse_motor(pulse_interval):
    while True:
        interval = pulse_interval.value
        for pin in PINS:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(pin, GPIO.LOW)

def ai_loop(): 
    with torch.no_grad():
        while True:
            # read frame
            ret, image = cap.read()
            if not ret:
                raise RuntimeError("failed to read frame")
    
            # convert opencv output from BGR to RGB
            image = image[:, :, [2, 1, 0]]
    
            # run model
            output = model(image)
            # do something with output ...
            print('total', output.xywhn[0].numpy())
            people = [p for p in output.xywhn[0].numpy() if ((float(p[-1]) == 0) & (float(p[-2]) > 0.6))] 
            if len(people) > 0: 
                print('fire!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                GPIO.output(mosfet_pin, GPIO.HIGH)
            else:
                GPIO.output(mosfet_pin, GPIO.LOW)
    
            print(output)

if __name__ == "__main__":
    motor_process = Process(target=pulse_motor, args=(pulse_interval,))
    motor_process.start()

    try: 
        ai_loop()
    finally:
        motor_process.terminate()
        GPIO.cleanup()
