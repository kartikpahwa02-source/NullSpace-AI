"""
File Downloader — Phone se files PC me lao
"""

import subprocess
import os
from config.settings import ADB_PATH


def adb(cmd):
    try:
        r = subprocess.run(
            f"{ADB_PATH} {cmd}",
            shell=True, capture_output=True, text=True, timeout=30
        )
        return r.stdout.strip() or r.stderr.strip() or "Done"
    except Exception as e:
        return f"Error: {e}"


def list_phone_files(path="/sdcard/Download"):
    """Phone me files list karo"""
    result = adb(f"shell ls -la {path}")
    return f"Files in {path}:\n{result[:2000]}"


def download_file(phone_path, local_name=None):
    """Phone se file PC me download karo"""
    if not local_name:
        local_name = os.path.basename(phone_path)

    local_path = os.path.join("uploads", local_name)
    adb(f'pull "{phone_path}" "{local_path}"')

    if os.path.exists(local_path):
        size = os.path.getsize(local_path)
        return f"Downloaded: {local_path} ({size//1024} KB)"
    return f"Download failed: {phone_path}"


def upload_file_to_phone(local_path, phone_path="/sdcard/Download/"):
    """PC se file phone me upload karo"""
    fname = os.path.basename(local_path)
    adb(f'push "{local_path}" "{phone_path}{fname}"')
    return f"Uploaded to phone: {phone_path}{fname}"


def list_downloads():
    """Phone Downloads folder dekho"""
    return list_phone_files("/sdcard/Download")


def list_gallery():
    """Phone Gallery dekho"""
    return list_phone_files("/sdcard/DCIM/Camera")


def list_documents():
    """Phone Documents dekho"""
    return list_phone_files("/sdcard/Documents")


def search_phone_file(name):
    """Phone me file search karo"""
    result = adb(f'shell find /sdcard -name "*{name}*" -type f 2>/dev/null | head -20')
    if result:
        return f"Found files:\n{result}"
    return f"No file found with name: {name}"


def phone_storage_info():
    """Phone storage info dekho"""
    result = adb("shell df /sdcard")
    return f"Phone Storage:\n{result}"


def delete_phone_file(path):
    """Phone se file delete karo"""
    adb(f'shell rm "{path}"')
    return f"Deleted: {path}"