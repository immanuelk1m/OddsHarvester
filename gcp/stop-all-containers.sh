#!/bin/bash

# 모든 인스턴스의 Docker 컨테이너 중지

echo "=== 모든 컨테이너 중지 ==="
echo ""

PROJECT_ID=${GCP_PROJECT_ID:-"single-mix-469714-r2"}
ZONE=${GCP_ZONE:-"asia-northeast3-a"}

for i in {1..7}; do
    INSTANCE_NAME="odds-collector-$i"
    
    echo "Stopping containers on $INSTANCE_NAME..."
    
    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
        docker stop \$(docker ps -q) 2>/dev/null || echo 'No containers to stop'
        docker ps -a
    " 2>/dev/null || echo "Failed to connect to $INSTANCE_NAME"
    
    echo ""
done

echo "=== 완료 ==="