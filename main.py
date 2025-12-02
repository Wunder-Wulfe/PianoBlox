import pyautogui
import rtmidi
import tkinter as tk
from tkinter import ttk
import asyncio
import multiprocessing as mp
from wrappedtuple import WrappedTuple
import sys
import os


"""
    Keyboard layout pattern established for translating MIDI events into virtual key presses
    
    'left', 'right', 'up', and 'down' represent the Arrow keys
    '0' - '9' are the numeric keys
    'num0' - 'num9', 'add', 'subtract', 'multiply', 'decimal', and 'divide' are keys found on the numpad
    
    An equivalent layout for Luau tables (can copy and paste):
    
        local KC = Enum.KeyCode
        
        local KEY_PATTERN: {Enum.KeyCode} = table.freeze {
            KC.Up, KC.Down, 
            KC.Zero, KC.One, KC.Two, KC.Three, KC.Four, 
            KC.Five, KC.Six, KC.Seven, KC.Eight, KC.Nine, 
            KC.Q, KC.W, KC.E, KC.R,
            KC.T, KC.Y, KC.U, KC.P, KC.A,
            KC.S, KC.D, KC.F, KC.G, KC.H,
            KC.J, KC.K, KC.L, KC.Z, KC.X,
            KC.C, KC.V, KC.B, KC.N, KC.M,
            KC.KeypadZero, KC.KeypadOne, KC.KeypadTwo, KC.KeypadThree, KC.KeypadFour, 
            KC.KeypadFive, KC.KeypadSix, KC.KeypadSeven, KC.KeypadEight, KC.KeypadNine,
            KC.KeypadPlus, KC.KeypadMinus, KC.KeypadMultiply, 
            KC.KeypadDivide, KC.Comma, KC.KeypadPeriod, KC.Semicolon, 
            KC.Quote, KC.LeftBracket, KC.RightBracket, 
            KC.Minus, KC.Equals
        }
"""
KEY_PATTERN = (
    'up', 'down', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'q', 'w', 'e', 'r', 't', 'y', 'u', 'p',
    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
    'z', 'x', 'c', 'v', 'b', 'n', 'm',
    'num0', 'num1', 'num2', 'num3', 'num4', 'num5',
    'num6', 'num7', 'num8', 'num9',
    'add', 'subtract', 'multiply', 'divide',
    ',', 'decimal', ';', '\'', '[', ']', '-', '='
)

# Calibration key is required in order to assign the 'Middle C' note
# This value is 0 index based
# In Roblox, make sure that your calibration value is aligned!!!
KEY_CALIBRATION = 28

# SHARP♯
# FLAT♭
NOTE_NAMES = WrappedTuple(
    (
        'C', 'C♯/D♭', 'D', 'D♯/E♭', 'E',
        'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B'
    )
)

def get_note_name(note: int) -> str:
    return f"{NOTE_NAMES[note]} {note // 12}"

NOTE_ON = 144
NOTE_OFF = 128

