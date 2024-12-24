from flask import Flask, jsonify, render_template
import psutil
import platform
import os
import subprocess
from cpuinfo import get_cpu_info

app = Flask(__name__)

@app.route("/api/")
def system_info_api():
    # CPU information
    cpu_usage = psutil.cpu_percent(interval=1)  # Overall CPU usage
    cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"  # Overall CPU frequency
    cpu_temp = get_cpu_temperatures()
    cpu_name = get_cpu_name()

    # Memory information
    virtual_memory = psutil.virtual_memory()
    ram_total = virtual_memory.total / (1024 ** 3)  # in GB
    ram_used = virtual_memory.used / (1024 ** 3)  # in GB
    ram_free = virtual_memory.available / (1024 ** 3)  # in GB

    # Disk information
    disk_usage = psutil.disk_usage('/')
    disk_total = disk_usage.total / (1024 ** 3)  # in GB
    disk_used = disk_usage.used / (1024 ** 3)  # in GB
    disk_free = disk_usage.free / (1024 ** 3)  # in GB

    # Battery information
    battery = psutil.sensors_battery()
    battery_status = {
        "percent": battery.percent if battery else "N/A",
        "charging": battery.power_plugged if battery else "N/A",
    }

    # System information
    system_info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": cpu_name,
    }

    return jsonify({
        "cpu": {
            "usage_percent": cpu_usage,
            "frequency_mhz": cpu_freq,
            "temperature_celsius": cpu_temp,
        },
        "ram": {
            "total_gb": round(ram_total, 2),
            "used_gb": round(ram_used, 2),
            "free_gb": round(ram_free, 2),
        },
        "disk": {
            "total_gb": round(disk_total, 2),
            "used_gb": round(disk_used, 2),
            "free_gb": round(disk_free, 2),
        },
        "battery": battery_status,
        "system_info": system_info,
    })


@app.route("/")
def frontend():
    return render_template("index.html")


def get_cpu_temperatures():
    """Fetch CPU temperatures for Linux, macOS, and Windows."""
    system = platform.system()
    temperatures = []
    if system == "Linux":
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                for temp in temps["coretemp"]:
                    if temp.label.startswith("Core"):
                        temperatures.append(temp.current)
                return round(sum(temperatures) / len(temperatures), 1)  # Average temperature
        except Exception:
            return "N/A"
    elif system == "Windows":
        return "N/A"  # Placeholder for Windows-specific temperature tools
    elif system == "Darwin":  # macOS
        return "N/A"  # Placeholder for macOS-specific temperature tools
    return "N/A"


def get_cpu_name():
    """Get the correct CPU name for Windows, Linux, and macOS."""
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            processor_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return processor_name
        except Exception:
            return platform.processor()
    elif system == "Linux":
        return get_cpu_info().get("brand_raw", platform.processor())
    elif system == "Darwin":  # macOS
        try:
            process = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True)
            return process.stdout.strip()
        except Exception:
            return platform.processor()
    return platform.processor()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)