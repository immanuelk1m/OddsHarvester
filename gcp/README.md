# GCP 배포 가이드

## 개요
이 가이드는 13개의 GCP 인스턴스에 OddsHarvester를 Docker로 배포하는 방법을 설명합니다.

## 사전 준비사항
- GCP 계정 및 프로젝트
- gcloud CLI 설치 및 인증
- Docker 설치 (로컬 빌드용)
- 충분한 GCP 할당량 (13개 e2-medium 인스턴스)

## 빠른 시작

### 1. 환경 변수 설정
```bash
cd gcp
cp .env.example .env
# .env 파일을 편집하여 GCP_PROJECT_ID 설정
export $(cat .env | xargs)
```

### 2. 전체 배포 실행
```bash
./deploy-all.sh
```

이 스크립트는 다음 작업을 자동으로 수행합니다:
- gcloud 인증 확인
- 필요한 API 활성화
- Docker 이미지 빌드 및 GCR 푸시
- 13개 인스턴스 생성
- 각 인스턴스에 자동으로 Docker 컨테이너 실행

## 개별 작업

### 기존 인스턴스 제거
```bash
./remove-instances.sh
```

### Docker 이미지 빌드 및 푸시
```bash
./build-and-push.sh
```

### 인스턴스 생성
```bash
./create-instances.sh
```

## 인스턴스 매핑

| 인스턴스 | 리그 | 데이터 수집 스크립트 |
|---------|------|-------------------|
| odds-collector-1 | Belgium | collect_belgium.sh |
| odds-collector-2 | Denmark | collect_denmark.sh |
| odds-collector-3 | England | collect_england.sh |
| odds-collector-4 | France | collect_france.sh |
| odds-collector-5 | Germany | collect_germany.sh |
| odds-collector-6 | Italy | collect_italy.sh |
| odds-collector-7 | Netherlands | collect_netherlands.sh |
| odds-collector-8 | Norway | collect_norway.sh |
| odds-collector-9 | Portugal | collect_portugal.sh |
| odds-collector-10 | Scotland | collect_scotland.sh |
| odds-collector-11 | Spain | collect_spain.sh |
| odds-collector-12 | Sweden | collect_sweden.sh |
| odds-collector-13 | Switzerland | collect_switzerland.sh |

## 모니터링

### 인스턴스 목록 확인
```bash
gcloud compute instances list --filter="name:odds-collector-*"
```

### 인스턴스 SSH 접속
```bash
gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a
```

### 스타트업 스크립트 로그 확인
```bash
gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a \
  --command='sudo cat /var/log/startup-script.log'
```

### Docker 컨테이너 상태 확인
```bash
gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a \
  --command='docker ps'
```

### Docker 컨테이너 로그 확인
```bash
gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a \
  --command='docker logs odds-harvester-belgium'
```

## 데이터 수집 확인

각 인스턴스는 자동으로 해당 리그의 데이터를 수집합니다.
수집된 데이터는 `/opt/odds-harvester/data` 디렉토리에 저장됩니다.

### 수집된 데이터 확인
```bash
gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a \
  --command='ls -la /opt/odds-harvester/data/'
```

## 문제 해결

### 인스턴스가 시작되지 않는 경우
1. GCP 콘솔에서 할당량 확인
2. 방화벽 규칙 확인
3. 스타트업 스크립트 로그 확인

### Docker 컨테이너가 실행되지 않는 경우
1. Docker 이미지가 GCR에 있는지 확인
2. 인스턴스의 서비스 계정 권한 확인
3. Docker 로그 확인

### 데이터 수집이 실패하는 경우
1. 컨테이너 로그 확인
2. 네트워크 연결 확인
3. 스크립트 권한 확인

## 비용 관리

- 사용하지 않을 때는 인스턴스 중지
- 자동 스케줄링으로 필요한 시간에만 실행
- 작은 인스턴스 타입 사용 고려 (e2-small)

## 체크리스트
배포 진행 상황은 `../check_list.md` 파일을 참조하세요.