pyautogui.PAUSE = 0


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS # exists when using PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(default=resource_path("icon.ico"))
        self.title('Piano Blox')
        self.geometry('800x400')
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.init_frame = tk.Frame(self)
        self.init_frame.grid(column=0, row=0, columnspan=3)
        self.midi_input = ttk.Combobox(self.init_frame, values=[], state='readonly')
        self.midi_input.grid(row=0, column=0)
        self.refresh = ttk.Button(self.init_frame, text='Refresh', command=self.on_refresh)
        self.refresh.grid(row=0, column=1)
        self.midi_handler = rtmidi.MidiIn()
        self.midi_handler.set_callback(self.on_event)

        self.octave_main_panel = ttk.Frame(self)
        self.octave_main_panel.grid(column=0, row=1, columnspan=3)
        self.octave = tk.IntVar(value=4)
        self.octave_label = tk.Label(self.octave_main_panel, text='Octave: 4')
        self.octave_label.grid(row=0, column=0)

        self.octave_up = ttk.Button(self.octave_main_panel, text='+', command=lambda: self.inc_octave(1))
        self.octave_up.grid(row=0, column=1)
        self.octave_down = ttk.Button(self.octave_main_panel, text='-', command=lambda: self.inc_octave(-1))
        self.octave_down.grid(row=0, column=2)

        self.kp_frame = ttk.Frame(self)
        self.kp_frame.grid(column=0, row=2, columnspan=3)
        self.enable_presses_label = ttk.Label(self.kp_frame, text='Enable Keyboard Presses')
        self.enable_presses_label.grid(row=0, column=0)
        self.keyboard_enabled = tk.BooleanVar(value=False)
        self.enable_presses = ttk.Checkbutton(self.kp_frame, variable=self.keyboard_enabled, command=self.on_toggle_keys)
        self.enable_presses.grid(row=0, column=1)

        self.show_keys = ttk.Label(self, text='Keys Pressed')
        self.show_keys.grid(row=3, column=0, columnspan=3)
        self.keys_list = ttk.Label(self, text='')
        self.keys_list.grid(row=4, column=0, columnspan=3)
        self.note_list = ttk.Label(self, text='')
        self.note_list.grid(row=5, column=0, columnspan=3)

        self.keys = ttk.Frame(self)
        self.keys.grid(row=6, column=0, columnspan=3)

        self.pressed = set()
        self.notes = set()

        self.on_refresh()

    def set_octave(self, octave:int):
        self.octave.set(max(min(octave, 8), -2))
        self.update_text()

    def inc_octave(self, value:int):
        self.set_octave(self.octave.get() + value)

    def on_refresh(self):
        self.on_toggle_keys()

        self.midi_input['values'] = self.midi_handler.get_ports()
        self.midi_input.current(0)
        self.on_select()

    def on_select(self):
        self.on_toggle_keys()

        self.midi_handler.close_port()
        self.midi_handler.open_port(self.midi_input.current())
        self.midi_handler.set_callback(self.on_event)

    def on_toggle_keys(self):
        self.clear_presses()
        self.update_text()

    def update_text(self):
        self.keys_list.config(text=' | '.join(k.upper() for k in self.pressed))
        self.note_list.config(text=' | '.join(get_note_name(k) for k in sorted(self.notes)))
        self.octave_label.config(text=f'Octave: {self.octave.get()}')

    def handle_note(self, note:int, velo:int, on:bool):
        if on:
            self.notes.add(note)
        else:
            self.notes.discard(note)

        if self.keyboard_enabled.get():
            index = KEY_CALIBRATION + note + (self.octave.get() - 8) * 12

            if 0 <= index < len(KEY_PATTERN):
                key = KEY_PATTERN[index]

                if on:
                    self.pressed.add(key)
                    pyautogui.keyDown(key)
                else:
                    self.pressed.discard(key)
                    pyautogui.keyUp(key)

        self.update_text()

    def clear_presses(self):
        for key in self.pressed:
            pyautogui.keyUp(key)
        self.pressed.clear()
        self.notes.clear()

    def on_event(self, event, data=None):
        msg, dt = event

        if len(msg) != 3:
            return

        status, note, velo = msg

        if status == NOTE_ON or status == NOTE_OFF:
            self.handle_note(note, velo, status == NOTE_ON)

    def __del__(self):
        self.clear_presses()
        del self.midi_handler

    def update_idletasks(self):
        super().update_idletasks()


def run_app():
    app = App()
    app.mainloop()


PROCESSES = set()


async def to_thread(f, *args):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, f, *args)


def start_parallel(f, *args, **kwargs):
    global PROCESSES

    p = mp.Process(target=f, args=args, kwargs=kwargs)

    PROCESSES.add(to_thread(p.join))

    p.start()


async def end_parallel():
    global PROCESSES

    while len(PROCESSES) > 0:
        done, unfinished = await asyncio.wait(PROCESSES, return_when=asyncio.FIRST_COMPLETED)
        PROCESSES -= set(x.get_coro() for x in done)


async def main():
    with mp.Manager() as manager:
        start_parallel(run_app)
        await end_parallel()


if __name__ == '__main__':
    mp.freeze_support()
    asyncio.run(main())
