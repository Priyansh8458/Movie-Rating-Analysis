@echo off
title CinePulse — Movie Intelligence Platform
echo ========================================================
echo   Launching CinePulse — Movie Intelligence Platform
echo   Backend: Apache Spark 3.5.5 ^| Frontend: Streamlit
echo ========================================================
echo.

set "JAVA_HOME=C:\Program Files\Java\jre1.8.0_202"
set "PATH=%JAVA_HOME%\bin;%PATH%"

python -m streamlit run app.py

pause
