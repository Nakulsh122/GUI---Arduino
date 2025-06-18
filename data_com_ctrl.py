import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy import signal
from datetime import datetime
import csv
class DataMaster():
    def __init__(self):
        self.sync = "#?#\n"
        self.startStream = "#s#\n"  # FIXED: Removed duplicate definition
        self.stopStream = "#A#\n"
        self.sync_ok = "!"
        self.syncChannels = 0
        self.xData = []
        self.yData = []
        self.functions = {
            "RowData" : self.RowData,
            "Voltage" : self.Voltage,
            "Savgo Filter" : self.savgo,
            "Digital Filter" : self.digi_filter
        }
        # FIXED: Added missing attribute initializations
        self.RowMsg = b""
        self.message = []
        self.messageLen = 0
        self.messageLenCheck = 0
        self.streamData = False
        self.IntMsg = []
        self.channels = []
        self.DisplayTime = 5
        self.channelNum = {
            'Ch0' : 0 ,
            'Ch1' : 1 ,
            'Ch2' : 2 ,
            'Ch3' : 3 ,
            'Ch4' : 4 ,
            'Ch5' : 5 ,
            'Ch6' : 6 ,
            'Ch7' : 7 ,
        }
        self.channelColor = {
            'Ch0': 'blue',
            'Ch1': 'green',
            'Ch2': 'red',
            'Ch3': 'cyan',
            'Ch4': 'magenta',
            'Ch5': 'yellow',
            'Ch6': 'black',
            'Ch7': 'white'
        }
        self.RefTime = None
        
    def DecodeMsg(self):
        try:
            temp = self.RowMsg.decode('utf8')
            if len(temp) > 0:
                if "#" in temp:
                    self.message = temp.split("#")
                    if len(self.message) > 0:
                        del self.message[0]  # Remove first empty element
                    
                    if len(self.message) > 0 and self.message[0] == "D":
                        self.messageLen = 0
                        self.messageLenCheck = 0
                        del self.message[0]
                        if len(self.message) > 0:
                            del self.message[len(self.message)-1]
                        # print("Error in decode Message")
                        if len(self.message) > 0:
                            self.messageLen = int(self.message[len(self.message)-1])
                            del self.message[len(self.message)-1]
                        for item in self.message:
                            self.messageLenCheck += len(item)
        except Exception as e:
            print(f"Error in DecodeMsg: {e}")
            self.message = []

    def IntMsgFunc(self):
        try:
            self.IntMsg = [float(msg) for msg in self.message]
            print(self.IntMsg)
        except Exception as e:
            print(f"Error in IntMsg func: {e}")
            self.IntMsg = []

    def streamDataCheck(self):
        self.streamData = False
        if self.messageLen == self.messageLenCheck:
            if self.syncChannels == len(self.message):
                self.streamData = True
                self.IntMsgFunc()

    def SetRefTime(self):
        if self.RefTime is None:
            self.RefTime = time.perf_counter()

    def updateX(self):
        if len(self.xData) == 0 :
            self.xData.append(0)
        else:
            self.xData.append(time.perf_counter()-self.RefTime)

    def updateY(self):
        for ChnNo in range(self.syncChannels):
            self.yData[ChnNo].append(self.IntMsg[ChnNo])

    def adjustData(self):
        lenXdata = len(self.xData)
        if (self.xData[lenXdata-1] - self.xData[0]) > self.DisplayTime:
            del self.xData[0]
            for ydata in self.yData:
                del ydata[0]

        x = np.array(self.xData)
        self.xdisplay = np.linspace(x.min(), x.max(), len(x), endpoint=0)
        self.ydisplay = np.array(self.yData)

    def genChannels(self):
        self.channels = [f"Ch{ch}" for ch in range(1, int(self.syncChannels) + 1)]

    def buildData(self):
        # Clear existing data first
        self.yData.clear()
        for _ in range(self.syncChannels):
            self.yData.append([])
     
    def RowData(self,gui):
        gui.chart.plot(gui.x, gui.y,color = gui.color,dash_capstyle = 'projecting', linewidth =  1);
        pass
    
    def Voltage(self,gui):
        gui.chart.plot(gui.x, (gui.y/4096)*3.3,color = gui.color,dash_capstyle = 'projecting', linewidth =  1);

        pass
    
    def savgo(self,gui):
        x = gui.x
        y = gui.y
        w = savgol_filter(y,len(x)-1,2)
        gui.chart.plot(gui.x, w,color = "#1cbda5",dash_capstyle = 'projecting', linewidth =  1);

    def digi_filter(self,gui):
        x = gui.x
        y=gui.y
        b,a = signal.ellip(4,0.01,120,0.125)
        fgust =  signal.filtfilt(b,a,y,method = "gust")
        gui.chart.plot(gui.x, fgust,color = "#00be95",dash_capstyle = 'projecting', linewidth =  1);

    def genFileName(self):
        now = datetime.now()
        self.filename = now.strftime("%Y%m%m%H%M%S")+'.csv'

    def saveData(self,gui):
        data = [elt for elt in self.IntMsg]
        data.insert(0,self.xData[len(self.xData)-1])
        if gui.save:
            with open(self.filename,'a',newline='') as f:
                data_writer = csv.writer(f)
                data_writer.writerow(data)
    def clearData(self):
        self.xData.clear()
        self.yData.clear()
        self.RowMsg = b""
        self.message = []
        self.messageLen = 0
        self.messageLenCheck = 0
        self.streamData = False
        self.IntMsg = []
        self.RefTime = None