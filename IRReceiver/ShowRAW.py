import RPi.GPIO as GPIO
from time import time

# Numbers GPIOs by physical location
GPIO.setmode(GPIO.BOARD)
# set pin 12 as an input pin with default as LOW v
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# define a function to acquire data
def binary_acquire(pin, duration):
    # acquires data as quickly as possible
    t0 = time() # time is in seconds here
    results = []
    while (time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results

print("Acquiring data for 1 second")
# acquire data for 1 second
results = binary_acquire(12, 1.0)
print("Done!")
print(",".join([str(result) for result in results]))
GPIO.cleanup()
