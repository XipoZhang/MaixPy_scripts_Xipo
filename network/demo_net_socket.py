import socket
import network
import gc
import os
import lcd, image
import machine
from Maix import GPIO
from board import board_info
from fpioa_manager import fm

#reset ESP8285 begin
fm.register(8, fm.fpioa.GPIOHS0, force=True)
wifi_en=GPIO(GPIO.GPIOHS0, GPIO.OUT)

fm.register(0, fm.fpioa.GPIOHS1, force=True)
wifi_io0_en=GPIO(GPIO.GPIOHS1, GPIO.OUT)
wifi_io0_en.value(0)

wifi_en.value(0)  ##if ESP8285 init error ,try add ## or remove ##  this line.
time.sleep(2)
wifi_en.value(1)
time.sleep(5)
#reset ESP8285 end

fm.register(board_info.WIFI_RX, fm.fpioa.UART2_TX, force=True)
fm.register(board_info.WIFI_TX, fm.fpioa.UART2_RX, force=True)
uart = machine.UART(machine.UART.UART2, 115200,timeout=1000, read_buf_len=4096)
nic=network.ESP8285(uart)
nic.connect("Sipeed_2.4G","passwd")

sock = socket.socket()
addr = socket.getaddrinfo("dl.sipeed.com", 80)[0][-1]
sock.connect(addr)
sock.send('''GET /MAIX/MaixPy/assets/Alice.jpg HTTP/1.1
Host: dl.sipeed.com
cache-control: no-cache
User-Agent: MaixPy
Connection: close

''')

img = b""
sock.settimeout(5)
while True:
    data = sock.recv(4096)
    if len(data) == 0:
        break
    print("rcv:", len(data))
    img = img + data

print(len(img))
begin=img.find(b"\r\n\r\n")+4
img = img[begin:begin+43756]   ## jpg file size is 43756 byte
print(len(img))
print("save to /flash/Alice.jpg")
f = open("/flash/Alice.jpg","wb")
f.write(img)
f.close()
print("save ok")
print("display")
img = image.Image("/flash/Alice.jpg")
lcd.init()
lcd.display(img)
