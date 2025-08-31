#!/bin/bash

# 7개 인스턴스에서 기본 리그 실행 스크립트

echo "=== 기본 리그 데이터 수집 배포 ==="
echo ""

PROJECT_ID=${GCP_PROJECT_ID:-"single-mix-469714-r2"}
ZONE=${GCP_ZONE:-"asia-northeast3-a"}
IMAGE_URL="gcr.io/$PROJECT_ID/odds-harvester:latest"

# 인스턴스별 기본 리그 매핑
declare -a ASSIGNMENTS=(
    "1:belgium"
    "2:denmark"
    "3:england"
    "4:france"
    "5:germany"
    "6:italy"
    "7:netherlands"
)

echo "기본 리그 할당:"
echo "- odds-collector-1: Belgium"
echo "- odds-collector-2: Denmark"
echo "- odds-collector-3: England"
echo "- odds-collector-4: France"
echo "- odds-collector-5: Germany"
echo "- odds-collector-6: Italy"
echo "- odds-collector-7: Netherlands"
echo ""

# 각 인스턴스에 기본 컨테이너 실행
for assignment in "${ASSIGNMENTS[@]}"; do
    IFS=':' read -r instance_num primary_league <<< "$assignment"
    INSTANCE_NAME="odds-collector-$instance_num"
    
    echo "=== $INSTANCE_NAME에 $primary_league 배포 ==="
    
    # SSH로 기본 Docker 컨테이너 실행
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        # 기존 컨테이너가 있다면 중지
        sudo docker stop odds-harvester-$primary_league 2>/dev/null || true
        sudo docker rm odds-harvester-$primary_league 2>/dev/null || true
        
        # 데이터 디렉토리 생성
        sudo mkdir -p /opt/odds-harvester/data-$primary_league
        
        # 컨테이너 실행
        sudo docker run -d \
            --name odds-harvester-$primary_league \
            -v /opt/odds-harvester/data-$primary_league:/app/data \
            -e LEAGUE=$primary_league \
            -e TZ=Asia/Seoul \
            --restart unless-stopped \
            $IMAGE_URL \
            /app/collect_${primary_league}.sh
        
        # 상태 확인
        echo '컨테이너 상태:'
        sudo docker ps | grep odds-harvester-$primary_league
    " || echo "Failed to connect to $INSTANCE_NAME"
    
    echo ""
done

echo "=== 배포 완료 ==="
echo ""
echo "모든 컨테이너 상태:"
for i in {1..7}; do
    echo "--- odds-collector-$i ---"
    gcloud compute ssh odds-collector-$i --zone=$ZONE \
        --command="sudo docker ps --format 'table {{.Names}}\t{{.Status}}' | grep odds-harvester" 2>/dev/null || echo "연결 실패"
    echo ""
done