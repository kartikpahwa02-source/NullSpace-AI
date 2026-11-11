"""
Smart Home Controller
- Lights on/off
- Fan control
- AC control
- Temperature check
- Custom device commands
"""

import requests
import json
from config.settings import SMART_HOME_DEVICES


def list_devices():
    """Connected devices list karo"""
    if not SMART_HOME_DEVICES:
        return "Koi smart device configured nahi hai.\nconfig/settings.py me SMART_HOME_DEVICES add karo."

    result = "Connected Smart Home Devices:\n"
    for name, info in SMART_HOME_DEVICES.items():
        result += f"- {name}: {info['type']} ({info['ip']}:{info['port']})\n"
    return result


def control_device(device_name, action):
    """Device ko control karo"""
    if device_name not in SMART_HOME_DEVICES:
        # Check partial match
        matches = [k for k in SMART_HOME_DEVICES if device_name.lower() in k.lower()]
        if matches:
            device_name = matches[0]
        else:
            return f"Device '{device_name}' not found. Available: {list(SMART_HOME_DEVICES.keys())}"

    device = SMART_HOME_DEVICES[device_name]
    ip = device["ip"]
    port = device["port"]
    device_type = device["type"]

    try:
        # Send command to device
        url = f"http://{ip}:{port}/control"
        payload = {"device": device_name, "action": action}

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            return f"{device_name} ({device_type}): {action} - Done!"
        else:
            return f"Device response: {response.status_code}"

    except requests.ConnectionError:
        return f"Cannot connect to {device_name} ({ip}:{port}). Check if device is online."
    except Exception as e:
        return f"Smart Home Error: {e}"


def light_on(device_name="living_room_light"):
    return control_device(device_name, "on")


def light_off(device_name="living_room_light"):
    return control_device(device_name, "off")


def fan_on(device_name="bedroom_fan", speed=3):
    return control_device(device_name, f"on_speed_{speed}")


def fan_off(device_name="bedroom_fan"):
    return control_device(device_name, "off")


def ac_on(device_name="ac", temp=24):
    return control_device(device_name, f"on_temp_{temp}")


def ac_off(device_name="ac"):
    return control_device(device_name, "off")


def get_temperature(device_name="ac"):
    """Temperature check karo"""
    if device_name not in SMART_HOME_DEVICES:
        return f"Device '{device_name}' not found."

    device = SMART_HOME_DEVICES[device_name]
    try:
        url = f"http://{device['ip']}:{device['port']}/status"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Temperature: {data.get('temperature', 'N/A')}°C"
        return f"Status: {response.status_code}"
    except Exception as e:
        return f"Status check failed: {e}"


def smart_home_scene(scene_name):
    """Pre-defined scene activate karo"""
    scenes = {
        "movie": [
            ("living_room_light", "dim_20"),
            ("ac", "on_temp_22")
        ],
        "sleep": [
            ("living_room_light", "off"),
            ("bedroom_fan", "on_speed_1"),
            ("ac", "on_temp_26")
        ],
        "wake_up": [
            ("living_room_light", "on"),
            ("ac", "off")
        ],
        "party": [
            ("living_room_light", "on_bright"),
            ("ac", "on_temp_20")
        ]
    }

    if scene_name not in scenes:
        available = ", ".join(scenes.keys())
        return f"Scene '{scene_name}' not found. Available: {available}"

    results = []
    for device, action in scenes[scene_name]:
        r = control_device(device, action)
        results.append(f"- {device}: {r}")

    return f"Scene '{scene_name}' activated:\n" + "\n".join(results)