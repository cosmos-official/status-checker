# Server Status Checker

GitHub Actions를 기반으로 한 서버 상태 모니터링 및 Slack 알림 시스템입니다.

## 기능 목록

### ✅ 기본 모니터링 기능
- [ ] 설정된 서버 목록에 대한 주기적 핑 테스트
- [ ] 서버 응답 시간 측정 및 기록
- [ ] 서버 다운타임 감지 및 기록
- [ ] 서버 상태 이력 관리

### ✅ 알림 시스템
- [ ] Slack 웹훅을 통한 실시간 알림
- [ ] 서버 다운타임 발생 시 즉시 알림
- [ ] 서버 복구 시 알림
- [ ] 정기 상태 리포트 (일/주/월 단위)

### ✅ 데이터 관리
- [ ] 서버 상태 데이터 JSON 형태로 저장
- [ ] GitHub 저장소 내 JSON 파일로 다운타임 이력 관리
- [ ] 서버별 응답 시간 통계 기록
- [ ] 데이터 백업 및 복구
- [ ] 상태 변화 시에만 커밋 기록 (UP → DOWN, DOWN → UP)
    - Sparse matrix 방식의 효율적인 상태 이력 관리

### ✅ 설정 관리
- [x] 서버 목록 설정 파일 (servers.json)
- [ ] 모니터링 주기 설정
- [ ] Slack 웹훅 URL 설정
- [ ] 알림 조건 설정 (응답 시간 임계값 등)

### ✅ GitHub Actions 워크플로우
- [ ] 주기적 실행 스케줄링 (cron)
- [ ] 서버 상태 체크 스크립트 실행
- [ ] 결과 데이터 저장 및 커밋
- [ ] Slack 알림 트리거

### ✅ 모니터링 대상
- [ ] HTTP/HTTPS 엔드포인트 상태 체크
- [ ] 커스텀 헬스체크 엔드포인트

### ✅ 알림 메시지
- [ ] 서버 다운타임 알림
- [ ] 서버 복구 알림
- [ ] 정기 상태 리포트
- [ ] 응답 시간 임계값 초과 알림

### ✅ 대시보드 및 리포트
- [ ] 서버 상태 대시보드 (GitHub Pages)
- [ ] 다운타임 통계 리포트
- [ ] 응답 시간 트렌드 차트

## 프로젝트 구조

```
status-checker-1/
├── .github/
│   └── workflows/
│       └── server-monitor.yml
├── scripts/
│   ├── check-servers.py
│   ├── send-slack-notification.py
│   ├── generate-report.py
│   └── update-dashboard.py
├── data/
│   ├── servers.json              # 모니터링할 서버 목록
│   ├── current-status.json       # 현재 서버 상태 (최신)
│   ├── status-changes.json       # 상태 변화 이력 (최근 30일)
│   ├── weekly-reports/           # 주간 리포트 저장소
│   │   ├── 2024-W01.json
│   │   ├── 2024-W02.json
│   │   └── ...
│   ├── monthly-reports/          # 월간 리포트 저장소
│   │   ├── 2024-01.json
│   │   ├── 2024-02.json
│   │   └── ...
│   └── archives/                 # 오래된 데이터 아카이브
│       ├── 2024-01-status-changes.json
│       ├── 2024-02-status-changes.json
│       └── ...
├── config/
│   └── settings.json
├── docs/
│   ├── dashboard.html            # 실시간 대시보드
│   ├── weekly-report.html        # 주간 리포트 템플릿
│   └── assets/
│       ├── css/
│       └── js/
├── requirements.txt
└── README.md
```

## 파일 기록 방식

### 📊 실시간 데이터
- **`current-status.json`**: 현재 모든 서버의 상태 (매 체크마다 업데이트)
- **`status-changes.json`**: 상태 변화 이력만 기록 (sparse matrix 방식)

### 📈 주간 리포트
- **`weekly-reports/YYYY-WNN.json`**: 주별 통계 및 다운타임 요약
- **자동 생성**: 매주 일요일 자정에 전주 데이터 집계
- **포함 내용**: 다운타임 횟수, 총 다운타임 시간, 평균 응답시간, 가용성 %

### 📊 월간 리포트  
- **`monthly-reports/YYYY-MM.json`**: 월별 통계 및 트렌드 분석
- **자동 생성**: 매월 1일 자정에 전월 데이터 집계
- **포함 내용**: 월간 가용성, 다운타임 패턴, 성능 트렌드

### 🎯 대시보드
- **`docs/dashboard.html`**: 실시간 서버 상태 시각화
- **GitHub Pages**: 자동 배포로 웹에서 접근 가능
- **업데이트**: 상태 변화 시 자동 갱신

### 📦 데이터 보관 정책
- **`status-changes.json`**: 최근 30일간의 상태 변화만 유지
- **월별 아카이브**: `archives/YYYY-MM-status-changes.json`으로 이동
- **자동 정리**: 매월 1일 자정에 30일 이전 데이터 아카이브 처리
- **Git 히스토리**: 모든 상태 변화는 Git 커밋으로 영구 보존

## 설정 방법

1. **서버 목록 설정**: `data/servers.json`에 모니터링할 서버 정보 입력
2. **Slack 웹훅 설정**: GitHub Secrets에 `SLACK_WEBHOOK_URL` 추가
3. **GitHub Actions 활성화**: `.github/workflows/server-monitor.yml` 파일 생성
4. **모니터링 시작**: GitHub Actions가 자동으로 실행됨

## 사용 기술

- **GitHub Actions**: 자동화된 워크플로우
- **Python**: 서버 체크 및 알림 스크립트
- **Slack API**: 실시간 알림
- **JSON**: 데이터 저장
- **GitHub Pages**: 상태 대시보드

## 라이선스

MIT License 