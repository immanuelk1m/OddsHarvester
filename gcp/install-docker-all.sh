#!/bin/bash

# 모든 인스턴스에 Docker 설치 및 설정

echo "=== 모든 인스턴스에 Docker 설치 ==="
echo ""

PROJECT_ID=${GCP_PROJECT_ID:-"single-mix-469714-r2"}
ZONE=${GCP_ZONE:-"asia-northeast3-a"}

for i in {1..7}; do
    INSTANCE_NAME="odds-collector-$i"
    
    echo "=== $INSTANCE_NAME Docker 설치 중 ==="
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        # Docker 설치 여부 확인
        if ! command -v docker &> /dev/null; then
            echo 'Docker 설치 시작...'
            
            # 패키지 업데이트
            sudo apt-get update
            
            # Docker 설치
            sudo apt-get install -y docker.io
            
            # Docker 서비스 시작
            sudo systemctl start docker
            sudo systemctl enable docker
            
            # docker-compose 설치
            sudo apt-get install -y docker-compose
            
            echo 'Docker 설치 완료'
        else
            echo 'Docker가 이미 설치되어 있습니다'
        fi
        
        # Docker 버전 확인
        sudo docker --version
        
        # GCR 인증 설정
        gcloud auth configure-docker gcr.io --quiet
        
        # 이미지 pull
        sudo docker pull gcr.io/$PROJECT_ID/odds-harvester:latest
        
        echo 'Docker 설정 완료'
    " || echo "Failed to connect to $INSTANCE_NAME"
    
    echo ""
done

echo "=== 설치 완료 ==="
echo ""
echo "Docker 상태 확인:"
for i in {1..7}; do
    echo -n "odds-collector-$i: "
    gcloud compute ssh odds-collector-$i --zone=$ZONE \
        --command="sudo docker --version" 2>/dev/null || echo "연결 실패"
done