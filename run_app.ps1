# CinePulse — Movie Intelligence Platform PowerShell Launcher
Write-Host "========================================================" -ForegroundColor DarkYellow
Write-Host "  Launching CinePulse — Movie Intelligence Platform" -ForegroundColor White
Write-Host "  Backend: Apache Spark 3.5.5 | Frontend: Streamlit" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor DarkYellow
Write-Host ""

$env:JAVA_HOME = "C:\Program Files\Java\jre1.8.0_202"
$env:PATH = "C:\Program Files\Java\jre1.8.0_202\bin;$env:PATH"

python -m streamlit run app.py
