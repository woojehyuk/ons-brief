@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
set CF=%~dp0tools\cloudflared.exe
if not exist "%CF%" (
  echo cloudflared.exe 가 없습니다. 다운로드 중...
  if not exist tools mkdir tools
  curl -L -o "%CF%" https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe || (echo 다운로드 실패 & pause & exit /b 1)
)
netstat -ano | findstr /R /C:":8100 .*LISTENING" >nul
if errorlevel 1 (
  echo [1/2] BE 서버 실행 (http://localhost:8100)
  start "ons-brief BE" cmd /k "cd /d %~dp0project\backend && python -m uvicorn main:app --host 127.0.0.1 --port 8100"
  timeout /t 4 /nobreak >nul
) else (
  echo [1/2] BE 서버 이미 실행 중
)
echo [2/2] trycloudflare 임시 주소 발급
echo   - 아래 로그의 https://....trycloudflare.com 주소를 FE "BE 연결" 화면에 입력
echo   - 이 창을 닫으면 터널 종료 · 실행할 때마다 주소 변경
echo   - 외부 접속에는 가린 연락처만 제공
echo.
"%CF%" tunnel --no-autoupdate --url http://localhost:8100
