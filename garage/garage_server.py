
#!/usr/bin/python
import socket
import thread
import time
import sys
import RPi.GPIO as GPIO
from time import sleep
import select
import logging

import datetime
#from astral import Location

HOST      = ''   # Symbolic name, meaning all available interfaces
PORT      = 8888 # Arbitrary non-privileged port
BUFF      = 1024
TIME_OUT  = 1.5 # seconds
KEY       = b'dGz3WWDriyUJbiK9vUNZuIbHZ0pt9S07'

OPN_GAR = 0 
CLS_GAR = 1
OPN_ENT = 2
CLS_ENT = 3
OPN_BLB = 4
CLS_BLB = 5

STAT_ENT = 0 #0: CLS, 1:OPN
STAT_GAR = 0 #0: CLS, 1:OPN
STAT_BLB = 0 #0: CLS, 1:OPN

def print_to_log(msg):
  logging.basicConfig(level=logging.DEBUG, filename="/home/pi/garage/garage_log", datefmt='%d/%m/%y %H:%M:%S',
                            filemode="a+", format="[%(asctime)s] %(message)s")
  logging.warning(msg)
  print(msg)

def open_lights():
  GPIO.setup(17, GPIO.OUT)
  sleep(0.05)
  GPIO.output(17, GPIO.LOW)
  sleep(10)
  GPIO.setup(17, GPIO.IN)

def operate_door(code):
#  l=Location(('', '', 41.13771944444, 1.296777777777, 'Europe/Madrid', 78))  
  GPIO.setmode(GPIO.BCM)
  sleep(0.05)
  if code==OPN_GAR:
#    if datetime.datetime.now().hour>=l.sunset().hour and datetime.datetime.now().minute>=l.sunset().minute:
#      thread.start_new_thread(open_lights)
    print('Accion: Abrir garaje')
    GPIO.setup(15, GPIO.OUT)
    sleep(0.05)
    GPIO.output(15, GPIO.LOW)
    sleep(0.5)
    GPIO.setup(15, GPIO.IN)
  elif code==CLS_GAR:
    print('Accion: Cerrar garaje')
    GPIO.setup(15, GPIO.OUT)
    sleep(0.05)
    GPIO.output(15, GPIO.LOW)
    sleep(0.5)        
    GPIO.setup(15, GPIO.IN)
  elif code==OPN_ENT:
    print('Accion: Abrir entrada')
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(14, GPIO.OUT)
    sleep(0.05)
    GPIO.output(18, GPIO.LOW)
    sleep(0.3)
    GPIO.setup(18, GPIO.IN)
    GPIO.output(14, GPIO.LOW)
    sleep(14.5)
    GPIO.setup(14, GPIO.IN)
  elif code==CLS_ENT: 
    print('Accion: Cerrar entrada')
    GPIO.setup(27, GPIO.OUT)
    sleep(0.05)
    GPIO.output(27, GPIO.LOW)
    sleep(15)
    GPIO.setup(27, GPIO.IN)
  elif code==OPN_BLB:
    print('Accion: Abrir luz')
    GPIO.setup(18, GPIO.OUT)
    sleep(0.05)
    GPIO.output(18, GPIO.LOW)
  elif code==CLS_BLB:
    print('Accion: Cerrar luz')
    GPIO.setup(18, GPIO.OUT)
    sleep(0.05)
    GPIO.output(18, GPIO.HIGH)
       
def check_identity(clientsock):
    clientsock.setblocking(0)
    ready = select.select([clientsock], [], [], TIME_OUT)
    if not ready[0]:      
      return (False, '', '')
    data = clientsock.recv(BUFF)
    try:
      (rcv_key, command)=data.split('#')
      if rcv_key==KEY:
        return (True, int(command), data)
    except ValueError:
      return (False, '', data)
    return (False, '', data)

def handler(clientsock,addr):
  (identified, command, data) = check_identity(clientsock)  
  if identified: 
    print_to_log('Connection accepted! Command = '+repr(command)+'. Data = '+repr(data))
    operate_door(command)
  else:
    print_to_log('Undesired connection! Rejecting. Data = '+repr(data))
  clientsock.close()
  return

if __name__=='__main__':
  ADDR = (HOST, PORT) 
  serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print_to_log('Listening connections ...')
  try:   
    serversock.bind(ADDR)
  except socket.error as msg:
    print_to_log('Bind failed. Error Code : ' + str(msg[0]) + '\nMSG = ' + msg[1])
    sys.exit()  
  try:
    serversock.listen(0)
    while 1:
        clientsock, addr = serversock.accept()
        print_to_log('Connection recieved: ' + addr[0])
        thread.start_new_thread(handler, (clientsock, addr))
  except KeyboardInterrupt:    
    print_to_log('Exiting after keyboard interrupt.')
  except:
    print_to_log('Unhandled error.')
  finally:
    GPIO.cleanup()
