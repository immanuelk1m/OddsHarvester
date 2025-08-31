#!/bin/bash

# Startup script template for odds-collector instances
# This will be customized for each league

# Set variables
PROJECT_ID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
INSTANCE_NAME=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/name" -H "Metadata-Flavor: Google")
ZONE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | cut -d'/' -f4)
LEAGUE=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/attributes/league" -H "Metadata-Flavor: Google")

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
cat > docker-compose.yml <<EOF
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
EOF

# Start the container
echo "Starting Docker container for $LEAGUE..."
docker-compose up -d

# Create a cron job for daily execution (optional)
CRON_FILE="/etc/cron.d/odds-harvester"
cat > $CRON_FILE <<EOF
# Run odds harvester daily at 2 AM KST (5 PM UTC)
0 17 * * * root cd $WORK_DIR && docker-compose restart >> /var/log/odds-harvester-cron.log 2>&1
EOF

# Set up log rotation
cat > /etc/logrotate.d/odds-harvester <<EOF
/var/log/odds-harvester*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF

echo "=== Startup Script Completed at $(date) ==="