import torch
import numpy as np
from torchvision import models, transforms
import RPi.GPIO as GPIO

import cv2
from PIL import Image

from gpiozero import AngularServo

servo = AngularServo(18, min_pulse_width=.1/60, max_pulse_width=.12/60)
cap = cv2.VideoCapture(0)
    

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

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
            servo.angle = 90
        else:
            servo.angle = 0

        print(output)
