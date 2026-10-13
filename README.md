# ons-brief

- 출동 전 원인 브리핑 카드 생성 실습 (SK ONS 교육 Day2)
- 알람 로그 + 장비이력 + 조치이력 연결 → 기지국별 예상 원인 · 근거 · 챙길 자재 카드
- 구성: FE(React + Vite) ↔ BE(FastAPI) · 외부 접속은 trycloudflare 터널

## 폴더 구조

```
06_출동전브리핑/
├─ start.bat · stop.bat · tunnel.bat
├─ docs/README.md         실습 안내 원본
├─ spec/SPEC.md           개발 명세
├─ data/                  원본 데이터 (저장소 미포함)
├─ tools/                 cloudflared.exe (tunnel.bat 최초 실행 시 자동 다운로드, 저장소 미포함)
└─ project/
   ├─ backend/            main.py(API) · build.py(분석) · config.yaml · sample_data.json · tests/
   ├─ frontend/           React + Vite + TypeScript 화면
   └─ output/             빌드 결과 (저장소 미포함)
```

## 준비

1. Python 3.10 이상, Node.js 20 이상 설치
2. Python 라이브러리 설치
   ```
   pip install pandas openpyxl pyyaml pytest fastapi "uvicorn[standard]"
   ```
3. 데이터 파일 6개를 `06_출동전브리핑/data/`에 복사
   - `alarm_log_20261008.csv`, `site_master.xlsx`, `장비이력.xlsx`, `조치이력.xlsx`, `symptom_map.csv`, `material_map.csv`
   - 개인정보(담당자 연락처) 포함 → 저장소 미포함, 별도 전달
   - 데이터가 없거나 읽기 실패 시 → **가상 샘플 데이터**로 자동 표시

## 실행

| 파일 | 하는 일 |
|---|---|
| `start.bat` | BE(포트 8100) + FE(포트 5173) 실행 → 브라우저 자동 열림. 최초 실행 시 `npm install` 자동 |
| `stop.bat` | BE · FE · 터널 종료 |
| `tunnel.bat` | BE 실행 + trycloudflare 임시 주소 발급 (`https://….trycloudflare.com`) |

- 화면 주소: http://localhost:5173
- BE 주소: http://localhost:8100 (기본값)
- 포트 8100 사용 이유: 이 PC에서 8000 포트를 다른 프로그램이 사용 중

### BE 연결 화면 (왼쪽 메뉴 "BE 연결")
1. BE 주소 입력 (내 PC: `http://localhost:8100` · 외부: tunnel.bat 창의 trycloudflare 주소)
2. "연결 테스트" 클릭 → 연결 성공 / 실패 배지 + 응답 시간
3. 성공 시 주소 자동 저장 → 모든 화면이 해당 BE 데이터 사용
4. "데이터 다시 계산": 원본 데이터 수정 후 BE에서 재계산

### API

| 주소 | 내용 |
|---|---|
| `GET /api/health` | 연결 확인 · 데이터 출처(원본/샘플) · 원본 읽기 오류 |
| `GET /api/briefing` | 화면 전체 데이터 |
| `POST /api/build` | 원본 데이터로 재계산 |

### 터널(외부 접속) 주의
- 주소를 아는 누구나 접속 가능 → 외부 접속에는 **가린 연락처만** 전송 (전체 번호는 내 PC 접속일 때만)
- 실행할 때마다 주소 변경 · tunnel.bat 창을 닫으면 종료

### 분석만 실행 (서버 없이)
```
cd 06_출동전브리핑/project/backend
set PYTHONIOENCODING=utf-8
python build.py
```

## 결과물 (`project/output/`)

| 파일 | 내용 |
|---|---|
| `app.json` | FE 화면용 전체 데이터 (BE가 제공) |
| `briefing.json` | 카드 데이터 (연락처 가림) |
| `cards/*.md` | 기지국별 브리핑 카드, `index.md` 목록 |
| `quality_report.md` | 파일 간 미매칭 · 결측 리포트 |

## 테스트

```
cd 06_출동전브리핑/project/backend
python -m pytest tests -q
```

## 설정 변경

- `project/backend/config.yaml`: 기준일, 파일 경로, 분류 기준, 점수 가중치
- 상세 기준: `spec/SPEC.md`

## 주의

- 사내 DRM 적용 파일(파일 앞부분 `SCDSA`)은 Python으로 읽을 수 없음 → DRM 해제 후 사용
- `output/app.json`에는 "번호 보기"용 전체 연락처 포함 → 외부 공유 금지
