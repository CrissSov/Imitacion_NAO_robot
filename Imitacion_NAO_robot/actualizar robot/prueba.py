# -*- coding: utf-8 -*-
from naoqi import ALProxy
ip = "192.168.137.115"
port = 9559

try:
    motion = ALProxy("ALMotion", ip, port)
    print("Conexión establecida con ALMotion")
except Exception as e:
    print("Error:", e)
