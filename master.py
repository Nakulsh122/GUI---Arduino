from gui_master import RootGUI ,ComGUI
from data_com_ctrl import DataMaster
from serial_master import SerialCtrl
Serial = SerialCtrl()
MyData = DataMaster()
RootMaster = RootGUI(Serial , MyData)
ComMaster = ComGUI(RootMaster.root,Serial,MyData)

RootMaster.root.mainloop()#pass the main root to the ComGui 