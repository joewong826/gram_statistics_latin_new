#pip install pyinstaller
#pyinstaller [opts] yourprogram.py
#-F, –onefile 打包成一个exe文件。
#-D, –onedir 创建一个目录，包含exe文件，但会依赖很多文件（默认选项）。
#-c, –console, –nowindowed 使用控制台，无界面(默认)
#-w, –windowed, –noconsole 使用窗口，无控制台

pyinstaller -F --distpath=bin dic_task.py
pyinstaller -F --distpath=bin tools.py
