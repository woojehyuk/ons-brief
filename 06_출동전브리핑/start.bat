@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo [1/3] BE 서버 실행 (http://localhost:8100)
start "ons-brief BE" cmd /k "cd /d %~dp0project\backend && python -m uvicorn main:app --host 127.0.0.1 --port 8100"
echo [2/3] FE 서버 실행 (http://localhost:5173)
if not exist "project\frontend\node_modules" (
  echo   - 최초 실행: 라이브러리 설치 중...
  pushd project\frontend && call npm install && popd
)
start "ons-brief FE" cmd /k "cd /d %~dp0project\frontend && npm run dev"
echo [3/3] 브라우저 열기
timeout /t 4 /nobreak >nul
start "" http://localhost:5173
echo 완료. 종료는 stop.bat 실행
