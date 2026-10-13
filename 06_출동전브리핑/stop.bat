@echo off
chcp 65001 >nul
echo ons-brief 서버 종료 (BE 8100 / FE 5173 / 터널)
for %%P in (8100 5173) do (
  for /f "tokens=5" %%I in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do taskkill /PID %%I /T /F >nul 2>&1
)
taskkill /IM cloudflared.exe /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq ons-brief*" /T /F >nul 2>&1
echo 완료
