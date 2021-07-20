from time import sleep
import RPi.GPIO as GPIO
import cv2

DIR = 20     # Direction GPIO Pin
STEP = 21    # Step GPIO Pin

STEPPING_CLKW = 1
STEPPING_CCLKW = 0
STEP_COUNT = 0


GPIO.setmode(GPIO.BCM)

GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

A4988_MODE_PIN = (14, 15, 18)
GPIO.setup(A4988_MODE_PIN, GPIO.OUT)

A4988_MODE = {'Full': (0, 0, 0),
              'Half': (1, 0, 0),
              '1/4': (0, 1, 0),
              '1/8': (1, 1, 0),
              '1/16': (1, 1, 1)}

def motor_set_mode(mode):
    GPIO.output(A4988_MODE_PIN, A4988_MODE[mode]) 

#def motor_CLKW():
#    GPIO.output(DIR, STEPPING_CLKW)
    
#def motor_CCLKW():
#    GPIO.output(DIR, STEPPING_CCLKW)
    
def motor_activate(stepcount, delay):
    
    #if direction == STEPPING_CLKW:
     #   motor_CLKW()
      #  direction = "Clock Wise"
    #else:
     #   motor_CCLKW()
      #  direction = "Counter Clock Wise"
        
    for step in range(stepcount):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    #GPIO.output(DIR, GPIO.LOW)
    #print("motor run", direction, "with", stepcount, "steps")
        
    
def motor_deactivate():
    GPIO.output(STEP, GPIO.LOW)
    

try:
    while True:
        STEPPING_CLKW = 1
        STEPPING_CCLKW = 0
        motor_set_mode("Full")
        print("Enter the steps: ")
        steps = int(input())
        print("Enter the delay:")
        delay = float(input())
        
        if steps > 0:
            GPIO.output(DIR, STEPPING_CLKW)
            motor_activate(steps, delay)
            print(steps)
        if steps < 0:
            GPIO.output(DIR, STEPPING_CCLKW)
            print("counter clock")
            steps = steps * -1
            motor_activate(steps, delay)
            print(steps)
        if steps == 0:
            motor_deactivate()
    
except KeyboardInterrupt:
    print ("\nCtrl-C pressed.  Stopping PIGPIO and exiting...")
finally:
    GPIO.output(STEP, GPIO.LOW)  # off
    GPIO.cleanup()


"""
import cv2

# setup camera object
cap = cv2.VideoCapture(0)

#QR code detection
detector = cv2.QRCodeDetector()

while True:
    _, img = cap.read()

    data, bbox, _ = detector.detectAndDecode(img)

    if bbox is None:
        for i in range(len(bbox)):
            cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,0,255), thickness=2)
        cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        if data:
            print("data found: ", data)
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break

cap.release()
cv2.destroyAllWindows()
"""