#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyaudio
import wave
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui, uic
import math, numpy, threading, json
from . import signalproducer

class Experience():

  def __init__(self, id=1, jsonObj=None):

    if jsonObj is None :
        self.id = id
        self.descr = "Set description..."
        self.voltage = 0.8
        self.fehd = 1.2
        self.fforz = 10
        self.dc = 50
        self.duration = 10
        self.camera = False
        self.smoke = False
        self.stop = False
        self.signalType = 'Seno'
        self.durationLeft = -1
    else :
        print(jsonObj)
        self.__dict__ = json.loads(jsonObj)

  def ejecutar(self, durat, counter):
    self.stop = False
    print ("Ejecutando..." + str(self.id))
    p = pyaudio.PyAudio()
    freq = self.fehd * 1000
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1, rate=44100, output=1)
    dur = self.play_tone(stream, frequency=freq, length=durat, counter=counter)
    stream.close()
    p.terminate()
    return dur

  def detener(self):
    print('Experience: Detener ejecucion')
    self.stop = True

  def play_tone(self, stream, frequency=440, length=1, counter=None):
    
    period = 1/self.fforz
    volume = self.voltage

    prod = signalproducer.SignalProducer(volume, self.signalType)
    chunk = prod.produceChunk(frequency, period , self.dc)
    
    if chunk is None:
        print('ERROR producing chunk')
        return
    x = 0
    acc = 0
    sec = length
    counter.display(length)
    
    while (x <= length) & (self.stop == False):
        x+=period
        stream.write(chunk.astype(numpy.float32).tostring())
        acc+=period
        if acc >= 0.97:
            acc = 0
            sec = sec - 1
            counter.display(sec)

    if x < length:
        self.durationLeft = length - x
    else:
        self.durationLeft = -1
        counter.display(0)
    return self.durationLeft

    
