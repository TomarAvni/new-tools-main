@echo off

start "" /B cmd /C "call C:\Users\prisma\virtualenvs\pzdev\Scripts\activate && python C:\Users\prisma\Desktop\Tools\Tools_Main\main.py"

if %errorlevel% neq 0 pause
