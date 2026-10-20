@echo off
title CineScope — Movie Performance Analytics
echo ========================================================
echo   Launching CineScope — Movie Performance Analytics
echo   Backend: Apache Spark 3.5.5 ^| Frontend: Streamlit
echo ========================================================
echo.

set "JAVA_HOME=C:\Program Files\Java\jre1.8.0_202"
set "PATH=%JAVA_HOME%\bin;%PATH%"

py -3.14 -m streamlit run app.py

pause
