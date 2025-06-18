import serial
import time
import math
import threading
import random

# Configuration
PORT = 'COM7'
BAUD = 9600
NUM_CHANNELS = 4
SEND_INTERVAL = 0.05  # seconds

# Open serial connection
ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"[Fake Arduino] Connected on {PORT} at {BAUD} baud")

# Global flag to control streaming
sending_data = threading.Event()  # better than bool for thread-safe signaling

def generate_data(t):
    """Generate synthetic telemetry data."""
    data = []
    for i in range(NUM_CHANNELS):
        val = math.sin(t + i) * 50 + 100 + random.uniform(-2, 2)
        data.append(f"{val:.2f}")
    return data

def sender():
    """Continuously send data packets when streaming is enabled."""
    t = 0.0
    while True:
        if sending_data.is_set():
            data = generate_data(t)
            data_str = "#".join(data)
            length = sum(len(item) for item in data)  # total length of all float strings
            packet = f"#D#{data_str}#{length}#\n"
            try:
                ser.write(packet.encode())
                print(f"[Sent] {packet.strip()}")
            except Exception as e:
                print(f"[Write Error] {e}")
            t += SEND_INTERVAL
            time.sleep(SEND_INTERVAL)
        else:
            time.sleep(0.1)

# Launch sender thread
threading.Thread(target=sender, daemon=True).start()

# Command listener loop
while True:
    try:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            continue

        print(f"[Received] {line}")

        if line == "#?#":
            response = f"#!#{NUM_CHANNELS}#\n"
            ser.write(response.encode())
            print(f"[Info] Sent sync_ok: {response.strip()}")

        elif line == "#s#":
            sending_data.set()
            print("[Info] Data stream started.")

        elif line == "#A#":
            sending_data.clear()
            print("[Info] Data stream stopped.")

        else:
            print(f"[Warning] Unknown command: {line}")

    except Exception as e:
        print(f"[Error] {e}")
        break
