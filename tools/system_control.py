"""
System Control — Full PC control
"""

import os
import platform
import subprocess
import json


def get_system_info():
    """PC ki full information"""
    try:
        import psutil

        info = f"""💻 System Information:

OS: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Processor: {platform.processor()}

CPU Usage: {psutil.cpu_percent(interval=1)}%
CPU Cores: {psutil.cpu_count(logical=True)}

RAM Usage: {psutil.virtual_memory().percent}%
RAM Total: {psutil.virtual_memory().total // (1024**3)} GB
RAM Used: {psutil.virtual_memory().used // (1024**3)} GB

Disk Usage: {psutil.disk_usage('/').percent}%
Disk Total: {psutil.disk_usage('/').total // (1024**3)} GB
Disk Free: {psutil.disk_usage('/').free // (1024**3)} GB

Boot Time: {psutil.boot_time()}
"""
        return info
    except ImportError:
        return f"OS: {platform.system()}\nProcessor: {platform.processor()}\nInstall psutil for more info: pip install psutil"


def list_processes():
    """Running processes list karo"""
    try:
        import psutil
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(p.info)
            except Exception:
                continue

        processes.sort(key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)

        output = "🔧 Top Processes:\n\n"
        for p in processes[:15]:
            output += f"PID: {p['pid']} | {p['name']} | CPU: {p.get('cpu_percent', 0)}% | RAM: {p.get('memory_percent', 0):.1f}%\n"
        return output
    except Exception as e:
        return f"Error: {e}"


def kill_process(pid):
    """Process kill karo"""
    try:
        import psutil
        p = psutil.Process(int(pid))
        name = p.name()
        p.terminate()
        return f"Process killed: {name} (PID: {pid})"
    except Exception as e:
        return f"Error: {e}"


def run_network_scan():
    """Network scan karo"""
    try:
        result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True, timeout=10)
        return f"🌐 Network Info:\n\n{result.stdout[:2000]}"
    except Exception as e:
        return f"Error: {e}"


def run_speed_test():
    """Internet speed test"""
    return "Speed test requires: pip install speedtest-cli\nThen: speedtest-cli"


def get_wifi_passwords():
    """WiFi passwords dekho (ethical use only)"""
    try:
        result = subprocess.run(
            'netsh wlan show profiles',
            shell=True, capture_output=True, text=True, timeout=10
        )
        profiles = []
        for line in result.stdout.split("\n"):
            if "All User Profile" in line:
                name = line.split(":")[-1].strip()
                profiles.append(name)

        output = "📶 WiFi Profiles:\n\n"
        for profile in profiles[:10]:
            output += f"- {profile}\n"

        return output
    except Exception as e:
        return f"Error: {e}"


def open_port_scan(host="127.0.0.1"):
    """Port scan (localhost only for safety)"""
    try:
        import socket
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080]

        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()

        if open_ports:
            return f"🔓 Open ports on {host}: {', '.join(map(str, open_ports))}"
        return f"No common ports open on {host}"
    except Exception as e:
        return f"Error: {e}"


def manage_startup():
    """Startup programs dekho"""
    try:
        import winreg
        output = "🚀 Startup Programs:\n\n"

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run")

        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                output += f"- {name}: {value[:80]}...\n"
                i += 1
            except OSError:
                break

        winreg.CloseKey(key)
        return output if i > 0 else "No startup programs found."
    except Exception as e:
        return f"Error: {e}"