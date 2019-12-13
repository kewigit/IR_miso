#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
デーモンエラーが出る場合

> sudo systemctl stop pigpiod
> sudo systemctl start pigpiod

"""
"""
glitch     ignore edges shorter than glitch microseconds, default 300 us
            　グリッチノイズのおそれのためマイクロ秒より短い短いエッジを無視する

post       expect post milliseconds of silence after code, default 15 ms
pre        expect pre milliseconds of silence before code, default 200 ms

short      reject codes with less than short pulses, default 10
             短径波形を無視する

tolerance  consider pulses the same if within tolerance percent, default 15
            　許容範囲内ならパルス幅を同じとする

no-confirm don't require a code to be repeated during record
            　確認の為のコードを繰り返し受信しない

TRANSMIT

freq       IR carrier frequency, default 38 kHz
            リモコンのヘルツをデフォルト３８k
gap        gap in milliseconds between transmitted codes, default 100 ms
            送信されたコード間のミリ秒単位のギャップ
"""

import time
import requests
import json

# import Adafruit_PCA9685
import pigpio  # http://abyz.co.uk/rpi/pigpio/python.html

GPIO = 18           #GPIO18
#CHANGED: デフォルト波形を300 → 100
GLITCH = 100        #波形
PRE_MS = 200
POST_MS = 15        #受信秒数
FREQ = 38.0         #受信するデフォルトのHz
VERBOSE = False
SHORT = 10          #除外する短径波形
GAP_MS = 0.1
NO_CONFIRM = True   #Trueの場合 受信するIRを2回確認しない
TOLERANCE = 15      #パルス幅

POST_US = POST_MS * 1000
PRE_US = PRE_MS * 1000
GAP_S = GAP_MS / 1000.0
CONFIRM = not NO_CONFIRM
TOLER_MIN = (100 - TOLERANCE) / 100.0
TOLER_MAX = (100 + TOLERANCE) / 100.0

last_tick = 0
in_code = False
code = []
fetching_code = False

# sendHit?id=25005&hit=ヒット数

def carrier(gpio, frequency, micros):
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros / cycle))
    on = int(round(cycle / 2.0))
    sofar = 0

    for c in range(cycles):
        target = int(round((c + 1) * cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1 << gpio, 0, on))
        wf.append(pigpio.pulse(0, 1 << gpio, off))

    return wf

#波形 正規化
def normalise(c):
    """
    Input

      M    S   M   S   M   S   M    S   M    S   M
    9000 4500 600 540 620 560 590 1660 620 1690 615

    Distinct marks

    9000                average 9000
    600 620 590 620 615 average  609

    Distinct spaces

    4500                average 4500
    540 560             average  550
    1660 1690           average 1675

    Output

      M    S   M   S   M   S   M    S   M    S   M
    9000 4500 609 550 609 550 609 1675 609 1675 609
    """
    if VERBOSE:
        print("before normalise", c)
    entries = len(c)
    p = [0] * entries  # Set all entries not processed.

    for i in range(entries):
        if not p[i]:  # Not processed?
            v = c[i]
            tot = v
            similar = 1.0

            # Find all pulses with similar lengths to the start pulse.
            for j in range(i + 2, entries, 2):
                if not p[j]:  # Unprocessed.
                    if (c[j] * TOLER_MIN) < v < (c[j] * TOLER_MAX):  # Similar.
                        tot = tot + c[j]
                        similar += 1.0

            # Calculate the average pulse length.
            newv = round(tot / similar, 2)
            c[i] = newv

            # Set all similar pulses to the average value.
            for j in range(i + 2, entries, 2):
                if not p[j]:  # Unprocessed.
                    if (c[j] * TOLER_MIN) < v < (c[j] * TOLER_MAX):  # Similar.
                        c[j] = newv
                        p[j] = 1

    if VERBOSE:
        print("after normalise", c)

#波形が短すぎる場合、その波形を除外
def end_of_code():
    global code, fetching_code
    if len(code) > SHORT:
        normalise(code)
        fetching_code = False

    else:
        code = []
        print("Error: Short code")

#GPIO18にエッジが検出された時
def cbf(gpio, level, tick):
    global last_tick, in_code, code, fetching_code

    if level != pigpio.TIMEOUT:
        edge = pigpio.tickDiff(last_tick, tick)
        last_tick = tick

        if fetching_code:
            if (edge > PRE_US) and (not in_code):  # Start of a code.
                in_code = True
                pi.set_watchdog(GPIO, POST_MS)  # watchdog　on.

            elif (edge > POST_US) and in_code:  # End of a code.
                in_code = False
                pi.set_watchdog(GPIO, 0)  # watchdog キャンセル.
                end_of_code()

            elif in_code:
                code.append(edge)

    else:
        pi.set_watchdog(GPIO, 0)  # watchdog　キャンセル.
        if in_code:
            in_code = False
            end_of_code()


pi = pigpio.pi()  # pigpio コネクト

if not pi.connected:
    exit(0)


pi.set_mode(GPIO, pigpio.INPUT)  # IR GPIO18 SET

pi.set_glitch_filter(GPIO, GLITCH)  # IRを受信したときのフィルター グリッチノイズ無視する.

cb = pi.callback(GPIO, pigpio.EITHER_EDGE, cbf) # GPIO18ピンにエッジが検出されるたび関数を呼び出す

#TODO: 適切な距波形を計算する
#TODO: 的をサーボモータで制御
#IR受信 メイン処理
if __name__ == "__main__":

    hitcount = 0 #IR受信数をカウント

    url = 'http://192.168.1.171:9999/recvNotice?id=25007'
    req = requests.get(url)
    notice = req.json()

    while notice["Flg"] == False:
       print("Press key for '{}'".format("Infrared"))
       code = []
       fetching_code = True

       while fetching_code and notice["Flg"] == False:
         url = 'http://192.168.1.171:9999/recvNotice?id=25007'
         req = requests.get(url)
         notice = req.json()
         print("notice", notice)   #デバック用
         time.sleep(1)

       if notice["Flg"] == True:
           #hitcount -= 1
           #hit数送信
           hit = 'http://192.168.1.171:9999/sendHit?id=25005&hit={}'.format(hitcount)
           requests.get(hit)
           print(hit)
           time.sleep(1)
           exit(0)

       print("Okay")
       #print("ferching", fetching_code)
       time.sleep(1)

       if CONFIRM:
           press_1 = code[:]
           done = False

       else:  # No confirm.
           print("赤外線検知")
           hitcount += 1
           print("Hit COUNT", hitcount)

pi.set_glitch_filter(GPIO, 0)  # フィルター 無効.
pi.set_watchdog(GPIO, 0)  # watchdog キャンセル.
pi.stop()  # pigpio stop
