#!/usr/bin/python
# _*_ coding: utf-8 _*_

"""
送信波形: NECリモコン 記録ファイル: recieves

curl -X GET http://192.168.x.x:9999/sendBullet?id=123\&bullet=XX
"""

import requests
import RPi.GPIO as GPIO
import subprocess
import time

url = 'http://192.168.1.171:9999/recvBullet?id=25004'
req =  requests.get(url)
bullet = req.json()
print("Bullet",bullet)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN,pull_up_down = GPIO.PUD_UP)

try:
   ammunition = bullet["Bullet"]

   while True:
      if ammunition <= 0:
         print("play end")
         url = 'http://192.168.1.171:9999/sendNotice?id=25007'
         requests.get(url)
         exit(0)

      if GPIO.input(4) == GPIO.LOW:
         print("sw on")
         #CHANGED: IR送信　言語をpythonからCに変更
         cmd = "timeout 0.2 sudo ./wink 17"
         subprocess.call(cmd.split())
         print(cmd)
         ammunition -= 1
         print(ammunition)

      time.sleep(0.1)

except KeyboardInterrupt:
   print("\nCtl+C")
   pass

GPIO.cleanup() #ピンをクリーンする