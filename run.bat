@echo off
REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application using launch.py
python launch.py server

@echo on