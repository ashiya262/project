import random
import requests
import time


API_URL = "http://127.0.0.1:8000/readings/"

battery_id = 1


for i in range(20):

    reading = {
        "battery_id": battery_id,
        "voltage": round(random.uniform(45.0, 48.5), 2),
        "current": round(random.uniform(8.0, 15.0), 2),
        "temperature": round(random.uniform(25.0, 40.0), 2)
    }

    response = requests.post(
        API_URL,
        json=reading
    )

    print(
        f"Reading {i + 1}:",
        response.json()
    )

    time.sleep(1)