# ChirpStack Mesh Relay Time Sync
A Python-based utility for syncing time to isolated/offline ChirpStack v4 mesh relays.

## Overview
ChirpStack relay nodes require synchronized time for logging, scheduled tasks and proper handling of event/status messages, but may lack a Real-Time Clock (RTC), GPS or network access. This solution runs a Python script on the **Border Gateway** which captures the current system time, encodes it into a ChirpStack-compliant "MeshCommand" protobuf message, and broadcasts it to the relay over LoRaWAN. The relay running ChirpStack Gateway OS v4 then runs a small local script to update the system time as instructed by the border gateway.


## Architecture
1.  **Source:** Border gateway system time (should be NTP synced).
2.  **Encoding:** Python chirpstack-api serializes data into a MeshCommand.
3.  **Transport:** paho-mqtt is used to send the command to the MQTT broker on the border gateway, which in turn sends the command to the remote relay over LoRaWAN.
4.  **Destination:** The relay node running ChirpStack Gateway OS v4 receives the proprietary command (type 150) and updates its internal clock via a simple shell script.

## Installation
**Border Gateway:**  
1. The _chirpstack-api_ and _paho-mqtt_ PIP modules must be installed on the border gateway: `pip install chirpstack-api paho-mqtt`
2. Deploy `sync_mesh_time.py` to _/var/opt/_.
3. `sync_mesh_time.py` should be run as a cron job on the border gateway, with the gateway ID and relay ID specified in the command line. e.g: `0 */6 * * * /root/venv/bin/python3 /var/opt/sync_mesh_time.py 1122aabbccddeeff 11223344`  
Where `1122aabbccddeeff` is the gateway ID, and `11223344` is the relay ID.  
4. Edit the variables in the _--- Configuration ---_ section of `sync_mesh_time.py`:  
`MQTT_BROKER` IP of your ChirpStack MQTT broker.  
`MQTT_USER/MQTT_PASS` Your MQTT credentials.  
`PREFIX` Your ChirpStack topic prefix (e.g. region code).
  
**Relay Gateway:**  
1. `update_time_command.sh` must be deployed to the relay gateway under _/usr/bin_, and made executable: `chmod +x /usr/bin/update_time_command.sh`.  
The script should also be added to `sysupgrade.conf` to be sure it's preserved during a firmware update: `echo "/usr/bin/update_time_command.sh" >> /etc/sysupgrade.conf`
2. The following lines should be added to `/etc/config/chirpstack-gateway-mesh` on the relay gateway to enable the command:
```
config commands_commands '150'
        list command '/usr/bin/update_time_command.sh'
```
3. Restart the gateway-mesh service: `/etc/init.d/chirpstack-gateway-mesh restart`


## Manual Usage
**Auto-sync current time**  
python3 sync_mesh_time.py <GATEWAY_ID> <RELAY_ID>

**Sync specific time**  
python3 sync_mesh_time.py <GATEWAY_ID> <RELAY_ID> --time "2026-01-01 09:00:00"

