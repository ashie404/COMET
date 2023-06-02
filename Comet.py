import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk

import mido
import serial
import serial.tools.list_ports
import os.path
import threading

_serial = serial.Serial()
max_dev_addr = 0

waiting_serial = False

def openSerialPort(p):
    #open serial port
    global _serial
    global max_dev_addr
    global current_device
    global waiting_serial
    _serial = serial.Serial(port=p,baudrate=115200,parity=serial.PARITY_ODD,timeout=2)

    #send ping to device to see if we're actually communicating with STARDRIVER or some random serial device
    _serial.write([0xE6, 0xFF, 0x01, 0x01]) # E6 - start byte, FF - device addr 255/all devices, 01 - length of message (1 byte), 01 - ping control byte
    print('Ping sent, waiting for device pong...')
    # wait to recieve pong message
    waiting_serial = True
    msg_pos = 0
    while waiting_serial:
        if _serial.readable:
            if msg_pos == 0:
                if _serial.read() == b'\xe6': #if start byte, advance msg pos, if not, cancel handshake.
                    msg_pos = 1
                else:
                    print('Invalid start byte, handshake cancelled.')
                    waiting_serial = False
            elif msg_pos == 1:
                _serial.read() # 2nd byte doesn't really matter, this is device address, still gotta read it tho
                msg_pos = 2
            elif msg_pos == 2:
                # 3rd byte is message size. this should always be 0x02 for a pong message. if not, cancel handshake.
                if _serial.read() == b'\x02':
                    msg_pos = 3
                else:
                    print('Invalid message size, handshake cancelled.')
                    waiting_serial = False
            elif msg_pos == 3:
                # 4th byte is the pong control byte, which is also always 0x02. 5th byte gives us the max device address for the connected board
                if _serial.read() == b'\x02':
                    print('Pong recieved!')
                    # successfully connected to a stardriver device
                    max_dev_addr = _serial.read()
                    current_device.config(text='Current device: ' + p + ', Max inst addr: ' + str(int.from_bytes(max_dev_addr, 'little')))
                    # send reset to ensure all instruments are in a resting state
                    _serial.write([0xE6, 0xFF, 0x01, 0xFF])
                    waiting_serial = False #handshake complete
                else:
                    print('Invalid control byte, handshake cancelled.')
                    waiting_serial = False #cancel handshake, message was not a pong message
                    

def updateSerialDevices():
    #reset serial devices frame
    global df
    df.grid_forget()
    df = ttk.LabelFrame(main_frame, text='Serial Devices')
    df.grid(column=1, row=0, padx=15, sticky=tk.N)
    _ports = serial.tools.list_ports.comports()
    for port in _ports:
        _pbtn = ttk.Radiobutton(df, text=port.name, variable=port_sel, command=lambda: openSerialPort(port.name))
        _pbtn.pack(anchor=tk.NW)

def stop():
    #stop playback
    global _playing
    global play_btn
    _playing = False
    play_btn.config(image=_playimg)

def playMidi():
    global _playing
    global play_btn
    _playing = True
    play_btn.config(image=_pauseimg)
    player = threading.Thread(target=midiLoop)
    player.start()
    _playing = False
    play_btn.config(image=_playimg)

def midiLoop():
    global _midi
    global _playing
    for msg in _midi.play():
        if not _playing: # if player state has changed, exit midi playing loop
            break
        print(msg)
        # TODO: implement midi playing functionality

def openFile():
    global song_name
    global _midi
    _types = (
        ('MIDI files', '*.mid *.midi'),
        ('All files', '*.*')
    )

    _path = fd.askopenfilename(
        title="Load a song",
        initialdir='.',
        filetypes=_types
    )

    song_name.config(text=os.path.basename(_path))
    _midi = mido.MidiFile(_path)

# init tk root/window root
root = Tk()
root.title("COMET")

# init empty midi object
_midi = mido.MidiFile()
_playing = False

# init selected port
port_sel = tk.StringVar()

main_frame = ttk.Frame(root)
main_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)

pf = ttk.LabelFrame(main_frame,text='Player')
pf.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NW)

# setup player section
song_name = Label(pf, text='No song loaded')
song_name.grid(column=0, row=0, sticky=tk.W)

seek_time = Label(pf, text='0:00 / 0:00')
seek_time.grid(column=0, row=1, sticky=tk.W)

playback_ctrl = ttk.Frame(pf)
playback_ctrl.grid(column=1, row=0)

_openimg = PhotoImage(file='./res/open.png')
open_btn = ttk.Button(playback_ctrl, image=_openimg, command=openFile)
open_btn.grid(column=0, row=0)

_playimg = PhotoImage(file='./res/play.png')
_pauseimg = PhotoImage(file='./res/pause.png')
_stopimg = PhotoImage(file='./res/stop.png')
play_btn = ttk.Button(playback_ctrl, image=_playimg, command=playMidi)
play_btn.grid(column=1, row=0, sticky=tk.W)
stop_btn = ttk.Button(playback_ctrl, image=_stopimg, command=stop)
stop_btn.grid(column=2, row=0, sticky=tk.W)

# NYI
#seek_slider = ttk.Scale(pf,from_=0,to=100)
#seek_slider.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky=tk.W)

# setup serial devices section
df = ttk.LabelFrame(main_frame, text='Serial Devices')

updateSerialDevices()

current_device = Label(main_frame, text="Current device: None, Max inst. addr: N/A")
current_device.grid(column=0, row=1, padx=5, pady=5, sticky=tk.SW)

root.mainloop()