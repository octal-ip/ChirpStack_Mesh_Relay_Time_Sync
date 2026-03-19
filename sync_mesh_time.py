import sys
import argparse
import re
import paho.mqtt.client as mqtt
from chirpstack_api import gw
import datetime

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USER = "YourUser"
MQTT_PASS = "YourPass"
COMMAND_TYPE = 150
PREFIX = "au915_1"

def validate_hex(value, length):
    """Checks if the string is a valid hex of the required length."""
    if not re.fullmatch(r'[0-9a-fA-F]{' + str(length) + r'}', value):
        raise argparse.ArgumentTypeError(f"Must be a {length}-character hex string.")
    return value.lower()

def send_time_sync(time_str, gateway_str, relay_str):
    mesh_cmd = gw.MeshCommand()
    mesh_cmd.gateway_id = gateway_str
    mesh_cmd.relay_id = relay_str

    item = mesh_cmd.commands.add()
    item.proprietary.command_type = COMMAND_TYPE
    item.proprietary.payload = time_str.encode('utf-8')

    payload_binary = mesh_cmd.SerializeToString()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER and MQTT_PASS:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        topic_name = f"{PREFIX}/gateway/{gateway_str}/command/mesh"
        result = client.publish(topic_name, payload_binary)
        result.wait_for_publish()
        client.disconnect()
        print(f"✅ Sent MeshCommand {COMMAND_TYPE} to {topic_name} containing {time_str}")
    except Exception as e:
        print(f"❌ MQTT Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send Time Sync to ChirpStack Relay Gateway")

    # Positional arguments with validation
    parser.add_argument("gateway", type=lambda x: validate_hex(x, 16),
                        help="Target Gateway ID (16 hex chars)")
    parser.add_argument("relay", type=lambda x: validate_hex(x, 8),
                        help="Target Relay ID (8 hex chars)")

    # Optional argument for time (defaults to now)
    parser.add_argument("--time", type=str,
                        default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        help="Override time string (YYYY-MM-DD HH:MM:SS)")

    args = parser.parse_args()

    print(f"Sending {args.time} to relay {args.relay} via gateway {args.gateway}")
    send_time_sync(args.time, args.gateway, args.relay)

    print(f"Sending {args.time} to relay {args.relay} via gateway {args.gateway}")
    send_time_sync(args.time, args.gateway, args.relay)
