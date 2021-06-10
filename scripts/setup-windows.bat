:: Setup Environment and Build Executable file
@echo off
cd ..\
md .\release

:: Requirements:
:: 1. python 3.8.10(with pip) should be installed at folder python3.8.10
:: 2. Files should be intact

:: 1. Install Packages
.\python3.8.10\Scripts\pip.exe install -r .\requirements.txt
.\python3.8.10\Scripts\pip.exe install pyinstaller

:: 2. Build executable file
.\python3.8.10\Scripts\pyinstaller.exe -i .\icon.ico -w .\BilibiliToolBoxGUI.py
md .\dist\BilibiliToolBoxGUI\data
md .\dist\BilibiliToolBoxGUI\download
copy .\data .\dist\BilibiliToolBoxGUI\data
copy .\download .\dist\BilibiliToolBoxGUI\download
copy .\cookie.txt .\dist\BilibiliToolBoxGUI\cookie.txt
copy .\api.cfg .\dist\BilibiliToolBoxGUI\api.cfg

:: 3. Clear Environment
md .\release\BilibiliToolBoxGUI
copy .\dist\BilibiliToolBoxGUI .\release\BilibiliToolBoxGUI
del .\dist
del .\build
del .\BilibiliToolBoxGUI.spec
Echo "---------------------finished-----------------------"
