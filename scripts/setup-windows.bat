:: Setup Environment and Build Executable file
@echo off
cd ..\
md .\release

:: Requirements:
:: 1. python 3.8.10 (with pip) should be installed at folder python3.8.10,
::    please read the project README for details. 
:: 2. Files should be intact

:: 1. Install Packages
.\python3.8.10\Scripts\pip.exe install -r .\requirements.txt
.\python3.8.10\Scripts\pip.exe install pyinstaller

:: 2. Build executable file
.\python3.8.10\Scripts\pyinstaller.exe -i .\icon.ico -w .\BilibiliToolBoxGUI.py
md .\dist\BilibiliToolBoxGUI\data
md .\dist\BilibiliToolBoxGUI\download
xcopy .\data .\dist\BilibiliToolBoxGUI\data /E/H/C/I
xcopy .\download .\dist\BilibiliToolBoxGUI\download /E/H/C/I
copy .\cookie.txt .\dist\BilibiliToolBoxGUI\cookie.txt /y
copy .\api.cfg .\dist\BilibiliToolBoxGUI\api.cfg /y
copy .\python3.8.10\Lib\site-packages\wordcloud\stopwords .\dist\BilibiliToolBoxGUI\wordcloud\stopwords /y

:: 3. Clear Environment
md .\release\BilibiliToolBoxGUI
xcopy .\dist\BilibiliToolBoxGUI .\release\BilibiliToolBoxGUI /E/H/C/I
rmdir /s/q .\dist
rmdir /s/q .\build
rmdir /s/q .\__pycache__
del .\BilibiliToolBoxGUI.spec
Echo "---------------------finished-----------------------"
