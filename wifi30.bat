@echo off
for /f "tokens=*" %%a in ('powershell -Command "Get-NetAdapter | Where-Object {$_.Name -eq 'Wi-Fi'} | Select-Object -ExpandProperty InterfaceIndex"') do set index=%%a
powershell -Command "Set-NetIPInterface -InterfaceIndex %index% -InterfaceMetric 30"