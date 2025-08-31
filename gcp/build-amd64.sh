#!/bin/bash

# linux/amd64용 Docker 이미지 빌드 및 푸시

echo "=== linux/amd64 Docker 이미지 빌드 ==="

PROJECT_ID=${GCP_PROJECT_ID:-"single-mix-469714-r2"}
IMAGE_NAME="odds-harvester"
IMAGE_TAG="amd64"

# 일반 Docker build로 linux/amd64 명시
echo "Building for linux/amd64..."
cd ..
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    echo "✓ Build successful"
    
    # 태그 추가
    docker tag gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    
    # GCR에 푸시
    echo "Pushing to GCR..."
    docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
    docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    
    if [ $? -eq 0 ]; then
        echo "✓ Push successful"
        echo ""
        echo "이미지 URL:"
        echo "- gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG"
        echo "- gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"
    else
        echo "✗ Push failed"
    fi
else
    echo "✗ Build failed"
fi