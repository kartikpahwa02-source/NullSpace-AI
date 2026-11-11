import os
import webbrowser
import subprocess
from datetime import datetime

def execute_tool(name, params):

    # === PC TOOLS ===
    if name == "open_youtube":
        webbrowser.open("https://youtube.com")
        return "YouTube open ho gaya"

    elif name == "search_google":
        q = params.get("query", "")
        webbrowser.open(f"https://www.google.com/search?q={q}")
        return f"Google search: {q}"

    elif name == "open_website":
        url = params.get("url", "")
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Website open: {url}"

    elif name == "type_text":
        import pyautogui
        pyautogui.write(params.get("text", ""), interval=0.03)
        return "Text type ho gaya"

    elif name == "take_screenshot":
        import pyautogui
        s = pyautogui.screenshot()
        fn = f"uploads/pc_{datetime.now().strftime('%H%M%S')}.png"
        s.save(fn)
        return f"Screenshot: {fn}"

    elif name == "open_application":
        app = params.get("app_name", "").lower()
        apps = {"notepad": "notepad", "calculator": "calc", "paint": "mspaint",
                "cmd": "cmd", "explorer": "explorer", "chrome": "start chrome"}
        os.system(f"start {apps.get(app, app)}")
        return f"{app} open ho gaya"

    elif name == "run_command":
        cmd = params.get("command", "")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return f"Output:\n{r.stdout or r.stderr or 'Done'}"
        except Exception as e:
            return f"Error: {e}"

    # === BROWSER TOOLS ===
    elif name == "browse_website":
        from tools.browser_auto import browse_open
        return browse_open(params.get("url", ""))

    elif name == "browse_search":
        from tools.browser_auto import browse_search_google
        return browse_search_google(params.get("query", ""))

    elif name == "browse_click":
        from tools.browser_auto import browse_click_text
        return browse_click_text(params.get("text", ""))

    elif name == "browse_type":
        from tools.browser_auto import browse_type_text
        return browse_type_text(params.get("selector", ""), params.get("text", ""))

    elif name == "browse_scroll":
        from tools.browser_auto import browse_scroll
        return browse_scroll(params.get("direction", "down"))

    elif name == "browse_screenshot":
        from tools.browser_auto import browse_screenshot
        return browse_screenshot()

    elif name == "browse_close":
        from tools.browser_auto import close_driver
        close_driver()
        return "Browser band ho gaya"

    # === IMAGE SEARCH ===
    elif name == "image_search":
        from tools.image_search import image_search
        return image_search(params.get("query", ""), int(params.get("num", 5)))

    elif name == "image_download":
        from tools.image_search import image_download
        return image_download(params.get("url", ""), params.get("name", None))

    # === PHONE TOOLS ===
    elif name == "phone_check":
        from tools.android_control import check_device
        return check_device()

    elif name == "phone_open_app":
        from tools.android_control import open_phone_app, get_package
        app = params.get("app_name", "")
        pkg = get_package(app)
        open_phone_app(pkg)
        return f"Phone me {app} open ho gaya"

    elif name == "phone_tap":
        from tools.android_control import phone_tap
        return phone_tap(int(params.get("x", 500)), int(params.get("y", 500)))

    elif name == "phone_type":
        from tools.android_control import phone_type
        return phone_type(params.get("text", ""))

    elif name == "phone_key":
        from tools.android_control import phone_key
        return phone_key(params.get("key", "home"))

    elif name == "phone_screenshot":
        from tools.android_control import phone_screenshot
        return phone_screenshot()

    elif name == "phone_whatsapp":
        from tools.android_control import phone_send_whatsapp
        return phone_send_whatsapp(params.get("number", ""), params.get("message", ""))

    # === PHONE CALLING ===
    elif name == "phone_call":
        from tools.phone_call import phone_call
        return phone_call(params.get("number", ""))

    elif name == "phone_dial":
        from tools.phone_call import phone_dial
        return phone_dial(params.get("number", ""))

    elif name == "phone_send_sms":
        from tools.phone_call import phone_send_sms
        return phone_send_sms(params.get("number", ""), params.get("message", ""))

    elif name == "phone_call_log":
        from tools.phone_call import phone_call_log
        return phone_call_log()

    elif name == "phone_contacts":
        from tools.phone_call import phone_contacts_search
        return phone_contacts_search(params.get("name", ""))

    elif name == "phone_end_call":
        from tools.phone_call import phone_end_call
        return phone_end_call()

    # === PHOTO EDIT ===
    elif name == "photo_gallery":
        from tools.photo_editor import photo_open_gallery
        return photo_open_gallery()

    elif name == "photo_selfie":
        from tools.photo_editor import photo_take_selfie
        return photo_take_selfie()

    elif name == "photo_crop":
        from tools.photo_editor import photo_crop
        return photo_crop(
            int(params.get("x", 100)), int(params.get("y", 100)),
            int(params.get("w", 500)), int(params.get("h", 500))
        )

    elif name == "photo_rotate":
        from tools.photo_editor import photo_rotate
        return photo_rotate(int(params.get("degrees", 90)))

    elif name == "photo_resize":
        from tools.photo_editor import photo_resize
        return photo_resize(int(params.get("width", 800)), int(params.get("height", 600)))

    elif name == "photo_filter":
        from tools.photo_editor import photo_filter
        return photo_filter(params.get("filter_type", "grayscale"))

    # === FILE TRANSFER ===
    elif name == "phone_list_files":
        from tools.file_transfer import phone_list_files
        return phone_list_files(params.get("path", "/sdcard/Download"))

    elif name == "phone_pull_file":
        from tools.file_transfer import phone_pull_file
        return phone_pull_file(params.get("phone_path", ""), params.get("pc_folder", "uploads"))

    elif name == "phone_push_file":
        from tools.file_transfer import phone_push_file
        return phone_push_file(params.get("pc_path", ""), params.get("phone_path", "/sdcard/Download/"))

    elif name == "phone_download":
        from tools.file_transfer import phone_download_file
        return phone_download_file(params.get("url", ""), params.get("name", None))

    elif name == "phone_storage":
        from tools.file_transfer import phone_storage_info
        return phone_storage_info()

    # === CALL RECORDING ===
    elif name == "call_record_start":
        from tools.call_recorder import call_record_start
        return call_record_start()

    elif name == "call_record_stop":
        from tools.call_recorder import call_record_stop
        return call_record_stop()

    elif name == "call_record_pull":
        from tools.call_recorder import call_record_pull
        return call_record_pull()

    elif name == "call_voice_memo":
        from tools.call_recorder import call_record_voice_memo
        return call_record_voice_memo(int(params.get("duration", 10)))

    # === VOICE (Sarvam) ===
    elif name == "voice_speak":
        from voice.voice_engine import text_to_speech
        audio = text_to_speech(
            params.get("text", ""),
            params.get("language", "hi-IN"),
            params.get("speaker", None)
        )
        if audio:
            fn = f"uploads/voice_{datetime.now().strftime('%H%M%S')}.wav"
            with open(fn, "wb") as f:
                f.write(audio)
            return f"Voice: {fn}"
        return "TTS failed"

    elif name == "translate_text":
        from voice.voice_engine import translate_text
        return translate_text(
            params.get("text", ""),
            params.get("source", "en"),
            params.get("target", "hi")
        )

    elif name == "transliterate":
        from voice.voice_engine import transliterate_text
        return transliterate_text(
            params.get("text", ""),
            params.get("source", "en"),
            params.get("target", "hi")
        )

    elif name == "detect_language":
        from voice.voice_engine import detect_language
        return detect_language(params.get("text", ""))

    # === FILE SIGNING ===
    elif name == "create_signature":
        from tools.file_signer import create_signature
        return create_signature(params.get("name", "Nikhil"))

    elif name == "sign_pdf":
        from tools.file_signer import sign_pdf
        return sign_pdf(
            params.get("pdf_path", ""),
            params.get("signature", "uploads/signature.png"),
            params.get("position", "bottom-right")
        )

    elif name == "sign_image":
        from tools.file_signer import sign_image
        return sign_image(
            params.get("image_path", ""),
            params.get("name", "Nikhil"),
            params.get("position", "bottom-right")
        )

    elif name == "sign_text_file":
        from tools.file_signer import sign_text_file
        return sign_text_file(
            params.get("file_path", ""),
            params.get("name", "Nikhil")
        )

    # === IoT ===
    elif name == "iot_list":
        from tools.iot_control import iot_list_devices
        return iot_list_devices()

    elif name == "iot_add":
        from tools.iot_control import iot_add_device
        return iot_add_device(
            params.get("name", ""),
            params.get("device_type", "generic"),
            params.get("ip", ""),
            params.get("protocol", "http")
        )

    elif name == "iot_remove":
        from tools.iot_control import iot_remove_device
        return iot_remove_device(params.get("name", ""))

    elif name == "iot_control":
        from tools.iot_control import iot_control_device
        return iot_control_device(params.get("name", ""), params.get("action", ""))

    elif name == "iot_status":
        from tools.iot_control import iot_status
        return iot_status(params.get("name", ""))

    # === THINKING ===
    elif name == "think":
        from brain.thinking_engine import think_about
        return think_about(params.get("task", ""), params.get("context", ""))

    elif name == "opinion":
        from brain.thinking_engine import form_opinion
        return form_opinion(params.get("topic", ""))

    elif name == "understand":
        from brain.thinking_engine import understand_request
        return understand_request(params.get("message", ""))

    elif name == "learn":
        from brain.thinking_engine import learn_from_interaction
        return learn_from_interaction(
            params.get("task", ""),
            params.get("result", ""),
            params.get("success", True)
        )

    elif name == "suggest":
        from brain.learning_engine import get_smart_suggestions
        return get_smart_suggestions(params.get("cid", "default"))

    elif name == "improve":
        from brain.thinking_engine import suggest_improvements
        return suggest_improvements()

    elif name == "progress":
        from brain.learning_engine import analyze_learning_progress
        return analyze_learning_progress()

    return f"Unknown tool: {name}"