#!/bin/bash

# Final working GCP download script
# Downloads all CSV files from GCP instances to local gcp/ directory
# Updated to download from /opt/odds-harvester for odds-collector-1 to 7

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ZONE="asia-northeast3-a"

echo "=========================================="
echo "GCP CSV Files Download Script"
echo "=========================================="
echo ""

start_time=$(date +%s)

# Function to download from instance
download_instance() {
    local i=$1
    local instance="odds-collector-${i}"
    local localdir="gcp/${instance}/data"
    
    echo -e "${BLUE}[${instance}] Starting...${NC}"
    
    # Create local directory
    mkdir -p "${localdir}"
    
    # Use find to list and copy files (avoids glob expansion issues)
    echo -e "${YELLOW}[${instance}] Preparing files...${NC}"
    
    file_count=$(gcloud compute ssh "${instance}" \
        --zone="${ZONE}" \
        --command="
            # Clean up any previous attempts
            rm -rf ~/csv_temp 2>/dev/null
            mkdir -p ~/csv_temp
            
            # Find and copy each CSV file individually from /opt/odds-harvester
            sudo find /opt/odds-harvester -name '*.csv' -type f | while read f; do
                sudo cp \"\$f\" ~/csv_temp/
            done
            
            # Fix permissions
            sudo chown -R \$(whoami):\$(whoami) ~/csv_temp/
            
            # Count files
            ls ~/csv_temp/*.csv 2>/dev/null | wc -l
        " 2>/dev/null | tail -1)
    
    if [ -z "$file_count" ] || [ "$file_count" = "0" ]; then
        echo -e "${RED}[${instance}] No CSV files found${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}[${instance}] Creating archive of ${file_count} files...${NC}"
    
    # Create tar archive
    gcloud compute ssh "${instance}" \
        --zone="${ZONE}" \
        --command="cd ~/csv_temp && tar -czf ~/data_archive.tar.gz *.csv" 2>/dev/null
    
    # Download archive
    echo -e "${YELLOW}[${instance}] Downloading...${NC}"
    
    if gcloud compute scp \
        --zone="${ZONE}" \
        "${instance}:~/data_archive.tar.gz" \
        "${localdir}/archive.tar.gz" 2>/dev/null; then
        
        # Extract
        cd "${localdir}"
        tar -xzf archive.tar.gz 2>/dev/null
        rm -f archive.tar.gz
        cd - >/dev/null
        
        # Clean up remote
        gcloud compute ssh "${instance}" \
            --zone="${ZONE}" \
            --command="rm -rf ~/csv_temp ~/data_archive.tar.gz" 2>/dev/null
        
        # Verify
        local actual_count=$(find "${localdir}" -name "*.csv" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}[${instance}] ✓ Downloaded ${actual_count} files${NC}"
        return 0
    else
        echo -e "${RED}[${instance}] ✗ Download failed${NC}"
        # Try to clean up
        gcloud compute ssh "${instance}" \
            --zone="${ZONE}" \
            --command="rm -rf ~/csv_temp ~/data_archive.tar.gz" 2>/dev/null
        return 1
    fi
}

# Run downloads in parallel
echo "Downloading from all instances..."
echo ""

for i in {1..7}; do
    download_instance $i &
done

# Wait for all
wait

end_time=$(date +%s)
duration=$((end_time - start_time))

# Summary
echo ""
echo "=========================================="
echo "DOWNLOAD SUMMARY"
echo "=========================================="

total_files=0
successful_instances=0

for i in {1..7}; do
    dir="gcp/odds-collector-${i}/data"
    if [ -d "${dir}" ]; then
        count=$(find "${dir}" -name "*.csv" -type f 2>/dev/null | wc -l)
        if [ $count -gt 0 ]; then
            size=$(du -sh "gcp/odds-collector-${i}" 2>/dev/null | cut -f1)
            echo -e "odds-collector-${i}: ${GREEN}${count} files${NC} (${size})"
            total_files=$((total_files + count))
            successful_instances=$((successful_instances + 1))
            
            # Show first 2 sample files
            echo "  Samples:"
            find "${dir}" -name "*.csv" -type f | sort | head -2 | while read f; do
                echo "    • $(basename "$f")"
            done
        else
            echo -e "odds-collector-${i}: ${YELLOW}No files${NC}"
        fi
    else
        echo -e "odds-collector-${i}: ${RED}Failed${NC}"
    fi
done

echo ""
if [ $total_files -gt 0 ]; then
    total_size=$(du -sh gcp 2>/dev/null | cut -f1)
    echo -e "Results: ${GREEN}${successful_instances}/7 instances${NC}"
    echo -e "Total files: ${GREEN}${total_files}${NC}"
    echo -e "Total size: ${GREEN}${total_size}${NC}"
    echo -e "Time: ${duration} seconds"
    echo ""
    echo -e "${GREEN}✅ Download successful!${NC}"
    echo -e "📁 Location: ${GREEN}$(pwd)/gcp/${NC}"
else
    echo -e "${RED}❌ No files downloaded${NC}"
    echo -e "Time: ${duration} seconds"
fi

# Clean up test file
rm -f test_download.csv 2>/dev/null