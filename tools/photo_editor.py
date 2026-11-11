"""
Photo Editor:
- Phone pe photo edit tools
- Crop, rotate, resize, filters
- Screenshot capture + edit
"""

def photo_open_gallery():
    from tools.android_control import open_phone_app
    return open_phone_app("com.google.android.apps.photos")

def photo_take_selfie():
    from tools.android_control import adb
    adb("shell am start -a android.media.action.STILL_IMAGE_CAMERA")
    import time
    time.sleep(2)
    adb("shell input keyevent 27")  # Camera button
    return "Selfie captured!"

def photo_crop(x, y, w, h):
    """Crop using ADB screenshot + local crop"""
    try:
        from tools.android_control import phone_screenshot
        from PIL import Image
        import os

        path = phone_screenshot()
        img = Image.open(path)
        cropped = img.crop((x, y, x+w, y+h))
        out = os.path.join("uploads", "cropped_photo.png")
        cropped.save(out)
        return f"Photo cropped: {out}"
    except Exception as e:
        return f"Crop Error: {e}"

def photo_rotate(degrees=90):
    """Rotate phone screenshot"""
    try:
        from tools.android_control import phone_screenshot
        from PIL import Image
        import os

        path = phone_screenshot()
        img = Image.open(path)
        rotated = img.rotate(-degrees, expand=True)
        out = os.path.join("uploads", "rotated_photo.png")
        rotated.save(out)
        return f"Photo rotated {degrees}°: {out}"
    except Exception as e:
        return f"Rotate Error: {e}"

def photo_resize(width, height):
    """Resize phone screenshot"""
    try:
        from tools.android_control import phone_screenshot
        from PIL import Image
        import os

        path = phone_screenshot()
        img = Image.open(path)
        resized = img.resize((width, height))
        out = os.path.join("uploads", "resized_photo.png")
        resized.save(out)
        return f"Photo resized to {width}x{height}: {out}"
    except Exception as e:
        return f"Resize Error: {e}"

def photo_filter(filter_type="grayscale"):
    """Apply filter to phone screenshot"""
    try:
        from tools.android_control import phone_screenshot
        from PIL import Image, ImageFilter, ImageEnhance
        import os

        path = phone_screenshot()
        img = Image.open(path).convert("RGB")

        if filter_type == "grayscale":
            result = img.convert("L").convert("RGB")
        elif filter_type == "blur":
            result = img.filter(ImageFilter.GaussianBlur(radius=5))
        elif filter_type == "sharpen":
            result = img.filter(ImageFilter.SHARPEN)
        elif filter_type == "bright":
            enhancer = ImageEnhance.Brightness(img)
            result = enhancer.enhance(1.5)
        elif filter_type == "dark":
            enhancer = ImageEnhance.Brightness(img)
            result = enhancer.enhance(0.5)
        elif filter_type == "contrast":
            enhancer = ImageEnhance.Contrast(img)
            result = enhancer.enhance(2.0)
        elif filter_type == "saturation":
            enhancer = ImageEnhance.Color(img)
            result = enhancer.enhance(2.0)
        elif filter_type == "sepia":
            result = img.convert("L").convert("RGB")
            r, g, b = result.split()
            import numpy as np
            arr = np.array(result)
            sepia = np.stack([
                arr * 1.0,
                arr * 0.8,
                arr * 0.6
            ], axis=-1).clip(0, 255).astype("uint8")
            result = Image.fromarray(sepia)
        else:
            result = img

        out = os.path.join("uploads", f"filtered_{filter_type}.png")
        result.save(out)
        return f"Filter '{filter_type}' applied: {out}"
    except Exception as e:
        return f"Filter Error: {e}"

def photo_push_to_phone(pc_path):
    """PC se edited photo phone me wapas bhejo"""
    from tools.android_control import adb
    try:
        adb(f'push "{pc_path}" /sdcard/Download/edited_photo.png')
        return f"Photo pushed to phone: /sdcard/Download/edited_photo.png"
    except Exception as e:
        return f"Push Error: {e}"