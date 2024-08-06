@echo off
REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the dependencies from the local directory
pip install --no-index --find-links=dependencies -r requirements.txt

@echo on
echo Setup complete. You can now run the application using run.bat
