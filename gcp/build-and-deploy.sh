#!/bin/bash

# GCP Docker 이미지 빌드 및 배포 스크립트

PROJECT_ID="single-mix-469714-r2"
IMAGE_NAME="odds-harvester"
TAG="v1.1-fixed"

echo "=== OddsHarvester Docker 이미지 빌드 및 배포 ==="
echo "브라우저 옵션이 수정된 버전을 배포합니다."

# 1. Docker 이미지 빌드
echo "1. Docker 이미지 빌드 중..."
docker build -t ${IMAGE_NAME}:${TAG} -f ../Dockerfile ..

# 2. GCR에 태그 지정
echo "2. GCR 태그 지정..."
docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# 3. GCR에 푸시
echo "3. GCR에 이미지 푸시..."
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# 4. 각 인스턴스에 배포
echo "4. GCP 인스턴스에 배포..."
for i in 1 2 3 4 5; do
    echo "   odds-collector-${i} 배포 중..."
    gcloud compute ssh odds-collector-${i} --zone=asia-northeast3-a --command "
        docker pull gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} && \
        docker stop odds-collector || true && \
        docker rm odds-collector || true && \
        docker run -d --name odds-collector \
            -v /home/letsgopolands/data:/app/data \
            gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
    "
done

echo "=== 배포 완료 ==="
echo "테스트 명령어:"
echo "gcloud compute ssh odds-collector-1 --zone=asia-northeast3-a"
echo "docker exec -it odds-collector bash"
echo "./docker-debug.sh"