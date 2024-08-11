@echo off
:loop
    echo Running script...
    python app.py
	python warp.py
	python sort.py
	python try.py

	
    if ERRORLEVEL 1 (
        echo Script encountered an error. Restarting...
    ) else (
        echo Script completed successfully.
//    )
    timeout /t 5 /nobreak >nul
    
