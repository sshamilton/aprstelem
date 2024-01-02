#!/usr/bin/python
# -*- coding:utf-8 -*-

import serial
import time
import ADS1256
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
import sys
import os
import pdb
import time
# 13975 is passcode for W2KGY

def serial_init():

    #Setup the Serial port for the TNC
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate=9600
    #ser.write(b'k')
    #ser.write('\r'.encode())
    ser.reset_output_buffer()
    ser.flush()
    #initialize the radio
    dump = ser.read(ser.in_waiting)
    print("Dump: ")
    print(dump)
    time.sleep(1)
    resp = ser.read(ser.in_waiting)
    if (resp[-4:] == b'cmd:'):
        print("Radio in command mode, setting relay and going to comms mode")
        ser.write(b'U RELAY\r')
        r = ser.read(ser.in_waiting)
        print(r)
        ser.write('MYCALL KJ5HY-2\r'.enode())
        r = ser.read(ser.in_waiting)
        print(r)
        ser.write(b'k\r')
    else:
        print("Not in command mode")
        print("read " + str(resp[-4:]))
    return (ser)

def serialnum():
    f = open('/tmp/snum', 'r')
    snum = f.read()
    print('incrementing' + snum)
    print(snum)
    inc = int(snum) + 1
    if (inc > 999):
        inc=1
    f.close()
    f = open('/tmp/snum', 'w')
    f.write(str(inc))
    f.close()
    return (int(snum))

def send_packet(ser):
    try:
        ADC = ADS1256.ADS1256()
        #This funntion prints out, which we don't want
        ADC.ADS1256_init()
        print("start") 
        snum = serialnum()
        print("Serial number is " + str(snum))
        ADC_Value = ADC.ADS1256_GetAll()
        temp = CPUTemperature().temperature
        #pdb.set_trace()
        ttemp = int(round(temp, 0))
        #print ("0 ADC = %lf"%(ADC_Value[0]*5.0/0x7fffff))
        print ("Pi temp = %.2f" % temp)
        adc =  ("%.2f"%(ADC_Value[0]*5.0/0x7fffff))
        tadc = float(adc)*100
        print("ADC Reading: " + str(tadc))

        tadc = int(round(tadc, 0)) #put in telemetry range for aprs 0-255
        telem = "T#{:03d}".format(snum) + "," + str(ttemp) + "," + str(tadc) + "\r"
        print (telem)
        #ser.write(bytes('\r\n', 'utf-8')) #Clear out anything in the queue
        r = ser.read(ser.in_waiting)
        time.sleep(1)
        print(r)

        ser.write(telem.encode())
        #ser.flush()
        print('Sent')
    except Exception as e:
        GPIO.cleanup()
        print ("\r\nProgram crashed: %s", e)
        exit()


def main():
    print("Initializing Serial Port")
    ser = serial_init()
    while (1):
        send_packet(ser)
        time.sleep(30)


    ser.close()

if __name__ == '__main__':
    sys.exit(main())
