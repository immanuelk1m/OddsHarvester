# GCP 인스턴스 배포 체크리스트

## 1. 사전 준비
- [ ] GCP 프로젝트 ID 설정 확인
- [ ] gcloud CLI 인증 확인
- [ ] 기본 리전/존 설정 (asia-northeast3-a)
- [ ] 필요한 API 활성화 (Compute Engine, Container Registry)

## 2. 기존 인스턴스 제거 (odds-collector-1 ~ 5)
- [ ] odds-collector-1 중지
- [ ] odds-collector-1 삭제
- [ ] odds-collector-2 중지
- [ ] odds-collector-2 삭제
- [ ] odds-collector-3 중지
- [ ] odds-collector-3 삭제
- [ ] odds-collector-4 중지
- [ ] odds-collector-4 삭제
- [ ] odds-collector-5 중지
- [ ] odds-collector-5 삭제

## 3. Docker 이미지 준비
- [ ] Dockerfile 생성
- [ ] Docker 이미지 빌드
- [ ] Google Container Registry에 푸시
- [ ] 이미지 태그 확인

## 4. 새 인스턴스 생성 (odds-collector-1 ~ 13)

### 인스턴스 매핑
| 인스턴스 | 담당 리그 | 스크립트 |
|---------|---------|---------|
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

### 인스턴스 생성
- [ ] odds-collector-1 생성
- [ ] odds-collector-2 생성
- [ ] odds-collector-3 생성
- [ ] odds-collector-4 생성
- [ ] odds-collector-5 생성
- [ ] odds-collector-6 생성
- [ ] odds-collector-7 생성
- [ ] odds-collector-8 생성
- [ ] odds-collector-9 생성
- [ ] odds-collector-10 생성
- [ ] odds-collector-11 생성
- [ ] odds-collector-12 생성
- [ ] odds-collector-13 생성

## 5. 인스턴스 초기 설정
- [ ] 모든 인스턴스 시작 확인
- [ ] Docker 설치 확인
- [ ] Docker 이미지 pull 확인
- [ ] 스크립트 실행 권한 확인

## 6. 데이터 수집 테스트
- [ ] odds-collector-1: Belgium 데이터 수집 테스트
- [ ] odds-collector-2: Denmark 데이터 수집 테스트
- [ ] odds-collector-3: England 데이터 수집 테스트
- [ ] odds-collector-4: France 데이터 수집 테스트
- [ ] odds-collector-5: Germany 데이터 수집 테스트
- [ ] odds-collector-6: Italy 데이터 수집 테스트
- [ ] odds-collector-7: Netherlands 데이터 수집 테스트
- [ ] odds-collector-8: Norway 데이터 수집 테스트
- [ ] odds-collector-9: Portugal 데이터 수집 테스트
- [ ] odds-collector-10: Scotland 데이터 수집 테스트
- [ ] odds-collector-11: Spain 데이터 수집 테스트
- [ ] odds-collector-12: Sweden 데이터 수집 테스트
- [ ] odds-collector-13: Switzerland 데이터 수집 테스트

## 7. 모니터링 및 로깅
- [ ] Cloud Logging 설정
- [ ] 에러 알림 설정
- [ ] 리소스 사용량 모니터링
- [ ] 비용 알림 설정

## 8. 데이터 저장 확인
- [ ] GCS 버킷 생성/확인
- [ ] 데이터 업로드 테스트
- [ ] 백업 정책 설정

## 9. 최종 확인
- [ ] 모든 인스턴스 정상 작동
- [ ] 자동 실행 스케줄 설정
- [ ] 문서화 완료
- [ ] 팀 공유