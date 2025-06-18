# Serial Communication and Data Visualization GUI

This project provides a Python-based GUI application for serial communication, real-time data streaming, and interactive data visualization. It allows users to connect to a serial device (e.g., an Arduino), synchronize with it, stream data, and display the received data on dynamic charts with various processing options.

## Table of Contents

1.  [Features](#features)
2.  [Files Overview](#files-overview)
3.  [Class Reference](#class-reference)
    * [DataMaster](#datamaster)
    * [SerialCtrl](#serialctrl)
    * [RootGUI](#rootgui)
    * [ComGUI](#comgui)
    * [ConnGUI](#conngui)
    * [DisplayGUI](#displaygui)
4.  [Data Flow and Structures](#data-flow-and-structures)
    * [Conceptual Data Flow Diagram](#conceptual-data-flow-diagram)
    * [Key Data Structures and Their Contents](#key-data-structures-and-their-contents)
5.  [Threading Model](#threading-model)
6.  [Graphing and Visualization](#graphing-and-visualization)
    * [Chart Creation](#chart-creation)
    * [Chart Update Mechanism](#chart-update-mechanism)
    * [Chart Deletion](#chart-deletion)
    * [Data Processing Functions](#data-processing-functions)
7.  [How to Run (Assuming a `sender.py` for testing)](#how-to-run-assuming-a-senderpy-for-testing)

## Features

* **Serial Port Management:** Automatically detects available COM ports and allows baud rate selection.
* **Device Synchronization:** Handshake mechanism to synchronize with the connected serial device.
* **Real-time Data Streaming:** Continuously receives and processes data from the serial port.
* **Dynamic Data Visualization:** Plots real-time data on interactive charts using Matplotlib.
* **Multiple Channel Support:** Handles data from multiple channels.
* **Data Processing Options:** Applies filters (Savitzky-Golay, Digital Elliptic) to streamed data.
* **Data Saving:** Option to save streamed data to a CSV file.
* **Modular GUI:** Tkinter-based GUI with distinct sections for communication, connection, and display.
* **Dark Mode Theme:** Enhanced dark mode for a better user experience.

## Files Overview

* `master.py`: The main entry point of the application. Initializes the core classes and starts the Tkinter event loop.
* `data_com_ctrl.py`: Contains the `DataMaster` class, responsible for handling data decoding, processing, storage, and applying various data transformations.
* `serial_master.py`: Contains the `SerialCtrl` class, managing serial port connections, synchronization, and data streaming threads.
* `gui_master.py`: Implements all the Tkinter GUI components, including `RootGUI`, `ComGUI`, `ConnGUI`, and `DisplayGUI`.
* `sender.py`: (Provided for testing) A simulated serial device that sends synthetic data, mimicking an Arduino or similar microcontroller.

## Class Reference

### DataMaster

`data_com_ctrl.py`

This class is central to managing, processing, and preparing data for display and storage.

**Data Structures:**

* `sync`: (String) "#?#\n" - Synchronization command sent to the device.
* `startStream`: (String) "#s#\n" - Command to start data streaming.
* `stopStream`: (String) "#A#\n" - Command to stop data streaming.
* `sync_ok`: (String) "!" - Expected response from device for successful sync.
* `syncChannels`: (Integer) Stores the number of active data channels reported by the device.
* `xData`: (List of Floats) Stores time-based X-axis data points.
* `yData`: (List of Lists of Floats) Stores raw Y-axis data points, where each inner list corresponds to a channel.
* `functions`: (Dictionary) Maps descriptive string names (e.g., "RowData", "Voltage") to the corresponding data processing methods within the class.
* `RowMsg`: (Bytes) Stores the raw byte message received from the serial port.
* `message`: (List of Strings) Stores the decoded and split string message parts.
* `messageLen`: (Integer) Expected total length of the numerical data within the message, as reported by the device.
* `messageLenCheck`: (Integer) Calculated total length of the numerical data for verification.
* `streamData`: (Boolean) Flag indicating if data streaming is active and valid.
* `IntMsg`: (List of Floats) Stores the integer/float representation of the decoded data values.
* `channels`: (List of Strings) Stores channel names (e.g., "Ch0", "Ch1") after synchronization.
* `DisplayTime`: (Integer) Time window (in seconds) for data displayed on the chart.
* `channelNum`: (Dictionary) Maps channel names to their numerical index (0-7).
* `channelColor`: (Dictionary) Maps channel names to predefined colors for plotting.
* `RefTime`: (Float) Stores the `time.perf_counter()` value at the start of data streaming for relative time calculation.
* `filename`: (String) Dynamically generated filename for saving data (e.g., "YYYYMMMDDHHMMSS.csv").

**Functions:**

* `__init__(self)`: Initializes all data structures and command strings.
* `DecodeMsg(self)`: Decodes the `RowMsg` byte string into a UTF-8 string, splits it by '#' delimiter, and parses the message length for validation. Handles potential decoding errors.
* `IntMsgFunc(self)`: Converts the string elements in `self.message` into a list of floats (`self.IntMsg`).
* `streamDataCheck(self)`: Verifies if the received message length matches the expected length and if the number of channels matches `syncChannels` to confirm valid stream data. If valid, calls `IntMsgFunc`.
* `SetRefTime(self)`: Sets `self.RefTime` to the current `time.perf_counter()` if it hasn't been set yet. Used as the starting point for relative time in `xData`.
* `updateX(self)`: Appends the current relative time (from `RefTime`) to `self.xData`.
* `updateY(self)`: Appends the current `IntMsg` values to their respective channel lists within `self.yData`.
* `adjustData(self)`: Manages the display window for data. If the time span of `xData` exceeds `DisplayTime`, it removes the oldest data points from both `xData` and `yData`. It then prepares `xdisplay` and `ydisplay` (NumPy arrays) for plotting.
* `genChannels(self)`: Generates `self.channels` list (e.g., `['Ch1', 'Ch2', ...]`) based on `syncChannels`.
* `buildData(self)`: Initializes `self.yData` as a list of empty lists, one for each `syncChannels`, to prepare for incoming data.
* `RowData(self, gui)`: Plots the raw data (`gui.y` vs `gui.x`) on the chart. This function is callable via the `functions` dictionary.
* `Voltage(self, gui)`: Converts raw data (`gui.y`) to voltage values (assuming 12-bit ADC, 3.3V reference) and plots it. This function is callable via the `functions` dictionary.
* `savgo(self, gui)`: Applies a Savitzky-Golay filter to `gui.y` data and plots the filtered output. This function is callable via the `functions` dictionary.
* `digi_filter(self, gui)`: Applies an Elliptic digital filter to `gui.y` data and plots the filtered output. This function is callable via the `functions` dictionary.
* `genFileName(self)`: Generates a unique filename for saving data based on the current timestamp.
* `saveData(self, gui)`: Appends the current timestamp and `IntMsg` data to the CSV file specified by `self.filename`. This is typically run in a separate thread.
* `clearData(self)`: Resets all internal data buffers and flags to their initial empty states, preparing for a new stream.

### SerialCtrl

`serial_master.py`

Handles the low-level serial communication, connection management, and threading for synchronization and data streaming.

**Data Structures:**

* `comList`: (List of Strings) Stores available COM ports.
* `ser`: (serial.Serial object) The PySerial object for managing the serial connection.
* `ser.status`: (Boolean, custom attribute) Indicates if the serial port is currently open.
* `sync_cnt`: (Integer) Counter limit for the synchronization attempt loop.
* `threading`: (Boolean) Global flag to control the execution of serial communication threads.

**Functions:**

* `__init__(self)`: Initializes `comList`, `ser` object, sets `ser.status` to `False`, and initializes `sync_cnt` and `threading` flag.
* `getComList(self)`: Populates `self.comList` with available serial ports on the system.
* `serialConnect(self, gui)`: Attempts to open a serial connection using the selected COM port and baud rate from the GUI. Updates `self.ser.status`.
* `serialClose(self)`: Closes the active serial connection if open.
* `serialStop(self, gui)`: Sends the `stopStream` command to the connected device.
* `serialSync(self, conn_gui)`: A threaded function that attempts to synchronize with the serial device. It repeatedly sends a sync command (`#?#`) and waits for a specific response (`!#<channels>#`). Upon successful synchronization, it updates the GUI (sync status, active channels) and prepares `DataMaster` for data reception. It sets `self.threading = False` on successful sync or error.
* `SerialDataStream(self, gui)`: A threaded function responsible for the main data streaming.
    * Initially sends the `startStream` command (`#s#`) and waits for the first valid data packet.
    * Once streaming begins, it continuously reads data from the serial port, passes it to `gui.data` (an instance of `DataMaster`) for decoding and processing (`updateX`, `updateY`, `adjustData`).
    * If `gui.save` is enabled, it spawns a separate thread to save the data using `gui.data.saveData`.
    * Crucially, it uses `gui.root.after(40, gui.updateChart)` to schedule the GUI chart updates on the main Tkinter thread, ensuring responsiveness and preventing GUI freezing.

### RootGUI

`gui_master.py`

The main Tkinter root window and top-level GUI controller.

**Data Structures:**

* `root`: (Tkinter Tk object) The main application window.
* `serial`: (SerialCtrl object) Instance of the serial communication controller.
* `data`: (DataMaster object) Instance of the data management controller.

**Functions:**

* `__init__(self, serial, data)`: Initializes the main Tkinter window, sets its title, geometry, and links the `serial` and `data` controller objects. Sets `closeWindow` as the protocol for closing the window.
* `closeWindow(self)`: Handles the application shutdown process, destroying the Tkinter root, closing the serial port, and setting `serial.threading` to `False` to stop any running threads.

### ComGUI

`gui_master.py`

Manages the COM port selection, baud rate setting, and connection/disconnection functionalities.

**Data Structures:**

* `root`: (Tkinter Tk object) Reference to the main application window.
* `serial`: (SerialCtrl object) Reference to the serial communication controller.
* `data`: (DataMaster object) Reference to the data management controller.
* `conn_menu`: (ConnGUI object) Reference to the connection management GUI, created upon successful serial connection.
* `frame`: (Tkinter LabelFrame) The main frame for COM manager widgets.
* `label_com`, `label_bodR`: (Tkinter Label) Labels for COM port and Baud Rate.
* `clicked_com`, `clicked_Bode`: (Tkinter StringVar) Variables to hold selected COM port and baud rate from dropdowns.
* `drop_com`, `drop_Bode`: (Tkinter OptionMenu) Dropdown menus for COM port and Baud Rate selection.
* `btn_refresh`, `btn_connect`: (Tkinter Button) Buttons for refreshing COM ports and connecting/disconnecting.

**Functions:**

* `__init__(self, root, serial, data)`: Initializes the frame and all widgets related to COM port management. Calls `ComOptMenu`, `BodeRateMenu`, and `Publish`.
* `ComOptMenu(self)`: Populates and configures the COM port dropdown menu using `serial.comList`.
* `BodeRateMenu(self)`: Populates and configures the Baud Rate dropdown menu.
* `Publish(self)`: Arranges and displays all COM GUI widgets using the `grid` layout manager.
* `Connect_ctrl(self, other)`: Enables/disables the "Connect" button based on whether valid COM port and Baud Rate selections have been made.
* `refresh_menu(self)`: Updates the list of available COM ports in the dropdown menu.
* `serialConnect(self)`: Handles the logic for connecting and disconnecting the serial port.
    * **Connect:** Calls `serial.serialConnect()`. If successful, changes the button text to "Disconnect", updates button colors, disables other COM controls, shows a success message, creates an instance of `ConnGUI`, and starts the `serialSync` thread.
    * **Disconnect:** Sets `serial.threading` to `False`, closes `conn_menu`, clears `data`, calls `serial.serialClose()`, and reverts button/control states to "Connect" mode.

### ConnGUI

`gui_master.py`

Manages the connection status, data streaming controls (start/stop), chart adding/killing, and data saving options.

**Data Structures:**

* `root`, `serial`, `data`: References to the main application objects.
* `save`: (Boolean) Flag indicating whether data saving is active.
* `SaveVar`: (Tkinter IntVar) Variable linked to the "Save Data" checkbox.
* `frame`: (Tkinter LabelFrame) The main frame for connection manager widgets.
* `sync_Label`, `sync_status`: (Tkinter Label) Labels for synchronization status.
* `ch_label`, `ch_status`: (Tkinter Label) Labels for active channels status.
* `btn_start_stream`, `btn_stop_stream`: (Tkinter Button) Buttons to start and stop data streaming.
* `btn_add_chart`, `btn_kill_chart`: (Tkinter Button) Buttons to add and remove charts.
* `save_check`: (Tkinter Checkbutton) Checkbox to enable/disable data saving.
* `chartMaster`: (DisplayGUI object) Instance of the display/chart management GUI.
* `chart`, `color`, `x`, `y`: (Attributes set dynamically during `updateChart`) Temporary variables used to pass plotting context to `DataMaster`'s plotting functions.

**Functions:**

* `__init__(self, root, serial, data)`: Initializes the frame and all connection-related widgets. Sets up `chartMaster`.
* `ConnGUIOpen(self)`: Displays the connection manager frame and its widgets. Adjusts root window geometry.
* `ConnGUIClose(self)`: Destroys all widgets within the connection manager frame and the frame itself. Adjusts root window geometry back to initial size.
* `start_stream(self)`: Disables the "Start" button, enables "Stop", and starts the `SerialDataStream` thread in `serial_master`.
* `stop_stream(self)`: Enables the "Start" button, disables "Stop", calls `serial.serialStop()`, and sets `self.serial.threading` to `False` to halt data streaming.
* `updateChart(self)`: **Crucial for real-time plotting.** This method is called repeatedly by `self.root.after()` on the main Tkinter thread.
    * It iterates through each active chart and its selected channels/functions.
    * For each selected channel, it retrieves the appropriate data (`self.x`, `self.y`) and color.
    * It then dynamically calls the chosen data processing function (e.g., `self.data.RowData`, `self.data.Voltage`) from `self.data.functions` dictionary, passing `self` (the `ConnGUI` instance) as an argument. This allows the data function to access `self.chart`, `self.x`, `self.y`, and `self.color` for plotting.
    * Clears the Matplotlib axes (`.clear()`) and then re-plots the data.
    * Updates the chart canvas (`.canvas.draw()`) to reflect changes.
    * Recursively schedules itself to run again after 40 milliseconds (`self.root.after(40, self.updateChart)`), creating the animation effect.
* `add_chart(self)`: Calls `chartMaster.addChannelMan()` to add a new chart display area.
* `kill_chart(self)`: Calls `chartMaster.kill_chart()` to remove the most recently added chart display area.
* `save_data(self)`: Toggles the `self.save` boolean flag based on the "Save Data" checkbox state.

### DisplayGUI

`gui_master.py`

Manages the dynamic creation, display, and deletion of individual chart frames and their channel selection controls.

**Data Structures:**

* `root`, `serial`, `data`: References to the main application objects.
* `frames`: (List of Tkinter LabelFrame) Stores references to the main `LabelFrame` for each chart.
* `controlFrames`: (List of Lists of Tkinter Widgets) Stores the `LabelFrame` and buttons (`+`, `-`) for adding/deleting channels within each chart.
* `framesCol`, `framesRow`: (Integers) Used to calculate the grid position for new chart frames.
* `totalFrames`: (Integer) Index of the current (last added) chart frame.
* `figs`: (List of Lists) Stores Matplotlib `Figure` objects, `Axes` objects, and `FigureCanvasTkAgg` for each chart.
* `channelFrames`: (List of Lists) Stores the `LabelFrame` that contains channel selection widgets for each chart, along with an index for easy referencing.
* `ViewVar`: (List of Lists of Tkinter IntVar) Stores `IntVar` objects for the "View" checkboxes for each channel within each chart.
* `OptionVar`: (List of Lists of Tkinter StringVar) Stores `StringVar` objects for the channel selection dropdowns (e.g., "Ch0", "Ch1").
* `FunVar`: (List of Lists of Tkinter StringVar) Stores `StringVar` objects for the function selection dropdowns (e.g., "RowData", "Voltage").

**Functions:**

* `__init__(self, root, serial, data)`: Initializes all lists that will hold references to dynamically created GUI elements and data.
* `addChannelMan(self)`: Orchestrates the creation of a new chart display area, calling `AddMasterFrame`, `adjustRoot`, `AddGraph`, `addchannelframe`, and `AddBtnFrame`.
* `AddMasterFrame(self)`: Creates a new `LabelFrame` for a chart, adds it to `self.frames`, and calculates its `grid` position based on existing charts.
* `adjustRoot(self)`: Dynamically adjusts the size of the main `root` window to accommodate new charts, arranging them in a 2-column layout.
* `AddGraph(self)`:
    * Creates a Matplotlib `Figure` and `Axes` object.
    * **Applies dark mode styling to the Matplotlib figure and axes for consistent theme integration.** This includes `dark_background` style, custom colors for ticks, labels, title, grid, and spines.
    * Embeds the Matplotlib figure into a Tkinter `FigureCanvasTkAgg` widget.
    * Adds these `fig`, `ax`, and `canvas` objects to `self.figs` list.
    * Grids the `canvas` within the chart's `LabelFrame`.
* `AddBtnFrame(self)`: Creates a `LabelFrame` containing "+" and "-" buttons for adding/deleting individual channels within a specific chart.
* `addchannelframe(self)`: Creates a new `LabelFrame` to hold the channel selection widgets (checkbox, channel dropdown, function dropdown) for a specific chart. Calls `AddChannel` to add the initial channel.
* `AddChannel(self, channelFrames)`:
    * Adds a new `LabelFrame` for a single channel's controls if the current chart has less than 8 channels.
    * Creates and grids a `Checkbutton` (for `ViewVar`), an `OptionMenu` for channel selection (for `OptionVar`), and an `OptionMenu` for function selection (for `FunVar`).
    * Populates the channel options from `self.data.channels` and function options from `self.data.functions.keys()`.
    * Configures the dropdown menus and checkboxes with dark mode styling.
* `ChannelOption(self, frame, ChannelFrameNumber)`: Helper function to create and configure the channel selection `OptionMenu` within a channel's `LabelFrame`.
* `FuncOption(self, frame, ChannelFrameNumber)`: Helper function to create and configure the function selection `OptionMenu` within a channel's `LabelFrame`.
* `deleteChannel(self, channelframe)`: Removes the last added channel's control widgets and its corresponding `IntVar` and `StringVar` entries from `self.ViewVar`, `self.OptionVar`, and `self.FunVar`.

## Data Flow and Structures

The application's data management is highly centralized within the `DataMaster` class, and data flows between the GUI and serial communication modules via instances of `SerialCtrl` and `DataMaster` passed during initialization.

### Conceptual Data Flow Diagram

*(Note: As an AI, I cannot generate visual diagrams directly. The following describes a conceptual diagram you could draw.)*

**Entities:**

* **Serial Device (e.g., Arduino/Sender.py)**: Source of raw data.
* **SerialCtrl**: Manages the physical serial connection.
* **DataMaster**: Processes, stores, and prepares data.
* **ConnGUI**: Controls streaming and triggers GUI updates.
* **DisplayGUI**: Manages and renders charts.
* **RootGUI**: Main application window.
* **ComGUI**: Manages COM port selection.
* **CSV File**: Destination for saved data.

**Flow (Arrows indicate data/control transfer):**

1.  **Initialization:**
    * `master.py` instantiates `RootGUI`, `SerialCtrl`, `DataMaster`, `ComGUI`.
    * `RootGUI` holds references to `SerialCtrl` and `DataMaster`.
    * `ComGUI` holds references to `RootGUI`, `SerialCtrl`, `DataMaster`.

2.  **Connection Phase:**
    * `ComGUI` (User selects port/baud, clicks "Connect") -> `SerialCtrl.serialConnect()` (Opens serial port).
    * If successful, `ComGUI` instantiates `ConnGUI`, passing `RootGUI`, `SerialCtrl`, `DataMaster` references.
    * `ComGUI` spawns **Thread 1 (Synchronization)**: `SerialCtrl.serialSync()`.
        * `SerialCtrl.serialSync()` <-> Serial Device (Sends `"#?#\n"`, receives `"!#<channels>#\n"`).
        * `SerialCtrl.serialSync()` updates `DataMaster.syncChannels`, calls `DataMaster.genChannels()`, `DataMaster.buildData()`.
        * `SerialCtrl.serialSync()` updates `ConnGUI` (sync status, channel count).

3.  **Data Streaming & Processing Phase:**
    * `ConnGUI` (User clicks "Start Stream") -> `SerialCtrl.SerialDataStream()` (spawns **Thread 2: Data Stream Reader**).
    * **Thread 2 (Data Stream Reader)**:
        * Reads `raw_msg` (bytes) from Serial Device.
        * Updates `DataMaster.RowMsg`.
        * Calls `DataMaster.DecodeMsg()` -> `DataMaster.message` (list of strings).
        * Calls `DataMaster.streamDataCheck()` -> Validates message length/format.
        * If valid:
            * Calls `DataMaster.IntMsgFunc()` -> `DataMaster.IntMsg` (list of floats).
            * Calls `DataMaster.SetRefTime()`.
            * Calls `DataMaster.updateX()` -> Appends time to `DataMaster.xData`.
            * Calls `DataMaster.updateY()` -> Appends `DataMaster.IntMsg` to `DataMaster.yData` (per channel).
            * Calls `DataMaster.adjustData()` -> Trims `xData`, `yData` to `DisplayTime` window; prepares `DataMaster.xdisplay`, `DataMaster.ydisplay` (NumPy arrays).
            * If `ConnGUI.save` is True, spawns **Thread 3 (Data Saver)**: `DataMaster.saveData()`.
                * **Thread 3 (Data Saver)**: Writes `DataMaster.IntMsg` and timestamp to CSV File.
            * Schedules GUI update on main thread: `RootGUI.root.after(40, ConnGUI.updateChart)`.

4.  **GUI Update & Rendering Phase (Main Tkinter Thread):**
    * `ConnGUI.updateChart()` (Triggered by `root.after`):
        * Iterates through charts managed by `DisplayGUI`.
        * For each chart and selected channel:
            * Retrieves `xdisplay` and `ydisplay` from `DataMaster`.
            * Dynamically calls selected `DataMaster` processing function (e.g., `RowData`, `Voltage`, `savgo`, `digi_filter`) using `DataMaster.functions` dictionary.
            * The chosen `DataMaster` function plots data on the `DisplayGUI`'s Matplotlib `Axes` (`chart`).
        * Calls `DisplayGUI`'s `canvas.draw()` to refresh the embedded Matplotlib plot.
        * Recursively schedules itself: `RootGUI.root.after(40, ConnGUI.updateChart)`.

5.  **Disconnection/Shutdown:**
    * `ConnGUI` (User clicks "Stop Stream") -> `SerialCtrl.serialStop()`. Sets `SerialCtrl.threading = False`.
    * `ComGUI` (User clicks "Disconnect") -> `SerialCtrl.serialClose()`. Clears `DataMaster` buffers. Destroys `ConnGUI` widgets.
    * `RootGUI` (User closes window) -> `RootGUI.closeWindow()`. Destroys root, closes serial port, sets `SerialCtrl.threading = False`.

### Key Data Structures and Their Contents

*(Imagine a table or a set of boxes for each class, showing its attributes and their typical contents/types.)*

**1. `DataMaster`:**

| Attribute Name    | Type                | Description                                                                 | Example Content                                                 |
| :---------------- | :------------------ | :-------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| `sync`            | `str`               | Command for device synchronization.                                         | `"#?#\n"`                                                       |
| `startStream`     | `str`               | Command to initiate data streaming.                                         | `"#s#\n"`                                                       |
| `stopStream`      | `str`               | Command to halt data streaming.                                             | `"#A#\n"`                                                       |
| `sync_ok`         | `str`               | Expected response for successful sync.                                      | `!`                                                             |
| `syncChannels`    | `int`               | Number of data channels reported by the device.                             | `4`                                                             |
| `xData`           | `list[float]`       | Raw time data points (relative to `RefTime`).                               | `[0.0, 0.05, 0.1, 0.15, ...]`                                   |
| `yData`           | `list[list[float]]` | Raw Y-axis data per channel. `yData[0]` is Ch0, `yData[1]` is Ch1, etc.     | `[[100.1, 105.3, ...], [20.5, 22.1, ...], ...]`                |
| `functions`       | `dict[str, method]` | Maps display function names to their corresponding methods.                 | `{"RowData": self.RowData, "Voltage": self.Voltage, ...}`       |
| `RowMsg`          | `bytes`             | Raw byte string received from serial.                                       | `b'#D#123.45#67.89#5.0#234#'`                                   |
| `message`         | `list[str]`         | Decoded and split message parts.                                            | `['', 'D', '123.45', '67.89', '5.0', '234', '']`                |
| `messageLen`      | `int`               | Expected total length of numerical data in message.                         | `15` (e.g., sum of lengths of "123.45", "67.89", "5.0", "234") |
| `IntMsg`          | `list[float]`       | Decoded and converted numerical data.                                       | `[123.45, 67.89, 5.0, 234.0]`                                   |
| `channels`        | `list[str]`         | Generated names for each channel.                                           | `['Ch0', 'Ch1', 'Ch2', 'Ch3']`                                  |
| `DisplayTime`     | `int`               | Time window for displayed data in seconds.                                  | `5`                                                             |
| `RefTime`         | `float`             | `time.perf_counter()` at stream start.                                      | `12345.6789`                                                    |
| `filename`        | `str`               | Name for the CSV data log file.                                             | `"20250618155107.csv"`                                          |
| `xdisplay`        | `np.ndarray`        | NumPy array of X-data, prepared for plotting after `adjustData()`.        | `array([0.0, 0.05, 0.1, ...])`                                  |
| `ydisplay`        | `np.ndarray`        | NumPy array of Y-data, prepared for plotting after `adjustData()`.        | `array([[100.1, 105.3, ...], ...])`                            |

**2. `SerialCtrl`:**

| Attribute Name | Type              | Description                                        | Example Content         |
| :------------- | :---------------- | :------------------------------------------------- | :---------------------- |
| `comList`      | `list[str]`       | List of available COM ports.                       | `['-', 'COM1', 'COM7']` |
| `ser`          | `serial.Serial`   | PySerial object for communication.                 | `<serial.Serial...>`    |
| `ser.status`   | `bool`            | True if serial port is open, False otherwise.      | `True`                  |
| `sync_cnt`     | `int`             | Counter limit for synchronization attempts.        | `200`                   |
| `threading`    | `bool`            | Global flag to control serial communication threads. | `True`                  |
| `t1`           | `threading.Thread` | Reference to the current active serial thread.     | `<Thread...>`           |

**3. `RootGUI`:**

| Attribute Name | Type          | Description                         | Example Content |
| :------------- | :------------ | :---------------------------------- | :-------------- |
| `root`         | `tkinter.Tk`  | Main Tkinter window.                | `<tkinter.Tk...>` |
| `serial`       | `SerialCtrl`  | Instance of the serial controller.  | `<SerialCtrl...>` |
| `data`         | `DataMaster`  | Instance of the data manager.       | `<DataMaster...>` |

**4. `ConnGUI`:**

| Attribute Name | Type                   | Description                                                | Example Content        |
| :------------- | :--------------------- | :--------------------------------------------------------- | :--------------------- |
| `save`         | `bool`                 | Flag for enabling/disabling data saving.                   | `True`                 |
| `SaveVar`      | `tkinter.IntVar`       | Tkinter variable for "Save Data" checkbox.                 | `1` (checked)          |
| `chartMaster`  | `DisplayGUI`           | Instance of the display/chart manager.                     | `<DisplayGUI...>`      |
| `chart`        | `matplotlib.axes.Axes` | Current Matplotlib axes being plotted on.                  | `<AxesSubplot...>`     |
| `color`        | `str`                  | Current plotting color for the active channel.             | `"#00be95"`            |
| `x`            | `np.ndarray`           | X-data (time) for current plot.                            | `array([0.0, 0.05,...])` |
| `y`            | `np.ndarray`           | Y-data (values) for current plot.                          | `array([100.1, 105.3,...])` |

**5. `DisplayGUI`:**

| Attribute Name    | Type                           | Description                                                            | Example Content                       |
| :---------------- | :----------------------------- | :--------------------------------------------------------------------- | :------------------------------------ |
| `frames`          | `list[tkinter.LabelFrame]`     | List of main frames for each chart.                                    | `[<LabelFrame...>, <LabelFrame...>]`  |
| `figs`            | `list[list[Figure, Axes, Canvas]]` | List of `[Figure, Axes, Canvas]` for each chart.                       | `[[<Figure...>, <Axes...>, <Canvas...>], ...]` |
| `channelFrames`   | `list[list[tkinter.LabelFrame, int]]` | List of `[channel_frame, index]` for channel controls within charts. | `[[<LabelFrame...>, 0], [<LabelFrame...>, 1]]` |
| `ViewVar`         | `list[list[tkinter.IntVar]]`   | Tkinter variables for channel "View" checkboxes per chart.             | `[[1, 0, 1], [1, 1, 0]]` (Chart 1: Ch0, Ch2 visible) |
| `OptionVar`       | `list[list[tkinter.StringVar]]` | Tkinter variables for channel selection dropdowns per chart.           | `[["Ch0", "Ch1"], ["Ch2"]]`           |
| `FunVar`          | `list[list[tkinter.StringVar]]` | Tkinter variables for function selection dropdowns per chart.          | `[["Voltage", "RowData"], ["Savgo Filter"]]` |

## Threading Model

This application uses Python's `threading` module to perform blocking operations (like serial communication) in the background, preventing the Tkinter GUI from freezing. It's crucial to understand that all GUI updates **must** occur on the main Tkinter thread. The `root.after()` method is used to safely schedule GUI updates from background threads.

**Key Threads and Their Responsibilities:**

1.  **Main Tkinter Thread:**
    * **Initiation:** Started by `RootMaster.root.mainloop()` in `master.py`.
    * **Responsibility:**
        * Handles all GUI rendering and user interactions.
        * Processes Tkinter events (button clicks, dropdown selections, window resizing).
        * Executes callbacks scheduled by `root.after()`, including `ConnGUI.updateChart()`.
        * Manages the lifecycle of the entire application.
    * **Control Mechanism:** This is the primary thread. Other threads communicate with it by scheduling tasks via `root.after()`.

2.  **Serial Synchronization Thread (T1):**
    * **Initiation:** Spawned in `ComGUI.serialConnect()` when the "Connect" button is clicked:
        ```python
        self.serial.t1 = threading.Thread(target=self.serial.serialSync, args=(self.conn_menu,), daemon=True)
        self.serial.t1.start()
        ```
    * **Responsibility:**
        * Executes `SerialCtrl.serialSync()`.
        * Continuously sends synchronization commands (`#?#`) to the serial device.
        * Waits for a specific synchronization response (`!#<channels>#`).
        * Updates the `DataMaster` with the number of detected channels (`syncChannels`).
        * Updates the GUI's sync status label via the `conn_gui` object (which is an instance of `ConnGUI`).
    * **Control Mechanism:**
        * `self.serial.threading = True` is set before starting.
        * The loop inside `serialSync` continues until synchronization is successful or an error occurs, at which point `self.serial.threading` is set to `False`. The `daemon=True` ensures the thread terminates with the main application.

3.  **Serial Data Streaming Thread (T1 - Reused):**
    * **Initiation:** Spawned in `ConnGUI.start_stream()` when the "Start Stream" button is clicked. It reuses `t1` from the synchronization phase if that thread has completed, or creates a new one if `t1` is `None` or not alive.
        ```python
        self.serial.t1 = threading.Thread(target=self.serial.SerialDataStream, args=(self,), daemon=True)
        self.serial.t1.start()
        ```
    * **Responsibility:**
        * Executes `SerialCtrl.SerialDataStream()`.
        * Sends the `startStream` command (`#s#`) to the device.
        * Enters a continuous loop to read raw byte messages (`self.ser.readline()`) from the serial port.
        * Passes raw messages to `DataMaster` for decoding, parsing, and data buffering (`DecodeMsg`, `streamDataCheck`, `updateX`, `updateY`, `adjustData`).
        * Crucially, it schedules `ConnGUI.updateChart()` on the main Tkinter thread using `gui.root.after(40, gui.updateChart)` after the first valid data packet is received, and this schedule is self-perpetuating within `updateChart`.
    * **Control Mechanism:**
        * `self.serial.threading = True` is set by `ConnGUI.start_stream()`.
        * The `while self.threading:` loop controls its execution.
        * `ConnGUI.stop_stream()` sets `self.serial.threading = False` to terminate this thread gracefully.

4.  **Data Saving Thread (Dynamic):**
    * **Initiation:** Spawned conditionally *within* the `SerialDataStream` thread if the "Save Data" checkbox (`gui.save`) is checked:
        ```python
        if gui.save:
            t_save = threading.Thread(target=gui.data.saveData, args=(gui,), daemon=True)
            t_save.start()
        ```
    * **Responsibility:**
        * Executes `DataMaster.saveData()`.
        * Appends the current timestamp and received data (`IntMsg`) to the designated CSV file.
    * **Control Mechanism:**
        * This thread is short-lived, starting a new one for each write operation. It performs its task and then terminates.
        * `daemon=True` ensures it doesn't prevent the main application from exiting.

**Thread-Safe Communication:**

* **GUI from Background Threads:** Serial communication and data processing happen in background threads. To update GUI elements (labels, charts), these threads **do not directly modify Tkinter widgets**. Instead, they use `root.after(delay_ms, callback_function)` to schedule a function to run on the main Tkinter thread. This ensures that all GUI operations are performed in a thread-safe manner.
* **Controlling Threads:** A shared boolean flag `self.threading` in `SerialCtrl` is used to signal background threads (synchronization and data streaming) to stop their loops. When `serialClose()` or `stop_stream()` is called, this flag is set to `False`, allowing the background loops to exit cleanly.
* **Data Sharing:** `SerialCtrl` and `DataMaster` instances are passed as arguments to the GUI classes (`RootGUI`, `ComGUI`, `ConnGUI`, `DisplayGUI`). This allows different parts of the application to access and modify the same data objects (like `xData`, `yData`, `RowMsg`) and control flags (`serial.threading`). While this provides access, proper synchronization (e.g., using locks if direct concurrent modification of shared mutable data was involved, though not explicitly shown for `xData`/`yData` in core loops due to the `root.after` pattern) is critical in more complex scenarios. In this design, `DataMaster` updates are primarily driven sequentially within the `SerialDataStream` loop.

## Graphing and Visualization

The graphing capabilities are primarily handled by the `DisplayGUI` class in conjunction with the data processing functions in `DataMaster`. Matplotlib is used for creating the plots, and `FigureCanvasTkAgg` integrates them into the Tkinter GUI.

### Chart Creation

Charts are created dynamically by the `DisplayGUI.addChannelMan()` method, which is invoked when the "Add Chart" button in `ConnGUI` is clicked.

1.  **`AddMasterFrame()`**: A `LabelFrame` is created to serve as a container for each individual chart and its associated controls. This frame is then positioned within the main Tkinter window using a grid layout, allowing for multiple charts to be displayed side-by-side or stacked. The `adjustRoot()` method is called to resize the main window appropriately.
2.  **`AddGraph()`**:
    * A Matplotlib `Figure` and an `Axes` object are created.
    * **Dark Mode Styling**: The `plt.style.use('dark_background')` is applied for a dark theme. Additionally, specific colors for ticks, labels, titles, grid lines, and plot spines are set to match the overall dark GUI aesthetic.
    * The `FigureCanvasTkAgg` bridges Matplotlib and Tkinter, embedding the plot directly into the `LabelFrame` created in the previous step.
    * The `Figure`, `Axes`, and `Canvas` objects are stored in `self.figs` for later access during updates and deletion.
3.  **`addchannelframe()`**: A sub-`LabelFrame` is created within the chart's main frame to house controls for individual data channels (e.g., checkboxes, dropdowns for channel selection and function selection).
4.  **`AddChannel()`**: For each channel within a chart:
    * A small `LabelFrame` is created for the channel's specific controls.
    * A `Checkbutton` is added (`self.ViewVar`) to toggle the visibility of that channel's plot.
    * An `OptionMenu` (`self.OptionVar`) allows the user to select which data channel (e.g., Ch0, Ch1) from the incoming stream should be plotted.
    * Another `OptionMenu` (`self.FunVar`) provides a choice of data processing functions (e.g., "RowData", "Voltage", "Savgo Filter", "Digital Filter") to apply before plotting. These options are dynamically populated from the `DataMaster.functions` dictionary.

### Chart Update Mechanism

The real-time updating of the charts is managed by the `ConnGUI.updateChart()` method, which uses Tkinter's `after` method for continuous, non-blocking updates:

1.  **Initial Scheduling**: Once serial data streaming successfully starts (`SerialCtrl.SerialDataStream`), it calls `gui.root.after(40, gui.updateChart)`. This schedules the first chart update to occur after a 40-millisecond delay on the main Tkinter event loop. This is crucial as all GUI operations must happen on the main thread.
2.  **Iterative Updates**:
    * `ConnGUI.updateChart()` iterates through each active chart managed by `self.chartMaster`.
    * For each chart, it clears the Matplotlib `Axes` (`self.chartMaster.figs[Channel][1].clear()`) to remove the previous plot.
    * It then iterates through each channel control associated with that chart.
    * **Conditional Plotting**: If a channel's `ViewVar` checkbox is selected (`state.get()` is True):
        * It retrieves the selected channel name (`MyChannel`) and the desired processing function name (`funcName`) from the `OptionVar` and `FunVar` dropdowns, respectively.
        * It gets the corresponding data (`self.y`) for the selected channel from `self.data.ydisplay` and the time data (`self.x`) from `self.data.xdisplay`.
        * It sets `self.chart` to the current Matplotlib `Axes` object and `self.color` to the channel's predefined color.
        * **Dynamic Function Call**: The core of the data processing and plotting is `self.data.functions[funcName](self)`. This dynamically calls the chosen method (e.g., `DataMaster.RowData`, `DataMaster.Voltage`, `DataMaster.savgo`, `DataMaster.digi_filter`) from the `DataMaster` instance. The `self` (which is the `ConnGUI` instance) is passed as an argument, allowing these `DataMaster` methods to access the current `chart`, `x`, `y`, and `color` properties directly for plotting on the correct axes.
        * A minimum length is calculated to ensure `x` and `y` arrays have consistent dimensions before plotting.
    * **Grid Display**: After plotting all active channels for a chart, a grid is drawn on the `Axes`.
    * **Redraw Canvas**: Finally, `self.chartMaster.figs[Channel][0].canvas.draw()` is called to refresh the Tkinter canvas, displaying the updated plot.
3.  **Recursive Scheduling**: If `self.serial.threading` is still `True` (meaning the data stream is active), `self.root.after(40, self.updateChart)` is called again. This creates a continuous loop, redrawing the charts approximately every 40 milliseconds (25 frames per second), providing a fluid real-time visualization.

### Chart Deletion

Charts are removed by clicking the "Kill Chart" button in `ConnGUI`, which triggers `ConnGUI.kill_chart()`:

1.  **`kill_chart()`**:
    * It checks if there are any charts currently displayed (`len(self.chartMaster.frames) > 0`).
    * It identifies the last added chart frame and destroys its Tkinter widget (`.destroy()`).
    * It removes the corresponding Matplotlib `Figure`, `Axes`, and `Canvas` objects from `self.chartMaster.figs` using `pop()`.
    * Similarly, it removes the control frames and channel frames associated with the deleted chart from `self.chartMaster.controlFrames` and `self.chartMaster.channelFrames`.
    * The `IntVar` and `StringVar` lists (`ViewVar`, `OptionVar`, `FunVar`) for the deleted chart are also removed.
    * Finally, `self.chartMaster.adjustRoot()` is called to resize the main Tkinter window to fit the remaining charts.

### Data Processing Functions

The `DataMaster` class contains methods that apply various transformations to the `y` data before it's plotted. These methods are dynamically chosen by the user via the "function" dropdown in the GUI.

* **`RowData(self, gui)`**: Plots the raw, unfiltered data as received.
* **`Voltage(self, gui)`**: Converts the raw digital values (assuming a 12-bit ADC range of 0-4095) to an analog voltage, typically with a 3.3V reference. The formula used is $(Y_{raw} / 4096) * 3.3$.
* **`savgo(self, gui)`**: Applies a Savitzky-Golay filter to smooth the data. This filter is particularly useful for preserving the shape of the signal while removing noise. The parameters `len(x)-1` and `2` specify the window length and polynomial order, respectively.
* **`digi_filter(self, gui)`**: Applies an Elliptic digital filter. This is a type of IIR filter known for its steep rolloff characteristics. The `signal.ellip` function designs the filter, and `signal.filtfilt` applies it to the data forward and backward to eliminate phase distortion.

## How to Run (Assuming a `sender.py` for testing)

To run this application, you will need Python installed along with the `pyserial`, `numpy`, and `matplotlib` libraries.

1.  **Install Dependencies:**
    ```bash
    pip install pyserial numpy matplotlib
    ```

2.  **Identify a COM Port:**
    * If you have a physical serial device, connect it and note its COM port.
    * If you want to test without a physical device, you can use a virtual serial port emulator (e.g., `com0com` on Windows, `socat` on Linux/macOS) to create a pair of connected virtual COM ports.
    * **Using `sender.py` for simulation:** The provided `sender.py` script acts as a fake Arduino. You will need to set the `PORT` variable in `sender.py` to an available COM port (e.g., 'COM7'). If you use a virtual COM port pair, set `sender.py` to one end (e.g., 'COM7') and run the `master.py` GUI to connect to the other end (e.g., 'COM8').

3.  **Run the `sender.py` script (for testing):**
    Open a terminal or command prompt and run:
    ```bash
    python sender.py
    ```
    (Make sure the `PORT` variable in `sender.py` is correctly configured to an available COM port on your system.)

4.  **Run the Main GUI Application:**
    Open another terminal or command prompt and run:
    ```bash
    python master.py
    ```

5.  **GUI Interaction:**
    * **Com Manager:**
        * The "Available Port(s)" dropdown should list the COM ports detected on your system. Select the COM port that `sender.py` is connected to (or the other end of your virtual COM port pair).
        * Select a "Bode Rate" (9600 is used by `sender.py`).
        * Click "Connect". You should see a "Connection Status" message.
    * **Connection Manager:**
        * The "Sync Status" will show "Syncing..." and then "Synced!" if successful.
        * The "Active Channels" will display the number of channels (e.g., "4" from `sender.py`).
        * Click "Start" to begin streaming data.
    * **Display Manager:**
        * Click "Add Chart" to add a new plotting area.
        * For each added chart, you can select specific channels (e.g., Ch0, Ch1) and apply different functions (RowData, Voltage, Savgo Filter, Digital Filter) to visualize the data in various ways.
        * Check the boxes next to the channels you want to display.
        * You can add multiple charts and multiple channels per chart.
        * Check "Save Data" to save the incoming data to a CSV file (named by timestamp).
    * Click "Stop" to halt data streaming.
    * Click "Disconnect" in the Com Manager to close the serial connection and hide the Connection Manager.
    * Close the main GUI window to exit the application gracefully.
