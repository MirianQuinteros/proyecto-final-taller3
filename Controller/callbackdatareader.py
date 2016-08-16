#!/usr/bin/python

from PyDAQmx import *
from PyDAQmx import Task
from numpy import zeros
import numpy as np

class CallbackTask(Task):

    def __init__(self, fq, limitvolt, readvlbl, fileName):
        Task.__init__(self)
        
        self.isOk = True
        self.points = 10000
        self.limit = limitvolt
        self.data = zeros(self.points)
        self.readvoltageLbl = readvlbl
        self.name = fileName

        ffq = 40000.0 # freq limite de la placa

        self.CreateAIVoltageChan("Dev1/ai0","",DAQmx_Val_RSE,-10.0,10.0, DAQmx_Val_Volts, None)
        self.CfgSampClkTiming("",ffq, DAQmx_Val_Rising,DAQmx_Val_ContSamps, self.points)
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer, self.points, 0)
        self.AutoRegisterDoneEvent(0)

        self.abc = open(self.name, 'wb')
        self.abc.truncate()
        self.abc.close()


    def EveryNCallback(self):
        read = int32()
        
        #self.ReadAnalogF64(self.points,10.0,DAQmx_Val_GroupByChannel,self.data,self.points,byref(read),'pepe')
        self.ReadAnalogF64(self.points,10.0,DAQmx_Val_GroupByScanNumber,self.data,self.points,byref(read),None)

        with open(self.name,'ab') as aff:
            np.savetxt(aff, self.data, delimiter=",")

        mm = max(self.data)

        for i in range(1,self.points,500):
            self.readvoltageLbl.setText(str(round(self.data[i], 2)) + 'KV')

        if mm > self.limit :
            self.isOk = False
            self.StopTask()
        return 0 # The function should return an integer

    def getStatus(self):
        return self.isOk

    def DoneCallback(self, status):
        print("Status",status)
        return 0 # The function should return an integer