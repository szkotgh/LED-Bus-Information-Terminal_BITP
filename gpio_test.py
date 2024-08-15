import RPi.GPIO as GPIO
import time
from datetime import datetime

def get_crtt():
    now = datetime.now()
    formatted_time = now.strftime("[%y/%m/%d.%H:%M:%S]")
    return formatted_time

print(f"{get_crtt()} program start")

pan_pins = [19, 20, 21, 22, 23, 24]

GPIO.setmode(GPIO.BCM)
for pan_pin in pan_pins:
    GPIO.setup(pan_pin, GPIO.OUT)
    GPIO.output(pan_pin, GPIO.HIGH)
    print(f"{get_crtt()} pin {pan_pin} setup")

try:
    while True:
        if int(input("> ")):
            for pan_pin in pan_pins:
                GPIO.output(pan_pin, GPIO.LOW)
            print(f"{get_crtt()} power on")
        
        else:
            for pan_pin in pan_pins:
                GPIO.output(pan_pin, GPIO.HIGH)
            print(f"{get_crtt()} power off")
        
except Exception as e:
    print(f"{get_crtt()} err:{e}")
    GPIO.cleanup()
