import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk

import mido
import serial
import serial.tools.list_ports
import os.path

_serial = serial.Serial()

def openSerialPort(p):
    #open serial port
    global _serial
    _serial = serial.Serial(port=p, baudrate=115200)

    #send ping to device to see if we're actually communicating with STARDRIVER or some random serial device
    _serial.write({0xE6, 0xFF, 0x01, 0x01}) # E6 - start byte, FF - device addr 255/all devices, 01 - length of message (1 byte), 01 - ping control byte


def updateSerialDevices():
    #reset serial devices frame
    global df
    df.grid_forget()
    df = ttk.LabelFrame(main_frame, text='Serial Devices')
    df.grid(column=1, row=0, padx=15, sticky=tk.N)
    _ports = serial.tools.list_ports.comports()
    for port in _ports:
        _pbtn = ttk.Radiobutton(df, text=port.name, variable=port_sel, command=openSerialPort(port.name))
        _pbtn.pack(anchor=tk.NW)

def stop():
    #stop playback
    _playing = False

def playMidi():
    _playing = True
    for msg in _midi.play():
        print(msg)
        # TODO: implement midi play functionality
    _playing = False

def openFile():
    _types = (
        ('MIDI files', '*.mid *.midi'),
        ('All files', '*.*')
    )

    _path = fd.askopenfilename(
        title="Load a song",
        initialdir='.',
        filetypes=_types
    )

    global song_name
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

pf = ttk.Frame(main_frame)
pf.grid(column=0, row=0, sticky=tk.N)

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

root.mainloop()