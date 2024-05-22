import RPi.GPIO as GPIO
import time
from datetime import datetime

def get_crtt():
    now = datetime.now()
    formatted_time = now.strftime("[%y/%m/%d.%H:%M:%S]")
    return formatted_time

print(f"{get_crtt()} program start")

pan_pin_1 = 17
pan_pin_2 = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(pan_pin_1, GPIO.OUT)
GPIO.setup(pan_pin_2, GPIO.OUT)
GPIO.output(pan_pin_1, GPIO.HIGH)
GPIO.output(pan_pin_2, GPIO.HIGH)
print(f"{get_crtt()} power reset")

try:
    while True:
        if int(input("> ")):
            GPIO.output(pan_pin_1, GPIO.LOW)
            GPIO.output(pan_pin_2, GPIO.LOW)
            print(f"{get_crtt()} power on")
        
        else:
            GPIO.output(pan_pin_1, GPIO.HIGH)
            GPIO.output(pan_pin_2, GPIO.HIGH)
            print(f"{get_crtt()} power off")
        
except Exception as e:
    print(f"{get_crtt()} err:{e}")
    GPIO.cleanup()

