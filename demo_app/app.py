from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response
import psutil
import time
import logging
import os


# ==========================================
# APPLICATION SETUP
# ==========================================

app = FastAPI(
    title="NOC Demo Application"
)


# ==========================================
# LOGGING SETUP
# ==========================================

os.makedirs("logs", exist_ok=True)

log_file = os.path.abspath("logs/app.log")

logger = logging.getLogger("noc-demo-app")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    log_file
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# ==========================================
# PROMETHEUS METRICS
# ==========================================

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

CPU_USAGE = Gauge(
    "app_cpu_usage_percent",
    "Current CPU usage percentage"
)

MEMORY_USAGE = Gauge(
    "app_memory_usage_percent",
    "Current memory usage percentage"
)

INCIDENT_MODE = Gauge(
    "app_incident_mode",
    "Whether incident simulation mode is enabled"
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total number of simulated application errors"
)


# ==========================================
# INCIDENT STATE
# ==========================================

incident_mode = False


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    start = time.time()

    REQUEST_COUNT.labels(
        method="GET",
        endpoint="/",
        status="200"
    ).inc()

    latency = time.time() - start

    REQUEST_LATENCY.labels(
        endpoint="/"
    ).observe(latency)

    logger.info(
        "Request processed successfully | endpoint=/ | status=200"
    )

    return {
        "service": "NOC Demo Application",
        "status": "healthy",
        "incident_mode": incident_mode
    }


# ==========================================
# HEALTH ENDPOINT
# ==========================================

@app.get("/health")
def health():

    logger.info(
        "Health check executed | endpoint=/health | status=200"
    )

    return {
        "status": "healthy",
        "incident_mode": incident_mode
    }


# ==========================================
# ERROR ENDPOINT
# ==========================================

@app.get("/error")
def error():

    ERROR_COUNT.inc()

    REQUEST_COUNT.labels(
        method="GET",
        endpoint="/error",
        status="500"
    ).inc()

    logger.error(
        "Application error | endpoint=/error | "
        "status=500 | error_type=SimulatedApplicationFailure | "
        "message=Simulated application failure"
    )

    return Response(
        content='{"error": "Simulated application failure"}',
        status_code=500,
        media_type="application/json"
    )


# ==========================================
# START INCIDENT
# ==========================================

@app.post("/incident/start")
def start_incident():

    global incident_mode

    incident_mode = True

    logger.warning(
        "INCIDENT MODE ENABLED | "
        "CPU=95% | MEMORY=92%"
    )

    return {
        "message": "Incident simulation started",
        "incident_mode": True
    }


# ==========================================
# STOP INCIDENT
# ==========================================

@app.post("/incident/stop")
def stop_incident():

    global incident_mode

    incident_mode = False

    logger.info(
        "INCIDENT MODE DISABLED"
    )

    return {
        "message": "Incident simulation stopped",
        "incident_mode": False
    }


# ==========================================
# PROMETHEUS METRICS
# ==========================================

@app.get("/metrics")
def metrics():

    global incident_mode

    if incident_mode:

        CPU_USAGE.set(95)

        MEMORY_USAGE.set(92)

        INCIDENT_MODE.set(1)

    else:

        CPU_USAGE.set(
            psutil.cpu_percent(interval=0.1)
        )

        MEMORY_USAGE.set(
            psutil.virtual_memory().percent
        )

        INCIDENT_MODE.set(0)

    return Response(
        generate_latest(),
        media_type="text/plain"
    )
