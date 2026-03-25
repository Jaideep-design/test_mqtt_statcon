import threading
import time
from typing import Any, Dict

latest_data_lock = threading.Lock()
latest_data: Dict[str, Any] = {}

def update_latest(raw, parsed_rows, device_id, topic):
    with latest_data_lock:
        latest_data[device_id] = {
            "raw": raw,
            "parsed": parsed_rows,
            "topic": topic,
            "last_updated": time.time(),
        }

def get_latest_data(device_id=None):
    with latest_data_lock:
        if device_id:
            return latest_data.get(device_id)
        return latest_data
