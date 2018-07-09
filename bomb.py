from datetime import datetime
from subprocess import call
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

wire_1 = 17
wire_2 = 27
wire_3 = 22
wire_4 = 23 
reset = 25

GPIO.setup(wire_1,GPIO.IN)
GPIO.setup(wire_2,GPIO.IN)
GPIO.setup(wire_3,GPIO.IN)
GPIO.setup(wire_4,GPIO.IN)
GPIO.setup(reset,GPIO.IN)

clock = 16
alarm = 26
led_green = 5
led_red = 6

GPIO.setup(clock,GPIO.OUT)
GPIO.setup(alarm,GPIO.OUT)
GPIO.setup(led_green,GPIO.OUT)
GPIO.setup(led_red,GPIO.OUT)

def explode():
    GPIO.output(clock,GPIO.LOW)
    GPIO.output(alarm,GPIO.HIGH) #1sec
    time.sleep(1)
    GPIO.output(alarm,GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(led_red,True)
    call(["aplay", "/home/pi/Explosif.wav"]) #boom
    print "fail"
    return

def defuse(): 
    GPIO.output(clock,GPIO.LOW)  
    time.sleep(1)
    GPIO.output(led_green,True)
    call(["aplay", "/home/pi/Tadaah.wav"]) #fanfare
    print "win"
    return

def set_time():
    global begin
    global now
    GPIO.output(clock,GPIO.LOW)
    startClk = False
    begin = datetime.now()
    now = datetime.now()
    while not startClk:
        check = datetime.now()
        if check.second > now.second or (check.second == 0 and check.second != now.second):
            now = datetime.now()
            GPIO.output(led_green,True)
            GPIO.output(led_red,True)
            time.sleep(0.5)
            GPIO.output(led_green,False)
            GPIO.output(led_red,False)
            GPIO.output(clock,GPIO.HIGH)
            startClk = True
    return

def check_time():
    global begin
    global now
    check = datetime.now()
    if check.hour != begin.hour and check.minute >= begin.minute and check.minute >= begin.second:
        explode()
    elif check.second > now.second or (check.second == 0 and check.second != now.second):
        now = datetime.now()
        call(["aplay", "/home/pi/Clock.wav"]) #tick
    else:
        return
    return

def bomb():
    while True:
        winCond = False
        GPIO.output(clock,GPIO.LOW)

        if GPIO.input(reset) and not (GPIO.input(wire_1) and GPIO.input(wire_2) and GPIO.input(wire_3) and GPIO.input(wire_4)):
            GPIO.output(led_green,True)
            GPIO.output(led_red,True)
            time.sleep(0.1)
            GPIO.output(led_green,False)
            GPIO.output(led_red,False)

        elif GPIO.input(wire_1) and GPIO.input(wire_2) and GPIO.input(wire_3) and GPIO.input(wire_4) and GPIO.input(reset):
            GPIO.output(led_green,False)
            GPIO.output(led_red,False)
            
            while not winCond: # Set up the bomb
                if GPIO.input(wire_1) and GPIO.input(wire_2) and GPIO.input(wire_3) and GPIO.input(wire_4):
                    set_time()
                    
                    while not winCond: # Stage 1
                        check_time()
                        if GPIO.input(reset):
                            break
                        elif GPIO.input(wire_1) and (not GPIO.input(wire_2) or not GPIO.input(wire_3) or not GPIO.input(wire_4)):
                            winCond = True
                            explode()
                            break
                        elif not GPIO.input(wire_1) and GPIO.input(wire_2) and GPIO.input(wire_3) and GPIO.input(wire_4):
                            
                            while not winCond: # Stage 2
                                check_time()
                                if GPIO.input(reset):
                                    break
                                elif GPIO.input(wire_2) and (not GPIO.input(wire_3) or not GPIO.input(wire_4)):
                                    winCond = True
                                    explode()
                                    break
                                elif not GPIO.input(wire_2) and GPIO.input(wire_3) and GPIO.input(wire_4):

                                    while not winCond: # Stage 3
                                        check_time()
                                        if GPIO.input(reset):
                                            break
                                        elif GPIO.input(wire_3) and not GPIO.input(wire_4):
                                            winCond = True
                                            explode()
                                            break
                                        elif not GPIO.input(wire_3) and GPIO.input(wire_4):

                                            while not winCond: # Stage 4
                                                check_time()
                                                if GPIO.input(reset):
                                                    break                        
                                                elif not GPIO.input(wire_4):
                                                    winCond = True
                                                    defuse()
                                                    break                      
    return

GPIO.output(led_green,True)
GPIO.output(led_red,True)
bomb()