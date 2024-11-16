import RPi.GPIO as GPIO
import time

GPIO_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(GPIO_PIN, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()