# PianoBlox

<img width="807" height="441" alt="image" src="https://github.com/user-attachments/assets/350dabfd-a589-4575-bb30-161e85eb6ca8" />

-------

This is a simple program designed for interfacing with video-games and engines that do not support native MIDI input.

PianoBlox functions sort of like a hotkey program, and will relay MIDI data as key presses to the software.

There are plans to make the key configuration something that is easy to switch, edit, and replace at run-time, so that the keys may be re-mapped in order to avoid conflicts in other software.
Currently, the keys that are mapped are designed for Roblox games, and should not interfere with the player or camera when they are actively using a seat, such as that on a piano.



https://github.com/user-attachments/assets/ac6d0c23-29e4-427a-8196-9535b259d655

*piano asset not included*

-------

You can inspect the main files in order to understand the key order and mapping. Middle C (under default mapping values) will be the `L` key on the keyboard.

The difference between this system and the common one is that this allows for the program to tell how long the note has been held down. 
There are some plans to add support for note velocity, pitch bends, and modulation inputs through virtual controller inputs.

-------

Since the 'keyboard' layout for this program is unique, it is unlikely to function with existing Roblox Piano games, unless they provide support for the keyboard layout specified in this software.
