---
version: alpha
name: SK ONS Network Operation UI
description: SK오앤에스 사내 업무 도구(네트워크 운영·장비 관리·작업 일정·대시보드)용 디자인 시스템
colors:
  primary: "#E0002A"
  primary-hover: "#C20024"
  primary-active: "#A8001F"
  primary-soft: "#FDECEF"
  topbar: "#F9D5DB"
  topbar-text: "#5C0A18"
  topbar-border: "#F2B8C2"
  ink: "#0A0A0B"
  text: "#374151"
  text-muted: "#6B7280"
  border: "#E5E7EB"
  surface: "#FFFFFF"
  background: "#F9FAFB"
  success: "#047857"
  success-soft: "#ECFDF5"
  warning: "#B45309"
  warning-soft: "#FFFBEB"
  error: "#B91C1C"
  error-soft: "#FEF2F2"
typography:
  display:
    fontFamily: Pretendard
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: -0.02em
  h1:
    fontFamily: Pretendard
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: -0.01em
  h2:
    fontFamily: Pretendard
    fontSize: 18px
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: Pretendard
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
  body-sm:
    fontFamily: Pretendard
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: Pretendard
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1.4
  number:
    fontFamily: Pretendard
    fontSize: 15px
    fontWeight: 500
    lineHeight: 1.4
    fontFeature: '"tnum" 1'
spacing: { xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, 2xl: 48px, gutter: 24px, max-width: 1200px, rail: 80px }
rounded: { sm: 6px, md: 8px, lg: 12px, full: 9999px }
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    height: 40px
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    borderColor: "{colors.border}"
    rounded: "{rounded.md}"
  input:
    height: 40px
    borderColor: "{colors.border}"
    focusColor: "{colors.primary}"
    rounded: "{rounded.md}"
  card:
    backgroundColor: "{colors.surface}"
    borderColor: "{colors.border}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  badge:
    rounded: "{rounded.full}"
    typography: "{typography.label}"
  top-bar:
    height: 56px
    backgroundColor: "{colors.topbar}"
    textColor: "{colors.topbar-text}"
    borderColor: "{colors.topbar-border}"
  nav-rail:
    width: "{spacing.rail}"
    backgroundColor: "{colors.surface}"
    activeColor: "{colors.primary}"
    activeIndicator: "{colors.primary-soft}"
---

# SK ONS Design System

## Overview

SK오앤에스는 SK 계열의 네트워크 구축·운영(O&M) 전문 기업입니다.
이 디자인 시스템은 고객 홍보용이 아니라 **사내 업무 도구**(계산기, 장비 관리, 견적, 예약, 대시보드)에 씁니다.

- **성격:** 신뢰, 정밀, 절제. 화려함보다 판독성이 우선입니다.
- **사용자:** 네트워크 운영 엔지니어와 현장·관리 직원. 하루 종일 표와 숫자를 봅니다.
- **느낌:** 흰 바탕, 넓은 여백, 파스텔 빨강 상단 바 + 하나의 SK 레드 강조. 운영 보고서처럼 정돈된 화면.

## Colors

브랜드 색은 SK 그룹 레드 계열을 기준으로 정했습니다(공식 CI 값은 사내 가이드로 최종 확인 필요).

