py -m PyInstaller ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --name "PianoBlox" ^
    main.py
