#!/usr/bin/python
# _*_ coding: utf-8 _*_

import requests
import RPi.GPIO as GPIO
import subprocess
import time

#def getbullet():
# url = 'http://192.168.1.1:9999/recvBullet?id=123'
# req =  requests.get(url)
# bullet = req.json()
 #bullet["Bullet"]  # 仮弾数
#print("Bullet",ammunition)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN,pull_up_down = GPIO.PUD_UP)

try:
   ammunition = 5
   while True:

      if ammunition <= 0:
         print("play end")
         # url = 'http://192.168.1.1:9999/sendNotice?id=123'
         exit(0)

      if GPIO.input(4) == GPIO.LOW:
         print("sw on")
         cmd = "timeout 0.3 python3 irrp.py -p -g17 -f recieves Infrared"
         subprocess.call(cmd.split())
         print(cmd)
         ammunition -= 1
         print(ammunition)

      time.sleep(0.5)

except KeyboardInterrupt:
   pass

#ピンをクリーンする
GPIO.cleanup()
#pi.set_mode(4, pigpio.OUTPUT)
#pi.stop()