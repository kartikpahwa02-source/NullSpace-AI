TOOLS = {
    # PC
    "open_youtube":       {"desc": "YouTube kholo", "risk": "low", "cat": "pc"},
    "search_google":      {"desc": "Google search", "risk": "low", "cat": "pc"},
    "open_website":       {"desc": "Website kholo", "risk": "low", "cat": "pc"},
    "type_text":          {"desc": "Screen pe type karo", "risk": "medium", "cat": "pc"},
    "take_screenshot":    {"desc": "Screenshot lo", "risk": "low", "cat": "pc"},
    "open_application":   {"desc": "PC app kholo", "risk": "medium", "cat": "pc"},
    "run_command":        {"desc": "System command (DANGEROUS)", "risk": "high", "cat": "pc"},

    # Browser
    "browse_website":     {"desc": "Browser me website", "risk": "low", "cat": "browser"},
    "browse_search":      {"desc": "Browser me Google", "risk": "low", "cat": "browser"},
    "browse_click":       {"desc": "Browser me click", "risk": "medium", "cat": "browser"},
    "browse_type":        {"desc": "Browser me type", "risk": "medium", "cat": "browser"},
    "browse_scroll":      {"desc": "Browser scroll", "risk": "low", "cat": "browser"},
    "browse_screenshot":  {"desc": "Browser screenshot", "risk": "low", "cat": "browser"},
    "browse_close":       {"desc": "Browser band karo", "risk": "low", "cat": "browser"},

    # Image Search
    "image_search":       {"desc": "Browser me image search", "risk": "low", "cat": "browser"},
    "image_download":     {"desc": "Image download karo", "risk": "low", "cat": "browser"},

    # Phone
    "phone_check":        {"desc": "Phone connected?", "risk": "low", "cat": "phone"},
    "phone_open_app":     {"desc": "Phone app kholo", "risk": "medium", "cat": "phone"},
    "phone_tap":          {"desc": "Phone tap karo", "risk": "medium", "cat": "phone"},
    "phone_type":         {"desc": "Phone me type", "risk": "medium", "cat": "phone"},
    "phone_key":          {"desc": "Phone key press", "risk": "low", "cat": "phone"},
    "phone_screenshot":   {"desc": "Phone screenshot", "risk": "low", "cat": "phone"},
    "phone_whatsapp":     {"desc": "WhatsApp message", "risk": "medium", "cat": "phone"},

    # Phone Calling
    "phone_call":         {"desc": "Phone call karo", "risk": "medium", "cat": "phone"},
    "phone_dial":         {"desc": "Number dial karo", "risk": "low", "cat": "phone"},
    "phone_send_sms":     {"desc": "SMS bhejo", "risk": "medium", "cat": "phone"},
    "phone_call_log":     {"desc": "Call log dekho", "risk": "low", "cat": "phone"},
    "phone_contacts":     {"desc": "Contact search", "risk": "low", "cat": "phone"},
    "phone_end_call":     {"desc": "Call end karo", "risk": "medium", "cat": "phone"},

    # Photo Edit
    "photo_gallery":      {"desc": "Phone gallery kholo", "risk": "low", "cat": "phone"},
    "photo_selfie":       {"desc": "Selfie lo", "risk": "low", "cat": "phone"},
    "photo_crop":         {"desc": "Photo crop karo", "risk": "low", "cat": "phone"},
    "photo_rotate":       {"desc": "Photo rotate karo", "risk": "low", "cat": "phone"},
    "photo_resize":       {"desc": "Photo resize karo", "risk": "low", "cat": "phone"},
    "photo_filter":       {"desc": "Photo filter lagao", "risk": "low", "cat": "phone"},

    # File Transfer
    "phone_list_files":   {"desc": "Phone files list", "risk": "low", "cat": "phone"},
    "phone_pull_file":    {"desc": "Phone se file lao", "risk": "medium", "cat": "phone"},
    "phone_push_file":    {"desc": "Phone pe file bhejo", "risk": "medium", "cat": "phone"},
    "phone_download":     {"desc": "Phone pe download", "risk": "low", "cat": "phone"},
    "phone_storage":      {"desc": "Phone storage info", "risk": "low", "cat": "phone"},

    # Call Recording
    "call_record_start":  {"desc": "Call recording start", "risk": "medium", "cat": "phone"},
    "call_record_stop":   {"desc": "Call recording stop", "risk": "low", "cat": "phone"},
    "call_record_pull":   {"desc": "Recording PC me lao", "risk": "medium", "cat": "phone"},
    "call_voice_memo":    {"desc": "Voice memo record", "risk": "low", "cat": "phone"},

    # Voice / Sarvam
    "voice_speak":        {"desc": "Voice me sunao (Sarvam)", "risk": "low", "cat": "voice"},
    "translate_text":     {"desc": "Translate karo", "risk": "low", "cat": "voice"},
    "transliterate":      {"desc": "Transliterate karo", "risk": "low", "cat": "voice"},
    "detect_language":    {"desc": "Language detect", "risk": "low", "cat": "voice"},

    # Research
    "research_topic":     {"desc": "Internet research", "risk": "low", "cat": "research"},

    # File
    "analyze_file":       {"desc": "File analyze karo", "risk": "low", "cat": "file"},
    "sign_pdf":           {"desc": "PDF pe signature", "risk": "low", "cat": "file"},
    "sign_image":         {"desc": "Image pe signature", "risk": "low", "cat": "file"},
    "sign_text_file":     {"desc": "Text file sign", "risk": "low", "cat": "file"},
    "create_signature":   {"desc": "Signature banao", "risk": "low", "cat": "file"},

    # IoT
    "iot_list":           {"desc": "IoT devices list", "risk": "low", "cat": "iot"},
    "iot_add":            {"desc": "IoT device add", "risk": "low", "cat": "iot"},
    "iot_remove":         {"desc": "IoT device remove", "risk": "low", "cat": "iot"},
    "iot_control":        {"desc": "IoT device control", "risk": "medium", "cat": "iot"},
    "iot_status":         {"desc": "IoT device status", "risk": "low", "cat": "iot"},

    # Thinking
    "think":              {"desc": "AI khud sochega", "risk": "low", "cat": "think"},
    "opinion":            {"desc": "AI apna opinion dega", "risk": "low", "cat": "think"},
    "understand":         {"desc": "AI samjhega request", "risk": "low", "cat": "think"},
    "learn":              {"desc": "AI seekhega", "risk": "low", "cat": "think"},
    "suggest":            {"desc": "AI suggestions dega", "risk": "low", "cat": "think"},
    "improve":            {"desc": "AI improvements suggest karega", "risk": "low", "cat": "think"},
    "progress":           {"desc": "Learning progress dekho", "risk": "low", "cat": "think"},

    # Autonomous
    "autonomous_task":    {"desc": "Complex task auto execute", "risk": "medium", "cat": "auto"},
}

def tools_text():
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}: {info['desc']} [{info['cat']}] risk:{info['risk']}")
    return "\n".join(lines)