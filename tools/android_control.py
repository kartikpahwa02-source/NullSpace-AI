import subprocess
from config.settings import ADB_PATH

def adb(cmd):
    try:
        r = subprocess.run(f"{ADB_PATH} {cmd}", shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() or r.stderr.strip() or "Done"
    except Exception as e:
        return f"ADB Error: {e}"

def check_device():
    out = adb("devices")
    lines = [l for l in out.split("\n") if "\tdevice" in l]
    if lines:
        return f"Device connected: {len(lines)}"
    return "No device found. USB debugging ON karo."

def open_phone_app(package):
    return adb(f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1")

def phone_tap(x, y):
    return adb(f"shell input tap {x} {y}")

def phone_type(text):
    safe = text.replace(" ", "%s").replace("'", "").replace('"', "")
    return adb(f'shell input text "{safe}"')

def phone_key(key):
    keys = {"home": "3", "back": "4", "enter": "66", "power": "26",
            "volume_up": "24", "volume_down": "25", "menu": "82"}
    code = keys.get(key.lower(), key)
    return adb(f"shell input keyevent {code}")

def phone_screenshot():
    adb("shell screencap -p /sdcard/es_screen.png")
    adb("pull /sdcard/es_screen.png uploads/phone_screenshot.png")
    return "uploads/phone_screenshot.png"

def phone_send_whatsapp(number, message):
    msg = message.replace(" ", "%20")
    return adb(f'shell am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone={number}&text={msg}"')

def list_installed_apps():
    return adb("shell pm list packages -3")

APP_PACKAGES = {
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "bgmi": "com.pubg.imobile",
    "spotify": "com.spotify.music",
    "telegram": "org.telegram.messenger",
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "gmail": "com.google.android.gm",
    "maps": "com.google.android.apps.maps",
    "phone": "com.android.dialer",
    "messages": "com.google.android.apps.messaging",
    "gallery": "com.google.android.apps.photos",
    "playstore": "com.android.vending",
    "twitter": "com.twitter.android",
    "facebook": "com.facebook.katana",
    "snapchat": "com.snapchat.android",
    "paytm": "net.one97.paytm",
    "phonepe": "com.phonepe.app",
}

def get_package(name):
    return APP_PACKAGES.get(name.lower(), name)