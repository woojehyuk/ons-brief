---
name: "speckit-constitution"
description: "프로젝트의 원칙과 운영 규칙을 constitution.md에 작성하거나 개정한다. 기능 구현이나 템플릿 편집은 별도 작업이다."
metadata:
  author: "github-spec-kit"
  source: "templates/commands/constitution.md"
---

# constitution — 한국어 실행 지침

실행 환경: `.specify/` 프로젝트 구조와 Bash/Python.

먼저 프로젝트 루트의 [공통 실행 규칙](../../../.specify/docs/workflow-common.md)을 읽는다.
사용자 입력은 `$ARGUMENTS`와 호출 메시지에서 확인한다. 본 작업 전 `hooks.before_constitution`, 본 작업 후 `hooks.after_constitution`을 공통 규칙에 따라 처리한다.

## 범위

이 스킬 자체는 `.specify/memory/constitution.md`만 작성한다. 템플릿과 명령은 실행 시 이 문서를 참조하므로 여기서 동기 수정하지 않는다. 별도로 요청된 구현·리팩터링·배포 의도는 원칙 문구와 분리하여 후속 작업으로 안내한다. 사용자가 연속 작업을 요청했다면 원칙 갱신 후 해당 별도 범위로 이어갈 수 있다.

## 절차

1. `.specify/scripts/bash/resolve-template.sh constitution-template --json`의 `TEMPLATE_CONTENT`를 읽는다. 합성 실패 시 일부 레이어로 진행하지 않는다. 기존 원칙 문서가 있으면 프로젝트별 값·개정 내용을 우선 보존하고 템플릿 구조를 참고한다.
2. `[ALL_CAPS_IDENTIFIER]` 자리표시자 값을 사용자 입력과 기존 저장소 문서에서 확인한다. 원칙 개수는 실제 필요와 사용자 요청에 맞춘다. 템플릿의 예시를 확정 원칙으로 채택하지 않는다.
3. 각 원칙에 간결한 이름, 검증 가능한 규칙, 필요하면 이유를 작성한다. 필수(MUST)와 권고(SHOULD)를 구분한다. 운영 규칙에는 개정 방법·버전 정책·준수 검토를 적되 요청되지 않은 승인 절차를 만들지 않는다.
4. `RATIFICATION_DATE`는 최초 채택일을 유지한다. 알 수 없으면 `TODO(RATIFICATION_DATE): 확인 필요`로 표시한다. `LAST_AMENDED_DATE`는 실제 수정일이며 바뀐 내용이 없으면 날짜·버전을 올리지 않는다.
5. 실제 개정은 의미적 버전을 적용한다: 호환되지 않는 원칙 삭제/재정의는 MAJOR, 원칙 추가·실질적 확장은 MINOR, 의미가 같은 번역·문구·오탈자 수정은 PATCH. 기존 버전이 없으면 초기 버전 선택의 근거를 적는다.
6. 문서 첫머리 HTML 주석으로 변경 영향 보고를 남긴다: 이전→새 버전, 바뀐 원칙, 추가·삭제 섹션, 보류 TODO. 불필요한 예시 주석은 제거한다.
7. 설명 없는 자리표시자, 모호한 규칙, 날짜 형식, 보고서와 본문의 버전 불일치를 검사하고 저장한다. 미정 항목은 확정된 값처럼 꾸미지 않는다.

## 완료 보고

버전과 변경 이유, 바뀐 원칙, 미정 항목, 필요하면 커밋 메시지 제안을 보고한다. 별도 기능 요청이 있었으면 원래 의도와 적절한 다음 스킬을 연결한다.
