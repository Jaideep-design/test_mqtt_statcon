import threading
import time
from typing import List, Dict, Any, Optional

from paho.mqtt import client as mqtt

from .parser_logic import parse_packet
from .shared_state import update_latest

# Global worker state
_worker_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()

_current_config_lock = threading.Lock()
_current_config: Dict[str, Any] = {
    "broker": None,
    "port": 1883,
    "topic": None,
    "device_id": None,
    "registers": None,
    "username": None,
    "password": None,
}

def extract_device_id(topic: str):
    try:
        return topic.split("/")[-2]
    except Exception:
        return "UNKNOWN"

def _mqtt_loop():
    """Background loop that connects to MQTT and listens for messages."""
    global _stop_event

    with _current_config_lock:
        broker = _current_config["broker"]
        port = _current_config["port"]
        topic = _current_config["topic"]
        device_id = _current_config["device_id"]
        registers = _current_config["registers"]
        username = _current_config["username"]
        password = _current_config["password"]

    if not broker or not registers:
        return

    client = mqtt.Client()

    # Set authentication
    if username and password:
        client.username_pw_set(username, password)

    # TLS for secure broker
    if port == 8883:
        import os
        import ssl

        base_dir = os.path.dirname(__file__)
        ca_path = os.path.join(base_dir, "ca.crt")

        print("[MQTT] Using CA certificate:", ca_path)

        client.tls_set(
            ca_certs=ca_path,
            cert_reqs=ssl.CERT_NONE,
            tls_version=ssl.PROTOCOL_TLS
        )

    def on_connect(client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")
        # client.subscribe("/GTI/STATCON/102/+/LiveData")
        client.subscribe("/GTI/STATCON/102/GTIPROTO00003/LiveData")

    def on_message(client, userdata, msg):
        print(f"[MQTT] Message received on {msg.topic}")

        raw = msg.payload.decode("utf-8", "ignore")
        parsed_rows = parse_packet(raw, registers)
        topic = msg.topic
        device_id = extract_device_id(topic)
        
        update_latest(raw, parsed_rows, device_id, topic)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"[MQTT] Connecting to {broker}:{port}")
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"[MQTT] Connection error: {e}")
        return

    while not _stop_event.is_set():
        client.loop(timeout=1.0)
        time.sleep(0.1)

    client.disconnect()

def configure_and_start_mqtt(
    broker,
    port,
    topic,
    device_id,
    registers,
    username=None,
    password=None
):
    """
    Called by the API when user updates configuration (topic/device/dictionary).
    Stops any existing worker and starts a new one.
    """
    global _worker_thread, _stop_event

    # Stop existing worker if running
    if _worker_thread and _worker_thread.is_alive():
        _stop_event.set()
        _worker_thread.join(timeout=2)

    # Update config
    with _current_config_lock:
        _current_config["broker"] = broker
        _current_config["port"] = int(port)
        _current_config["topic"] = topic
        _current_config["device_id"] = device_id
        _current_config["registers"] = registers
        _current_config["username"] = username
        _current_config["password"] = password

    # Start new worker
    _stop_event = threading.Event()
    _worker_thread = threading.Thread(target=_mqtt_loop, daemon=True)
    _worker_thread.start()
