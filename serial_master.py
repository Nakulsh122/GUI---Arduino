import serial
import serial.tools.list_ports
import time
import threading

class SerialCtrl():
    def __init__(self):
        self.comList = []
        self.ser = serial.Serial()
        self.ser.status = False  # Custom attribute
        self.sync_cnt = 200
        self.threading = False

    def getComList(self):
        ports = serial.tools.list_ports.comports()
        self.comList = ['-'] + [com[0] for com in ports]

    def serialConnect(self, gui):
        PORT = gui.clicked_com.get()
        BAUD = gui.clicked_Bode.get()

        if not self.ser.is_open:
            try:
                self.ser.port = PORT
                self.ser.baudrate = int(BAUD)
                self.ser.timeout = 0.2
                self.ser.open()
                self.ser.status = True
                print(f"Connected to {PORT} at {BAUD} baud.")
            except Exception as e:
                self.ser.status = False
                print(f"Some Error Occurred: {e}")

    def serialClose(self):
        try:
            if self.ser.is_open:
                self.ser.close()
                self.ser.status = False
                print("port closed")
        except Exception as e:
            self.ser.status = False
            print(f"Error closing port: {e}")

    def serialStop(self, gui):
        # FIXED: Use gui.data instead of self.data
        self.ser.write(gui.data.stopStream.encode())

    
    def serialSync(self, conn_gui):
        print("Starting serialSync thread...")
        self.threading = True
        cnt = 0
        
        while self.threading:
            try:
                # Send sync command
                sync_command = conn_gui.data.sync.encode()
                self.ser.write(sync_command)
                print(f"Sent sync command: {sync_command}")
                
                # Update GUI status
                conn_gui.sync_status.config(text="syncing...", fg="orange")
                
                # Read response
                raw_msg = self.ser.readline()
                if raw_msg:
                    conn_gui.data.RowMsg = raw_msg
                    conn_gui.data.DecodeMsg()
                    if conn_gui.data.sync_ok in conn_gui.data.message[0]:
                        conn_gui.sync_status.config(text="Synced!", fg="green")
                        conn_gui.btn_start_stream["state"] = "normal"
                        conn_gui.save_check["state"] = "normal"
                        conn_gui.btn_add_chart["state"] = "normal"
                        conn_gui.btn_kill_chart["state"] = "normal"
                        conn_gui.ch_status["text"] = conn_gui.data.message[1]
                        conn_gui.data.syncChannels = int(conn_gui.data.message[1])
                        conn_gui.data.genChannels()
                        conn_gui.data.buildData()
                        conn_gui.data.genFileName()
                        print(conn_gui.data.channels, conn_gui.data.yData)
                        self.threading = False
                        break
                        
                    else:
                        print(f"Unexpected response: {conn_gui.data.message[0]}")
                
                # Check if threading should stop
                if not self.threading:
                    break
                    
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error in serialSync: {e}")
                conn_gui.sync_status.config(text="Error", fg="red")
                break
                
            cnt += 1
            if cnt > self.sync_cnt:
                cnt = 0
                conn_gui.sync_status.config(text="Sync timeout", fg="red")
                print("Sync timeout - no response from device")
                time.sleep(0.5)
        
        print("serialSync thread ended")

    def SerialDataStream(self, gui):
        self.threading = True
        cnt = 0 
        while self.threading:
            try:
                self.ser.write(gui.data.startStream.encode())
                
                raw_msg = self.ser.readline()
                if raw_msg and len(raw_msg) > 1:  # Only process non-empty messages
                    gui.data.RowMsg = raw_msg
                    gui.data.DecodeMsg()
                    gui.data.streamDataCheck()
                    if gui.data.streamData:
                        gui.data.SetRefTime()
                        print(f"Row message {gui.data.RowMsg}, Msg : {gui.data.message}")
                        break
                else:
                    if raw_msg == b'':
                        print("Received empty message from serial port")
                        
            except Exception as e:
                print("Error in datastream:")
                print(e)
        
        # Schedule the initial chart update after the stream starts
        gui.root.after(40, gui.updateChart) # Schedule the first update

        while self.threading :
            try:
                gui.data.RowMsg = self.ser.readline()
                gui.data.DecodeMsg()
                gui.data.streamDataCheck()
                if gui.data.streamData:
                    gui.data.updateX()
                    gui.data.updateY()
                    gui.data.adjustData()
                # print(gui.data.xData[-1])
                # print(gui.data.yData[-1][0])
                if gui.save:
                    t1 = threading.Thread(target = gui.data.saveData , args=(gui,),daemon=True)
                    t1.start()
            except Exception as e :
                print(f"Error occured in streamData : {e}")
            

if __name__ == "__main__":
    SerialCtrl()