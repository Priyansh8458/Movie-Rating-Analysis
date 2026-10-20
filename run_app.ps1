# CineScope — Movie Performance Analytics PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Launching CineScope — Movie Performance Analytics" -ForegroundColor White
Write-Host "  Backend: Apache Spark 3.5.5 | Frontend: Streamlit" -ForegroundColor Magenta
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$env:JAVA_HOME = "C:\Program Files\Java\jre1.8.0_202"
$env:PATH = "C:\Program Files\Java\jre1.8.0_202\bin;$env:PATH"

py -3.14 -m streamlit run app.py
