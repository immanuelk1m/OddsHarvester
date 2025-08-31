FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation \
    fonts-unifont \
    libgtk-3-0 \
    libnotify4 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY match_urls_complete ./match_urls_complete
COPY collect_*.sh ./

# Install Python dependencies
RUN uv sync

# Install Playwright and Chromium
RUN uv run playwright install chromium
# Skip install-deps as we already installed all required dependencies manually

# Create data directory and GCS mount point
RUN mkdir -p data /mnt/gcs-data

# Make all collect scripts executable
RUN chmod +x collect_*.sh

# Set environment variables for headless operation
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

# Default command
CMD ["/bin/bash"]