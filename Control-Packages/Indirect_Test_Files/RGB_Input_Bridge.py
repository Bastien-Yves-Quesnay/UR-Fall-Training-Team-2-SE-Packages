import serial
from pynput import keyboard

# Match your board's COM port
COM_PORT = 'COM7'  
BAUD_RATE = 115200

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    print(f"Connected to {COM_PORT}. Hold R, G, or B on your keyboard!")
except Exception as e:
    print(f"Could not open {COM_PORT}: {e}")
    exit()

active_keys = set()

def on_press(key):
    try:
        k = key.char.lower()
        if k in ['r', 'g', 'b'] and k not in active_keys:
            active_keys.add(k)
            ser.write(k.upper().encode())  # Sends 'R', 'G', or 'B'
    except AttributeError:
        pass

def on_release(key):
    try:
        k = key.char.lower()
        if k in active_keys:
            active_keys.remove(k)
            ser.write(k.lower().encode())  # Sends 'r', 'g', or 'b'
    except AttributeError:
        pass

# Start keyboard listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()