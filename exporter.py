import time
import requests
from prometheus_client import start_http_server, Gauge

CONFIDENCE_GAUGE = Gauge('prediction_confidence_score', 'Latest ML model prediction confidence')

APP_URL = "http://localhost:32500/api/latest-confidence"

def fetch_confidence():
    try:
        resp = requests.get(APP_URL, timeout=5)
        data = resp.json()
        return float(data.get("confidence", 1.0))
    except Exception:
        return 1.0

if __name__ == "__main__":
    start_http_server(8000)
    print("Exporter running on port 8000")
    readings = []
    while True:
        conf = fetch_confidence()
        readings.append(conf)
        if len(readings) > 5:
            readings.pop(0)
        avg = sum(readings) / len(readings)
        CONFIDENCE_GAUGE.set(avg)
        time.sleep(5)
