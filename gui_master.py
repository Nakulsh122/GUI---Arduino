from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import matplotlib.pyplot as plt
from functools import partial
import numpy as np

# Enhanced dark mode color scheme
bg_dark = "#1e1e1e"       # Main background
fg_light = "#ffffff"      # Primary text
bg_frame = "#2d2d2d"      # Frame background
bg_button = "#404040"     # Button background
bg_button_hover = "#505050"  # Button hover
accent_color = "#0078d4"  # Accent blue
success_color = "#00ff88" # Success green
warning_color = "#ffb347" # Warning orange
error_color = "#ff6b6b"   # Error red
bg_input = "#383838"      # Input field background
border_color = "#505050"  # Border color

class RootGUI:
    def __init__(self,serial,data):
        self.root = Tk()  # initialising the root element.
        self.root.title("Serial Communication GUI")
        self.root.geometry("400x120")
        self.root.resizable(True, True)
        self.root.config(bg=bg_dark)
        self.serial = serial
        self.data = data
        self.root.protocol("WM_DELETE_WINDOW", self.closeWindow)

    def closeWindow(self):
        print("Closing the Window")
        self.root.destroy()
        self.serial.serialClose()
        self.serial.threading = False

class ComGUI:
    def __init__(self, root, serial,data):  # initialise the comGUI frame
        self.root = root
        self.serial = serial  # include the serial controller in the gui
        self.data = data
        self.conn_menu = None  # Initialize connection menu reference
        self.frame = LabelFrame(
            self.root, text="Com Manager", bg=bg_frame, fg=fg_light, padx=10, pady=10,
            font=("Arial", 10, "bold"), bd=1, relief="solid", highlightbackground=border_color
        )
        self.label_com = Label(
            self.frame,
            text="Available Port(s):",
            bg=bg_frame,
            fg=fg_light,
            width=15,
            anchor="w",
            font=("Arial", 9)
        )
        self.label_bodR = Label(
            self.frame, text="Bode Rate", bg=bg_frame, fg=fg_light, width=15, anchor="w",
            font=("Arial", 9)
        )
        self.ComOptMenu()
        self.BodeRateMenu()
        self.btn_refresh = Button(
            self.frame,
            text="Refresh",
            bg=bg_button,
            fg=fg_light,
            width=10,
            command=self.refresh_menu,
            activebackground=bg_button_hover,
            activeforeground=fg_light,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.btn_connect = Button(
            self.frame,
            text="Connect",
            bg=accent_color,
            fg=fg_light,
            width=10,
            state="disabled",
            command=self.serialConnect,
            activebackground="#0066bb",
            activeforeground=fg_light,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )
        self.Publish()
        pass

    def ComOptMenu(self):
        # dropdow for the com options
        self.serial.getComList()
        self.clicked_com = StringVar()  # store the clicked Options
        self.clicked_com.set(self.serial.comList[0])
        self.drop_com = OptionMenu(
            self.frame,
            self.clicked_com,
            *self.serial.comList,
            command=self.Connect_ctrl,
        )
        self.drop_com.config(
            width=10, 
            bg=bg_input, 
            fg=fg_light,
            activebackground=bg_button_hover,
            activeforeground=fg_light,
            highlightbackground=border_color,
            highlightthickness=1,
            relief="solid",
            font=("Arial", 9),
            bd=1
        )
        # Configure the dropdown menu itself
        menu = self.drop_com['menu']
        menu.config(
            bg=bg_frame,
            fg=fg_light,
            activebackground=accent_color,
            activeforeground=fg_light,
            font=("Arial", 9)
        )

    def BodeRateMenu(self):
        # dropdow for the Bode options
        self.Bode_rates = [
            110,
            300,
            600,
            1200,
            2400,
            4800,
            9600,
            14400,
            19200,
            28800,
            38400,
            57600,
            115200,
            128000,
            256000,
        ]
        self.clicked_Bode = StringVar()  # store the clicked Options
        self.clicked_Bode.set(self.Bode_rates[0])
        self.drop_Bode = OptionMenu(
            self.frame, self.clicked_Bode, *self.Bode_rates, command=self.Connect_ctrl
        )
        self.drop_Bode.config(
            width=10, 
            bg=bg_input, 
            fg=fg_light,
            activebackground=bg_button_hover,
            activeforeground=fg_light,
            highlightbackground=border_color,
            highlightthickness=1,
            relief="solid",
            font=("Arial", 9),
            bd=1
        )
        # Configure the dropdown menu itself
        menu = self.drop_Bode['menu']
        menu.config(
            bg=bg_frame,
            fg=fg_light,
            activebackground=accent_color,
            activeforeground=fg_light,
            font=("Arial", 9)
        )

    def Publish(self):
        # will publish the component on the root
        self.frame.grid(
            row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5
        )  # we add a grid to the frame so that it can be placed
        self.label_com.grid(column=1, row=2, padx=5, pady=2)
        self.drop_com.grid(column=2, row=2, padx=5, pady=2)
        self.label_bodR.grid(column=1, row=3, padx=5, pady=2)
        self.drop_Bode.grid(column=2, row=3, padx=5, pady=2)
        self.btn_refresh.grid(column=3, row=2, padx=5, pady=2)
        self.btn_connect.grid(column=3, row=3, padx=5, pady=2)
        pass

    def Connect_ctrl(self, other):
        # this will be used to control the connect button
        if self.clicked_com.get() == "-" or self.clicked_Bode.get() == "-":
            self.btn_connect.config(state="disabled", bg=bg_button)
        else:
            self.btn_connect.config(state="normal", bg=accent_color)
        pass

    def refresh_menu(self):
        self.serial.getComList()
        # Update the OptionMenu with new list of COM ports
        menu = self.drop_com["menu"]
        menu.delete(0, "end")
        for port in self.serial.comList:
            menu.add_command(label=port, command=lambda value=port: self.clicked_com.set(value))

        self.clicked_com.set(self.serial.comList[0] if self.serial.comList else "-")
        self.clicked_Bode.set(self.Bode_rates[0])
        self.Connect_ctrl(None) # Call to update connect button state

    def serialConnect(self):
        if self.btn_connect["text"] in "Connect":
            self.serial.serialConnect(self)
            if self.serial.ser.status:
                self.btn_connect["text"] = "Disconnect"
                self.btn_connect.config(bg=error_color, activebackground="#ff5555")
                self.btn_refresh["state"] = "disabled"
                self.btn_refresh.config(bg=bg_button, fg="#888888")
                self.drop_com["state"] = "disabled"
                self.drop_com.config(bg=bg_button, fg="#888888")
                self.drop_Bode["state"] = "disabled"
                self.drop_Bode.config(bg=bg_button, fg="#888888")
                InfoMsg = f"Connected to {self.clicked_com.get() } at {self.clicked_Bode.get()}"
                messagebox.showinfo("Connection Status", InfoMsg)

                # Display the connection menu
                self.conn_menu = ConnGUI(self.root, self.serial, self.data)

                # Start the sync thread - FIXED: Pass conn_menu instead of self
                self.serial.t1 = threading.Thread(
                    target=self.serial.serialSync,
                    args=(self.conn_menu,),  # Pass ConnGUI instance
                    daemon=True,
                )
                self.serial.t1.start()
            else:
                ErrorMsg = f"Error connecting to {self.clicked_com.get()} at {self.clicked_Bode.get()}"
                messagebox.showerror("Connection Error", ErrorMsg)
        else:
            self.serial.threading = False
            self.conn_menu.save = False
            if self.conn_menu:
                self.conn_menu.ConnGUIClose()
                self.conn_menu.data.clearData()
            self.serial.serialClose()
            self.btn_connect["text"] = "Connect"
            self.btn_connect.config(bg=accent_color, activebackground="#0066bb")
            self.btn_refresh["state"] = "active"
            self.btn_refresh.config(bg=bg_button, fg=fg_light)
            self.drop_com["state"] = "active"
            self.drop_com.config(bg=bg_input, fg=fg_light)
            self.drop_Bode["state"] = "active"
            self.drop_Bode.config(bg=bg_input, fg=fg_light)
            # start closing the connection
            pass

class ConnGUI:
    def __init__(self, root, serial, data):
        self.padx = 10
        self.pady = 10
        self.root = root
        self.serial = serial
        self.data = data
        self.save = False
        self.frame = LabelFrame(
            self.root,
            text="Connection Manager",
            bg=bg_frame,
            fg=fg_light,
            padx=self.padx,
            pady=self.pady,
            font=("Arial", 10, "bold"),
            bd=1,
            relief="solid",
            highlightbackground=border_color
        )

        self.sync_Label = Label(
            self.frame,
            text="Sync Status:",
            bg=bg_frame,
            fg=fg_light,
            width=15,
            anchor="w",
            padx=self.padx,
            pady=self.pady,
            font=("Arial", 9)
        )

        self.sync_status = Label(
            self.frame,
            text="...Sync...",
            bg=bg_frame,
            fg=warning_color,
            width=15,
            anchor="w",
            font=("Arial", 9, "bold")
        )

        self.ch_label = Label(
            self.frame,
            text="Active Channels:",
            bg=bg_frame,
            fg=fg_light,
            width=15,
            anchor="w",
            font=("Arial", 9)
        )

        self.ch_status = Label(
            self.frame,
            text="...",
            bg=bg_frame,
            fg=fg_light,
            width=15,
            anchor="w",
            font=("Arial", 9)
        )

        self.btn_start_stream = Button(
            self.frame,
            text="Start",
            state="disabled",
            bg=success_color,
            fg=bg_dark,
            width=5,
            command=self.start_stream,
            activebackground="#00cc66",
            activeforeground=bg_dark,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )

        self.btn_stop_stream = Button(
            self.frame,
            text="Stop",
            state="disabled",
            bg=error_color,
            fg=fg_light,
            width=5,
            command=self.stop_stream,
            activebackground="#ff5555",
            activeforeground=fg_light,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )

        self.btn_add_chart = Button(
            self.frame,
            text="Add Chart",
            bg=accent_color,
            fg=fg_light,
            command=self.add_chart,
            activebackground="#0066bb",
            activeforeground=fg_light,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )

        self.btn_kill_chart = Button(
            self.frame,
            text="Kill Chart",
            bg=bg_button,
            fg=fg_light,
            command=self.kill_chart,
            activebackground=bg_button_hover,
            activeforeground=fg_light,
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2"
        )

        self.save = False
        self.SaveVar = IntVar()
        self.save_check = Checkbutton(
            self.frame,
            text="Save Data",
            variable=self.SaveVar,
            onvalue=1,
            offvalue=0,
            bg=bg_frame,
            fg=fg_light,
            activeforeground=fg_light,
            selectcolor=accent_color,
            activebackground=bg_frame,
            command=self.save_data,
            highlightbackground=bg_frame,
            relief="flat",
            font=("Arial", 9),
            cursor="hand2"
        )

        self.ConnGUIOpen()
        self.chartMaster = DisplayGUI(self.root ,self.serial,self.data)

    def ConnGUIOpen(self):
        self.root.geometry("1000x120")
        self.frame.grid(
            row=0,
            column=4,
            rowspan=3,
            columnspan=3,
            padx=5,
            pady=5,
        )
        self.frame.config(
            width=60
        )
        self.sync_Label.grid(column=1, row=1, padx=5, pady=2)
        self.sync_status.grid(column=2, row=1, padx=5, pady=2)
        self.ch_label.grid(column=1, row=2, padx=5, pady=2)
        self.ch_status.grid(column=2, row=2, padx=5, pady=2)
        self.btn_start_stream.grid(column=3, row=1, padx=5, pady=2)
        self.btn_stop_stream.grid(column=3, row=2, padx=5, pady=2)
        self.btn_add_chart.grid(column=4, row=1, padx=5, pady=2)
        self.btn_kill_chart.grid(column=4, row=2, padx=5, pady=2)
        self.save_check.grid(column=5, row=1, padx=5, pady=2)

    def ConnGUIClose(self):
        for widget in self.frame.winfo_children():  # list of all children inside the frame
            widget.destroy()
        self.frame.destroy()
        self.root.geometry("800x120")

    def start_stream(self):
        print("starting Stream")
        self.btn_start_stream["state"] = "disabled"
        self.btn_stop_stream["state"]  = "normal"
        self.serial.t1 = threading.Thread(
            target =self.serial.SerialDataStream,
            args=(self,),
            daemon=True
        )
        self.serial.t1.start()
        pass

    def stop_stream(self):
        print("Stopping Stream")
        self.btn_start_stream["state"] = "active"
        self.btn_stop_stream["state"] = "disabled"
        self.serial.serialStop(self)
        self.serial.threading = False
        pass

    def updateChart(self):
        try:
            mydisplayChannels = []
            for Channel in range(len(self.chartMaster.ViewVar)):
                self.chartMaster.figs[Channel][1].clear()
                for cnt , state in enumerate(self.chartMaster.ViewVar[Channel]):
                    if state.get():
                        MyChannel = self.chartMaster.OptionVar[Channel][cnt].get()
                        mydisplayChannels.append(MyChannel)
                        channelIndex = self.data.channelNum[MyChannel]-1

                        funcName =  self.chartMaster.FunVar[Channel][cnt].get()
                        self.chart = self.chartMaster.figs[Channel][1]
                        self.color = self.data.channelColor[MyChannel] 
                        self.y = self.data.ydisplay[channelIndex]
                        self.x = self.data.xdisplay
                        self.data.functions[funcName](self)
                        min_len = min(len(self.x), len(self.y))
                        self.x = self.x[-min_len:]
                        self.y = self.y[-min_len:]
                self.chartMaster.figs[Channel][1].grid(
                    color = 'b',
                    linestyle = '-',
                    linewidth = 0.2
                )
                self.chartMaster.figs[Channel][0].canvas.draw()
            print(mydisplayChannels)
        except Exception as e:
            print(f"Error in chart updation : {e}")
        if self.serial.threading:
            self.root.after(40,self.updateChart) # recall every 40 ms 

    def add_chart(self):
        print("Add chart")
        self.chartMaster.addChannelMan()
        pass

    def kill_chart(self):
        print("Kill chart requested")
        try:
            if len(self.chartMaster.frames) > 0:
                totalFrame = len(self.chartMaster.frames)-1
                self.chartMaster.frames[totalFrame].destroy()
                self.chartMaster.figs.pop()
                self.chartMaster.controlFrames[totalFrame][0].destroy()
                self.chartMaster.controlFrames.pop()

                self.chartMaster.channelFrames[totalFrame][0].destroy()
                self.chartMaster.channelFrames.pop()

                self.chartMaster.ViewVar.pop()
                self.chartMaster.OptionVar.pop()
                self.chartMaster.FunVar.pop()
                self.chartMaster.adjustRoot()

        except Exception as e:
            print("Error occurred while killing chart:", str(e))

    def save_data(self):
        print(self.SaveVar.get())
        if self.save:
            self.save = False
        else:
            self.save=True
        pass

class DisplayGUI:
    def __init__(self,root,serial ,data):
        self.root = root
        self.serial = serial
        self.data = data
        self.frames = []
        self.controlFrames = []
        self.framesCol = 0
        self.framesRow = 4
        self.totalFrames = 0
        self.padx = 10
        self.pady = 10
        self.figs = []
        self.channelFrames = []
        self.ViewVar = []
        self.OptionVar = []
        self.FunVar = []

    def addChannelMan(self):
        self.AddMasterFrame()
        self.adjustRoot()
        self.AddGraph()
        self.addchannelframe()
        self.AddBtnFrame()

    def AddMasterFrame(self):
        self.frames.append(LabelFrame(
            self.root,
            text = f"Display Manager - {len(self.frames)+1}",
            padx = self.padx,
            pady = self.pady,
            bg=bg_frame,
            fg=fg_light,
            font=("Arial", 10, "bold"),
            bd=1,
            relief="solid",
            highlightbackground=border_color
        ))
        self.totalFrames = len(self.frames)-1
        if self.totalFrames%2 == 0:
            self.framesCol = 0
        else:
            self.framesCol = 9

        self.framesRow = 4 + 4 * int(self.totalFrames/2)
        self.frames[self.totalFrames].grid(padx = self.padx , pady = self.pady,column = self.framesCol,row = self.framesRow , columnspan = 9 ,sticky = NW)

    def adjustRoot(self):
        self.totalFrames = len(self.frames)-1
        if self.totalFrames >= 0: # Ensures RootW is set even for the first frame
            RootW = 800 * (1 if self.totalFrames == 0 else 2) # Adjusted logic for total frames
        else:
            RootW = 800

        if self.totalFrames + 1 == 0: # This condition might be problematic if totalFrames is -1
            RootH = 120
        else:
            RootH = 120 + 430 * (int(self.totalFrames/2)+1)
        self.root.geometry(f"{RootW}x{RootH}")
        pass

    def AddGraph(self):
        self.figs.append([])
        # Configure Matplotlib figure for dark mode
        plt.style.use('dark_background')  # Use matplotlib's dark style
        fig = plt.Figure(figsize=(7, 5), dpi=80, facecolor=bg_frame)
        ax = fig.add_subplot(111, facecolor=bg_dark)

        # Enhanced dark mode styling for matplotlib
        ax.tick_params(axis='x', colors=fg_light, labelsize=9)
        ax.tick_params(axis='y', colors=fg_light, labelsize=9)
        ax.yaxis.label.set_color(fg_light)
        ax.xaxis.label.set_color(fg_light)
        ax.title.set_color(fg_light)

        # Grid styling
        ax.grid(True, color=border_color, alpha=0.3, linewidth=0.5)

        # Enhanced spine styling
        for spine in ax.spines.values():
            spine.set_color(border_color)
            spine.set_linewidth(1)

        self.figs[self.totalFrames].append(fig)
        self.figs[self.totalFrames].append(ax)

        canvas = FigureCanvasTkAgg(self.figs[self.totalFrames][0], master=self.frames[self.totalFrames])
        canvas.get_tk_widget().config(bg=bg_frame, highlightbackground=border_color, highlightthickness=1)
        self.figs[self.totalFrames].append(canvas)

        self.figs[self.totalFrames][2].get_tk_widget().grid(
            column=1, row=0, rowspan=17, columnspan=4, sticky=N, padx=5, pady=5)

    def AddBtnFrame(self):
        btn_w = 4
        btn_h = 2
        self.controlFrames.append([])
        self.controlFrames[self.totalFrames].append(
            LabelFrame(
                self.frames[self.totalFrames], 
                pady=self.pady,
                bg=bg_frame,
                highlightbackground=border_color,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )
        )
        self.controlFrames[self.totalFrames][0].grid(column=0, row=0, padx=self.padx, pady=self.pady, sticky=N)
        
        self.controlFrames[self.totalFrames].append(
            Button(
                self.controlFrames[self.totalFrames][0], 
                text=" + ",
                width=btn_w, 
                height=btn_h,
                bg=success_color, 
                fg=bg_dark, 
                activebackground="#00cc66", 
                activeforeground=bg_dark,
                relief="flat", 
                bd=0,
                font=("Arial", 12, "bold"),
                cursor="hand2",
                command=partial(self.AddChannel, self.channelFrames[self.totalFrames])
            )
        )
        self.controlFrames[self.totalFrames][1].grid(column=0, row=0, padx=self.padx, pady=self.pady)
        
        self.controlFrames[self.totalFrames].append(
            Button(
                self.controlFrames[self.totalFrames][0], 
                text=" - ",
                width=btn_w, 
                height=btn_h,
                bg=error_color, 
                fg=fg_light, 
                activebackground="#ff5555", 
                activeforeground=fg_light,
                relief="flat", 
                bd=0,
                font=("Arial", 12, "bold"),
                cursor="hand2",
                command=partial(self.deleteChannel, self.channelFrames[self.totalFrames])
            )
        )
        self.controlFrames[self.totalFrames][2].grid(column=2, row=0, padx=self.padx, pady=self.pady)

    def addchannelframe(self):
        self.channelFrames.append([])
        self.ViewVar.append([])
        self.OptionVar.append([])
        self.FunVar.append([])
        self.channelFrames[self.totalFrames].append(
            LabelFrame(
                self.frames[self.totalFrames],
                pady=self.pady,
                padx=self.padx,
                bg=bg_frame,
                highlightbackground=border_color,
                highlightthickness=1,
                bd=1,
                relief="solid"
            )
        )
        self.channelFrames[self.totalFrames].append(self.totalFrames)
        self.channelFrames[self.totalFrames][0].grid(
            column=0,
            row=1,
            padx=self.padx,
            pady=self.pady,
            rowspan=16,
            sticky=N
        )

        self.AddChannel(self.channelFrames[self.totalFrames])

    def AddChannel(self,channelFrames):
        if len(channelFrames[0].winfo_children()) < 8:
            NewFrameChannel = LabelFrame(
                channelFrames[0], 
                bg=bg_frame, 
                fg=fg_light,
                highlightbackground=border_color, 
                highlightthickness=1,
                bd=1,
                relief="solid"
            )

            NewFrameChannel.grid(
                column=0, 
                row=len(channelFrames[0].winfo_children()),
                padx=2,
                pady=2,
                sticky="ew"
            )

            self.ViewVar[channelFrames[1]].append(IntVar())
            Ch_btn = Checkbutton(
                NewFrameChannel, 
                variable=self.ViewVar[channelFrames[1]][len(self.ViewVar[channelFrames[1]])-1],
                onvalue=1, 
                offvalue=0, 
                bg=bg_frame, 
                fg=fg_light,
                activebackground=bg_frame, 
                activeforeground=fg_light,
                selectcolor=accent_color,
                highlightbackground=bg_frame,
                relief="flat",
                font=("Arial", 9),
                cursor="hand2"
            )
            Ch_btn.grid(row=0, column=0, padx=self.padx, pady=2)
            self.ChannelOption(NewFrameChannel,channelFrames[1])
            self.FuncOption(NewFrameChannel,channelFrames[1])

    def ChannelOption(self, frame, ChannelFrameNumber):
        self.OptionVar[ChannelFrameNumber].append(StringVar())

        bds = self.data.channels
        self.OptionVar[ChannelFrameNumber][len(self.OptionVar[ChannelFrameNumber])-1].set(bds[0])
        drop_ch = OptionMenu(frame, self.OptionVar[ChannelFrameNumber][len(self.OptionVar[ChannelFrameNumber])-1], *bds)
        drop_ch.config(
            width=5, 
            bg=bg_input, 
            fg=fg_light,
            activebackground=bg_button_hover, 
            activeforeground=fg_light,
            highlightbackground=border_color, 
            highlightthickness=1,
            relief="solid",
            font=("Arial", 8),
            bd=1
        )
        # Configure the dropdown menu itself
        menu = drop_ch['menu']
        menu.config(
            bg=bg_frame,
            fg=fg_light,
            activebackground=accent_color,
            activeforeground=fg_light,
            font=("Arial", 8)
        )
        drop_ch.grid(row=0, column=1, padx=1, pady=2)

    def FuncOption(self, frame, ChannelFrameNumber):
        self.FunVar[ChannelFrameNumber].append(StringVar())

        bds = [func for func in self.data.functions.keys()]
        self.FunVar[ChannelFrameNumber][len(self.FunVar[ChannelFrameNumber])-1].set(bds[0])
        drop_ch = OptionMenu(frame, self.FunVar[ChannelFrameNumber][len(self.FunVar[ChannelFrameNumber])-1], *bds)
        drop_ch.config(
            width=5, 
            bg=bg_input, 
            fg=fg_light,
            activebackground=bg_button_hover, 
            activeforeground=fg_light,
            highlightbackground=border_color, 
            highlightthickness=1,
            relief="solid",
            font=("Arial", 8),
            bd=1
        )
        # Configure the dropdown menu itself
        menu = drop_ch['menu']
        menu.config(
            bg=bg_frame,
            fg=fg_light,
            activebackground=accent_color,
            activeforeground=fg_light,
            font=("Arial", 8)
        )
        drop_ch.grid(row=0, column=2, padx=1, pady=2)

    def deleteChannel(self, channelframe):
        if len(channelframe[0].winfo_children()) > 0 : # Changed condition to allow deleting the very last channel
            channelframe[0].winfo_children()[-1].destroy() # Destroys the last added child widget
            self.ViewVar[channelframe[1]].pop()
            self.OptionVar[channelframe[1]].pop()
            self.FunVar[channelframe[1]].pop()

if __name__ == "__main__":
    RootGUI()
    ComGUI()
    ConnGUI()
    DisplayGUI()    