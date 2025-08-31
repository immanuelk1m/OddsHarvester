#!/bin/bash

# Startup script for france odds-collector instance

# Set variables
PROJECT_ID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
INSTANCE_NAME=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/name" -H "Metadata-Flavor: Google")
ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | cut -d'/' -f4)
LEAGUE="france"

# Log file
LOG_FILE="/var/log/startup-script.log"
exec 1> >(tee -a ${LOG_FILE})
exec 2>&1

echo "=== Startup Script Started at $(date) ==="
echo "Instance: $INSTANCE_NAME"
echo "League: $LEAGUE"
echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"

# Update system
echo "Updating system packages..."
apt-get update

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
else
    echo "Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    apt-get install -y docker-compose
else
    echo "Docker Compose already installed"
fi

# Install Google Cloud SDK if not present
if ! command -v gcloud &> /dev/null; then
    echo "Installing Google Cloud SDK..."
    snap install google-cloud-sdk --classic
else
    echo "Google Cloud SDK already installed"
fi

# Configure Docker for GCR
echo "Configuring Docker for GCR..."
gcloud auth configure-docker gcr.io --quiet

# Pull the latest image
IMAGE_URL="gcr.io/$PROJECT_ID/odds-harvester:latest"
echo "Pulling Docker image: $IMAGE_URL"
docker pull $IMAGE_URL

# Create working directory
WORK_DIR="/opt/odds-harvester"
mkdir -p $WORK_DIR/data
cd $WORK_DIR

# Create docker-compose.yml
cat > docker-compose.yml <<EOFDOCKER
version: '3.8'

services:
  odds-harvester:
    image: $IMAGE_URL
    container_name: odds-harvester-$LEAGUE
    volumes:
      - ./data:/app/data
      - /mnt/gcs-data:/mnt/gcs-data
    environment:
      - LEAGUE=$LEAGUE
      - INSTANCE_NAME=$INSTANCE_NAME
      - TZ=Asia/Seoul
    restart: unless-stopped
    command: /app/collect_${LEAGUE}.sh
EOFDOCKER

# Start the container
echo "Starting Docker container for $LEAGUE..."
docker-compose up -d

# Check container status
sleep 5
if docker ps | grep -q "odds-harvester-$LEAGUE"; then
    echo "✓ Container started successfully"
else
    echo "✗ Container failed to start"
    docker-compose logs
fi

echo "=== Startup Script Completed at $(date) ==="
