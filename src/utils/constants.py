ODDSPORTAL_BASE_URL = "https://www.oddsportal.com"

PLAYWRIGHT_BROWSER_ARGS = [
    "--disable-background-networking",
    "--disable-extensions",
    "--mute-audio",
    "--window-size=1280,720",
    "--disable-popup-blocking",
    "--disable-translate",
    "--no-first-run",
    "--disable-infobars",
    "--disable-features=IsolateOrigins,site-per-process",
    "--enable-gpu-rasterization",
    "--disable-blink-features=AutomationControlled",
]

PLAYWRIGHT_BROWSER_ARGS_DOCKER = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-accelerated-2d-canvas",
    "--no-first-run",
    "--no-zygote",
    "--single-process",
    "--disable-gpu",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-web-security",
    "--disable-blink-features=AutomationControlled",
    "--window-size=1920,1080",
    "--start-maximized",
    "--disable-background-networking",
    "--disable-popup-blocking",
    "--disable-extensions",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]
