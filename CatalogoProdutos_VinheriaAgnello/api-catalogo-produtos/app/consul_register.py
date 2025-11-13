import os
import requests
import socket

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
SERVICE_NAME = "product"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 80))
SERVICE_ID = f"{SERVICE_NAME}-{socket.gethostname()}"

def register():
    payload = {
        "ID": SERVICE_ID,
        "Name": SERVICE_NAME,
        "Address": SERVICE_ID,  # Consul will use container IP if address blank; you can leave it blank
        "Port": SERVICE_PORT,
        "Check": {
            "HTTP": f"http://{SERVICE_NAME}:{SERVICE_PORT}/health", # or /health if you add one
            "Interval": "10s"
        }
    }
    try:
        requests.put(f"http://{CONSUL_HOST}:8500/v1/agent/service/register", json=payload, timeout=3)
        print("registered to consul")
    except Exception as e:
        print("consul register failed", e)

if __name__:
    register()
