"""
Call Recording:
- Phone call record start/stop
- Recording list
- Recording download
"""

from tools.android_control import adb
import os


def call_record_start():
    """Call recording start karo"""
    # Method 1: Use screen recorder (works during calls)
    result = adb("shell screenrecord /sdcard/call_recording.mp4")
    return f"Screen recording started (works during calls)"


def call_record_stop():
    """Recording stop karo"""
    adb("shell pkill -l2 screenrecord")
    return "Recording stopped. File: /sdcard/call_recording.mp4"


def call_record_pull():
    """Recording PC me lao"""
    try:
        os.makedirs("uploads", exist_ok=True)
        adb("pull /sdcard/call_recording.mp4 uploads/call_recording.mp4")
        path = "uploads/call_recording.mp4"
        if os.path.exists(path):
            size = os.path.getsize(path)
            return f"Recording downloaded: {path} ({size // 1024} KB)"
        return "Recording file nahi mili"
    except Exception as e:
        return f"Pull Error: {e}"


def call_record_list():
    """Phone me recordings list karo"""
    result = adb("shell ls -la /sdcard/ | grep -i record")
    if not result or "Error" in result:
        result = adb("shell ls -la /sdcard/Recordings/ 2>/dev/null || ls -la /sdcard/MIUI/sound_recorder/ 2>/dev/null || ls -la /sdcard/")
    return f"Recordings:\n{result[:2000]}"


def call_record_voice_memo(duration=10):
    """Voice memo record karo"""
    import time
    adb(f"shell am start -a android.provider.MediaStore.RECORD_SOUND")
    time.sleep(2)
    adb("shell input keyevent 66")  # Press record
    time.sleep(duration)
    adb("shell input keyevent 66")  # Press stop
    adb("shell input keyevent 4")   # Back
    return f"Voice memo recorded ({duration}s)"