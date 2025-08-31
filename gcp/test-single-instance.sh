#!/bin/bash

# 단일 인스턴스 테스트 스크립트

PROJECT_ID="single-mix-469714-r2"
IMAGE_NAME="odds-harvester"
TAG="v1.1-fixed"
INSTANCE="odds-collector-1"
ZONE="asia-northeast3-a"

echo "=== ${INSTANCE}에서 수정된 버전 테스트 ==="

# 1. 로컬에서 이미지 빌드
echo "1. Docker 이미지 빌드..."
cd .. && docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .

# 2. GCR에 푸시
echo "2. GCR에 푸시..."
docker tag ${IMAGE_NAME}:${TAG} gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}
docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}

# 3. 테스트 인스턴스에 배포
echo "3. ${INSTANCE}에 배포..."
gcloud compute ssh ${INSTANCE} --zone=${ZONE} --command "
    echo '기존 컨테이너 중지...' && \
    docker stop odds-collector 2>/dev/null || true && \
    docker rm odds-collector 2>/dev/null || true && \
    echo '새 이미지 다운로드...' && \
    docker pull gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} && \
    echo '새 컨테이너 실행...' && \
    docker run -d --name odds-collector \
        -v /home/letsgopolands/data-test:/app/data \
        gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG} && \
    echo '컨테이너 상태 확인...' && \
    docker ps | grep odds-collector
"

# 4. 테스트 실행
echo ""
echo "4. 배당 수집 테스트 실행..."
gcloud compute ssh ${INSTANCE} --zone=${ZONE} --command "
    docker exec odds-collector bash -c '
        echo \"테스트 시작...\" && \
        uv run python src/main.py scrape_historic \
            --match_links \"https://www.oddsportal.com/football/belgium/jupiler-league-2020-2021/antwerp-anderlecht-Iusx5MVa/\" \
            --sport football \
            --leagues belgium-jupiler-pro-league \
            --season 2020-2021 \
            --markets over_under_2_5 \
            --format csv \
            --file_path data/test_docker.csv \
            --headless \
            --concurrency_tasks 1 && \
        echo \"\" && \
        echo \"수집된 데이터 확인:\" && \
        head -1 data/test_docker.csv | tr \",\" \"\\n\" | grep -n . && \
        echo \"\" && \
        echo \"마켓 데이터 존재 여부:\" && \
        if grep -q \"over_under\" data/test_docker.csv; then \
            echo \"✓ 마켓 데이터 수집 성공!\" && \
            head -2 data/test_docker.csv | tail -1 | cut -d\",\" -f12 | head -c 200 \
        else \
            echo \"✗ 마켓 데이터 수집 실패\" \
        fi
    '
"

echo ""
echo "=== 테스트 완료 ==="