- **Primary (#E0002A) — SK Red:** 주요 버튼, 링크, 선택된 탭, 포커스 테두리에만 씁니다. 흰 바탕 대비 약 4.9:1입니다.
- **Top bar (#F9D5DB) — 파스텔 레드:** 상단 바 배경 전용. 글자는 `topbar-text`(#5C0A18), 아래 1px `topbar-border`.
- **Ink (#0A0A0B):** 제목과 핵심 숫자. 순수한 검정(#000) 대신 씁니다.
- **Text / Text-muted:** 본문은 `text`, 보조 설명·단위·캡션은 `text-muted`.
- **Background (#F9FAFB) / Surface (#FFFFFF):** 페이지는 연회색, 카드와 표는 흰색으로 층을 구분합니다.
- **상태 색 (판정 전용):** 아래 의미 외에는 쓰지 않습니다. 진한 색은 글자, `-soft`는 배지 배경입니다.

| 의미 | 글자 | 배경 | 시험 업무 용어 |
| --- | --- | --- | --- |
| 정상 | `success` | `success-soft` | 정상, 복구 완료, 작업 완료 |
| 주의 | `warning` | `warning-soft` | 점검 임박, 지연, 검토 중 |
| 위험 | `error` | `error-soft` | 장애, 만료, 오류 |

- 위험(`error`)은 브랜드 레드와 헷갈리지 않도록 **항상 배지 + 글자**로만 표시합니다.

## Typography

- **글꼴:** Pretendard 하나만 씁니다. CDN:
  `https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css`
- **제목:** `h1`은 페이지당 하나. 화면 제목은 짧은 명사형("장비 점검 현황").
- **숫자:** 측정값·금액·날짜는 `number` 스타일(`font-variant-numeric: tabular-nums`)로 자릿수를 맞추고 표에서 **오른쪽 정렬**합니다.
- **단위:** 숫자와 단위 사이에 한 칸 띄웁니다(`-75 dBm`, `1,200,000 원`). 단위는 `text-muted`로 약하게.
- **날짜:** `YYYY-MM-DD` 하나로 통일합니다.

## Layout

- 최대 폭 1200px, 가운데 정렬, 좌우 여백 24px(모바일 16px). 간격은 4px 배수만 씁니다.
- **단일 화면:** 파스텔 레드 상단 바(높이 56px, 로고 텍스트 "SK ONS" + 화면 제목) → 요약 카드 줄 → 본문(표 또는 폼).
- **화면이 2개 이상(라우팅 필요):** 상단 바는 유지(로고·화면 제목만)하고, 메뉴는 **왼쪽 Navigation Rail**을 씁니다(Components 참고). 본문은 Rail 오른쪽에 같은 규칙으로 배치합니다.
- 폼은 한 열이 기본, 넓은 화면에서만 2열. 768px 이하에서는 모든 그리드를 한 열(`minmax(0, 1fr)`)로 접고, 표는 가로 스크롤 컨테이너에 넣습니다.

## Elevation & Shapes

- 층 구분은 **1px `border` 테두리**와 배경색 차이로 합니다. 그림자는 모달·드롭다운에만 `0 4px 16px rgba(0,0,0,0.08)`.
- 모서리: 버튼·입력창 `md`(8px), 카드 `lg`(12px), 배지 `full`.

## Motion

움직임은 **상태가 바뀌었음을 알려 줄 때만** 씁니다. 장식용 애니메이션은 쓰지 않습니다.

| 토큰 | 값 | 용도 |
| --- | --- | --- |
| `--motion-fast` | 120ms | hover, 누름, 포커스 |
| `--motion-base` | 200ms | 탭 전환, 패널 열림, 배지·행 추가/삭제 |
| `--motion-slow` | 600ms | 그래프, 진행도, 숫자 카운트업 |
| `--ease` | `cubic-bezier(0.2, 0, 0, 1)` | 모든 전환 공통 |

- **사용자 인터랙션:** 버튼 hover 시 배경색 전환, 누를 때 `scale(0.98)`. 오류 문구·새 항목은 페이드인 + 위로 4px, 삭제는 페이드아웃. Rail 활성 표시는 `base`로 이동.
- **그래프:** 처음 보일 때 막대·선이 0에서 값까지 자랍니다(`slow`, 막대마다 40ms 지연). 핵심 숫자는 0부터 카운트업.
- **진행도:** 진행 바·단계 점·남은 일수 바는 0에서 현재 값까지 채워집니다(`slow`). 상태가 바뀌면 배지 색을 `base`로 전환.
- `transform`, `opacity`, 색만 애니메이션합니다(레이아웃이 흔들리지 않게).
- `@media (prefers-reduced-motion: reduce)`에서는 모든 애니메이션을 끄고 최종 상태만 보여 줍니다.

## Components

### Top Bar (모든 화면)
- 화면 맨 위 전체 폭, 높이 56px, `topbar` 배경 + 아래 `topbar-border` 1px.
- 왼쪽 로고 텍스트 "SK ONS"(`h2`, `topbar-text`) + 구분선 + 화면 제목. 오른쪽에 사용자명 등 보조 정보(`body-sm`).
- 메뉴 항목은 넣지 않습니다. 그림자·그라데이션 없이 단색.

### Navigation Rail (라우팅이 있을 때만)
- 상단 바 아래 남은 높이, 폭 80px, `surface` 배경 + 오른쪽 `border`.
- 항목은 세로로 쌓고, 각 항목은 24px 선 아이콘(SVG) 위 + 12px 라벨 아래. 항목은 3~7개.
- 활성 항목: 아이콘 뒤에 `primary-soft` 알약(56×32px) + `primary` 색 아이콘·라벨. 나머지는 `text-muted`.
- 768px 이하에서는 같은 항목을 화면 아래 탭 바(높이 64px)로 바꿉니다.

### Button
- **Primary:** SK 레드 배경 + 흰 글자. 화면당 하나(저장, 계산, 생성).
- **Secondary:** 흰 배경 + 회색 테두리(취소, 초기화, 내보내기). **Danger:** 삭제 확정에만, 흰 배경 + `error` 글자.
- 높이 40px, 좌우 패딩 16px, hover 시 `primary-hover`.

### Input
- 라벨은 입력창 **위**에 `label` 스타일로. placeholder를 라벨 대신 쓰지 않습니다. 단위는 입력창 오른쪽 안에.
- 포커스: `primary` 2px 테두리. 오류: `error` 테두리 + 아래에 한 줄 안내 문구.

### Card (요약 지표)
- 흰 배경, 테두리, 패딩 24px. 작은 라벨(`text-muted`) → 큰 숫자(`display`, `ink`) → 보조 설명.

### Table
- 헤더: `background` 배경, `label` 스타일, 아래 테두리. 행 높이 44px 이상, 가로 테두리만(세로선 없음).
- 숫자 열은 오른쪽, 텍스트 열은 왼쪽 정렬. 행 hover 시 `background` 색. 정렬 가능한 열에는 화살표.
- 데이터가 없으면 표 대신 빈 상태 문구("등록된 장비가 없습니다")를 보여 줍니다.

### Badge (상태 표시)
- 둥근 알약, `-soft` 배경 + 진한 글자 + 앞에 6px 점. 색만으로 구분하지 않고 **항상 글자**("정상", "장애")를 함께 씁니다.

## Do's and Don'ts

**Do**
- 색은 frontmatter 토큰만 씁니다. CSS 변수(`--color-primary` 등)로 정의해 재사용하세요.
- 숫자에는 천 단위 쉼표와 단위를 붙이고, 모든 입력값은 검증해 입력창 바로 아래에 알려 줍니다.
- 실습 데이터는 가상 데이터만 씁니다(가상 국사 "가나국사", 가상 장비 "RU-0001" 등). 버튼·링크는 키보드로 이동되고 포커스가 보여야 합니다.

**Don't**
- 그라데이션, 네온, 유리 효과, 큰 그림자를 쓰지 않습니다.
- 이모지를 아이콘 대신 쓰지 않습니다. 아이콘이 필요하면 단순한 선 아이콘(SVG)만.
- 진한 SK 레드를 넓은 배경 면적에 칠하지 않습니다(넓은 면은 파스텔 `topbar`만). 초록·`error` 빨강은 판정 외의 장식으로 쓰지 않습니다.
- 한 화면에 Primary 버튼을 두 개 이상 두지 않고, 본문에 대비 4.5:1 미만의 연한 글자를 쓰지 않습니다.
- 무한 반복·바운스 애니메이션, 600ms를 넘는 애니메이션을 쓰지 않습니다.
- 상단 바에 가로 메뉴나 햄버거 메뉴를 넣지 않습니다(라우팅은 Rail 사용).
