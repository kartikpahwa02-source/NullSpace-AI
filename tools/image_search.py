"""
Image Search:
- Browser me image search karo
- Reverse image search
- Image download
"""

import os
import requests
from datetime import datetime


def image_search(query, num=5):
    """Google image search"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from tools.browser_auto import get_driver
        import time

        d = get_driver()
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch"
        d.get(url)
        time.sleep(3)

        results = []
        images = d.find_elements(By.CSS_SELECTOR, "img.rg_i")[:num]

        for i, img in enumerate(images):
            try:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and src.startswith("http"):
                    results.append({"index": i, "url": src})
            except Exception:
                continue

        if results:
            # Download first image
            first = results[0]
            r = requests.get(first["url"], timeout=10)
            fn = f"uploads/img_{datetime.now().strftime('%H%M%S')}.png"
            with open(fn, "wb") as f:
                f.write(r.content)
            return f"Image search: '{query}'\nFound {len(results)} images\nFirst image saved: {fn}"

        return f"Image search: '{query}'\nBrowser opened, images loading..."

    except Exception as e:
        return f"Image Search Error: {e}"


def image_download(url, save_name=None):
    """Image download karo"""
    try:
        if not save_name:
            save_name = f"img_{datetime.now().strftime('%H%M%S')}.png"

        path = os.path.join("uploads", save_name)
        r = requests.get(url, timeout=10)

        with open(path, "wb") as f:
            f.write(r.content)

        size = os.path.getsize(path)
        return f"Image downloaded: {path} ({size // 1024} KB)"
    except Exception as e:
        return f"Download Error: {e}"


def image_reverse_search(image_path):
    """Reverse image search (Google Lens)"""
    try:
        from tools.browser_auto import browse_open
        import base64

        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()

        # Upload to Google Lens
        browse_open("https://lens.google.com/upload")
        return f"Google Lens opened. Upload image: {image_path}"

    except Exception as e:
        return f"Reverse Search Error: {e}"