from abc import ABC, abstractmethod
from memory.memory import add_task_history, learn


class BaseAgent(ABC):
    def __init__(self, name, desc, icon, color):
        self.name = name; self.desc = desc; self.icon = icon; self.color = color
        self.tasks_done = 0; self.status = "ready"; self.last_task = None

    @abstractmethod
    def can_handle(self, command): pass

    @abstractmethod
    def execute(self, command, params, cid): pass

    def run(self, command, params, cid):
        self.status = "working"; self.last_task = command; self.tasks_done += 1
        try:
            result = self.execute(command, params, cid)
            self.status = "ready"
            add_task_history(f"[{self.name}] {command}", str(result)[:300], True)
            return {"success": True, "agent": self.name, "result": result, "status": "done"}
        except Exception as e:
            self.status = "error"
            return {"success": False, "agent": self.name, "result": f"Error: {e}", "status": "error"}

    def get_status(self):
        return {"name": self.name, "desc": self.desc, "icon": self.icon, "color": self.color, "status": self.status, "tasks_done": self.tasks_done}


class GameAgent(BaseAgent):
    def __init__(self): super().__init__("Game Agent", "PC + Phone games", "🎮", "#ef4444")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["game","khel","play","bgmi","pubg","free fire","minecraft","gta","chess","ludo","subway","temple run","candy crush","clash"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        PG = {"bgmi":"com.pubg.imobile","free fire":"com.dts.freefireth","temple run":"com.imangi.templerun2","subway":"com.kiloo.subwaysurf","candy crush":"com.king.candycrushsaga","clash royale":"com.supercell.clashroyale"}
        BG = {"chess":"https://www.chess.com","ludo":"https://poki.com/en/g/ludo-king"}
        if "phone" in cmd or "mobile" in cmd:
            from tools.android_control import open_phone_app
            for n, pkg in PG.items():
                if n in cmd: open_phone_app(pkg); return f"Phone me {n} khul gaya!"
            return "Kaunsa game? BGMI, Free Fire, Subway, Temple Run"
        for n, url in BG.items():
            if n in cmd:
                from tools.browser_auto import browse_open; browse_open(url); return f"{n} khul gaya!"
        if "bgmi" in cmd:
            from tools.android_control import open_phone_app; open_phone_app("com.pubg.imobile"); return "BGMI khul gaya!"
        if "minecraft" in cmd: import os; os.system("start minecraft:"); return "Minecraft khul gaya!"
        if "gta" in cmd: import os; os.system("start steam://rungameid/271590"); return "GTA khul gaya!"
        return "Games: BGMI, Minecraft, GTA, Chess, Free Fire, Subway"


class CommunicationAgent(BaseAgent):
    def __init__(self): super().__init__("Communication Agent", "WhatsApp, SMS, Messages", "💬", "#22c55e")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["whatsapp","message","bhejo","bhej","sms","telegram","dm"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "whatsapp" in cmd:
            if "open" in cmd or "kholo" in cmd:
                from tools.android_control import open_phone_app, get_package; open_phone_app(get_package("whatsapp")); return "WhatsApp khul gaya!"
            n = p.get("number",""); m = p.get("message","")
            if not n or not m: return "Number aur message batao. Example: 'WhatsApp pe bhejo 919999999999 message: Hello'"
            from tools.android_control import phone_send_whatsapp; return phone_send_whatsapp(n, m)
        if "sms" in cmd:
            n = p.get("number",""); m = p.get("message","")
            if not n or not m: return "Number aur message batao."
            from tools.phone_caller import send_sms; return send_sms(n, m)
        if "telegram" in cmd:
            from tools.android_control import open_phone_app; open_phone_app("org.telegram.messenger"); return "Telegram khul gaya!"
        return "WhatsApp message, SMS, Telegram"


class PhoneAgent(BaseAgent):
    def __init__(self): super().__init__("Phone Agent", "Android phone control", "📱", "#a855f7")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["phone","mobile","android","phone screenshot","phone gallery","phone file","phone storage"]) and "call" not in c.lower() and "whatsapp" not in c.lower()
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "check" in cmd or "device" in cmd:
            from tools.android_control import check_device; return check_device()
        if "open" in cmd or "kholo" in cmd or "khol" in cmd:
            from tools.android_control import open_phone_app, get_package
            app = p.get("app_name","")
            if not app:
                for a in ["youtube","instagram","chrome","camera","settings","bgmi","spotify","gmail","maps"]:
                    if a in cmd: app = a; break
            if app: open_phone_app(get_package(app)); return f"Phone me {app} khul gaya!"
            return "Kaunsa app kholna hai?"
        if "screenshot" in cmd:
            from tools.android_control import phone_screenshot; return phone_screenshot()
        if "home" in cmd:
            from tools.android_control import phone_key; return phone_key("home")
        if "back" in cmd:
            from tools.android_control import phone_key; return phone_key("back")
        if "gallery" in cmd:
            from tools.file_downloader import list_gallery; return list_gallery()
        if "storage" in cmd:
            from tools.file_downloader import phone_storage_info; return phone_storage_info()
        if "file" in cmd:
            from tools.file_downloader import list_phone_files; return list_phone_files("/sdcard/Download")
        if "download" in cmd:
            pp = p.get("phone_path","")
            if not pp: from tools.file_downloader import list_downloads; return list_downloads()
            from tools.file_downloader import download_file; return download_file(pp)
        return "Phone check, App open, Screenshot, Gallery, Files, Storage"


class PhotoAgent(BaseAgent):
    def __init__(self): super().__init__("Photo Agent", "Photo edit, filter, search", "📸", "#14b8a6")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["photo","filter","crop","resize","watermark","image search","image download"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "search" in cmd:
            from tools.image_search import image_search_google; return image_search_google(p.get("query", c))
        if "download" in cmd and "image" in cmd:
            from tools.image_search import image_search_download; return image_search_download()
        if "list" in cmd or "photos" in cmd:
            from tools.photo_editor import photo_list; return photo_list()
        if "editor" in cmd:
            from tools.photo_editor import photo_open_editor; return photo_open_editor()
        if "filter" in cmd:
            path = p.get("path",""); ft = "grayscale"
            for f in ["grayscale","blur","sharpen","bright","dark","contrast","sepia"]:
                if f in cmd: ft = f; break
            if not path: return f"Photo path batao. Example: 'photo me {ft} filter lagao uploads/photo.jpg'"
            from tools.photo_editor import photo_filter; return photo_filter(path, ft)
        if "resize" in cmd:
            path = p.get("path","")
            if not path: return "Photo path batao."
            from tools.photo_editor import photo_resize; return photo_resize(path, int(p.get("width",800)), int(p.get("height",600)))
        if "watermark" in cmd:
            from tools.signature_tool import add_watermark; return add_watermark(p.get("text","EmptySpace AI"))
        if "signature" in cmd:
            from tools.signature_tool import create_signature; return create_signature(p.get("name","Nikhil"))
        return "Image search, Filter, Resize, Watermark, Signature, Editor"


class SmartHomeAgent(BaseAgent):
    def __init__(self): super().__init__("SmartHome Agent", "Smart home devices", "🏠", "#06b6d4")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["light","fan","ac ","room","smart","scene","movie","sleep","temperature"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "list" in cmd or "device" in cmd:
            from tools.smart_home import list_devices; return list_devices()
        if "light" in cmd:
            dev = "bedroom_light" if "bed" in cmd else "living_room_light"
            if "on" in cmd or "jalao" in cmd: from tools.smart_home import light_on; return light_on(dev)
            elif "off" in cmd or "bujhao" in cmd: from tools.smart_home import light_off; return light_off(dev)
        if "fan" in cmd:
            dev = "bedroom_fan"; sp = 3
            if "1" in cmd: sp = 1
            elif "2" in cmd: sp = 2
            if "on" in cmd: from tools.smart_home import fan_on; return fan_on(dev, sp)
            elif "off" in cmd: from tools.smart_home import fan_off; return fan_off(dev)
        if "ac" in cmd:
            import re; temp = 24
            m = re.search(r'(\d{2})\s*(?:degree|deg)', cmd)
            if m: temp = int(m.group(1))
            if "on" in cmd: from tools.smart_home import ac_on; return ac_on("ac", temp)
            elif "off" in cmd: from tools.smart_home import ac_off; return ac_off("ac")
        if "scene" in cmd or "movie" in cmd or "sleep" in cmd:
            scene = "sleep" if "sleep" in cmd else "movie"
            from tools.smart_home import smart_home_scene; return smart_home_scene(scene)
        return "Devices, Light, Fan, AC, Scene"


class AutomationAgent(BaseAgent):
    def __init__(self): super().__init__("Automation Agent", "PC apps, typing", "⚙️", "#22c55e")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["open","kholo","khol","type","likho","screenshot","notepad","calculator","paint","cmd","explorer","chrome"]) and "phone" not in c.lower()
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "youtube" in cmd: from tools.executor import execute_tool as et; return et("open_youtube",{})
        if "google" in cmd and ("search" in cmd or "karo" in cmd): from tools.executor import execute_tool as et; return et("search_google",{"query":c})
        if "screenshot" in cmd: from tools.executor import execute_tool as et; return et("take_screenshot",{})
        if "type" in cmd or "likho" in cmd:
            t = p.get("text",""); 
            if not t: return "Kya type karna hai?"
            from tools.executor import execute_tool as et; return et("type_text",{"text":t})
        if "open" in cmd or "kholo" in cmd or "khol" in cmd:
            app = p.get("app_name","")
            am = {"notepad":"notepad","calculator":"calc","paint":"mspaint","cmd":"cmd","explorer":"explorer","chrome":"start chrome"}
            if not app:
                for n in am:
                    if n in cmd: app = n; break
            if app: from tools.executor import execute_tool as et; return et("open_application",{"app_name":app})
        return "YouTube, Google, Screenshot, Type, App open"


class CallAgent(BaseAgent):
    def __init__(self): super().__init__("Call Agent", "Phone calls, SMS", "📞", "#f97316")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["call","ring","dial","uthao","cut karo","end call","call log","contact"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "call log" in cmd or "recent" in cmd: from tools.phone_caller import call_logs; return call_logs()
        if "contact" in cmd: from tools.phone_caller import open_contacts; return open_contacts()
        if "dialer" in cmd: from tools.phone_caller import open_dialer; return open_dialer()
        if "end" in cmd or "cut" in cmd: from tools.phone_caller import end_call; return end_call()
        if "answer" in cmd or "uthao" in cmd: from tools.phone_caller import answer_call; return answer_call()
        n = p.get("number","")
        if not n: from tools.phone_caller import open_dialer; return open_dialer()
        from tools.phone_caller import make_call; return make_call(n)


class RecordAgent(BaseAgent):
    def __init__(self): super().__init__("Record Agent", "Screen/Audio recording", "🔴", "#dc2626")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["record","recording","screen record","voice memo"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "start" in cmd: from tools.call_recorder import start_recording; return start_recording()
        if "stop" in cmd: from tools.call_recorder import stop_recording; return stop_recording()
        if "list" in cmd: from tools.call_recorder import list_recordings; return list_recordings()
        if "download" in cmd: from tools.call_recorder import download_recording; return download_recording()
        return "Recording start/stop/list/download"


class ResearchAgent(BaseAgent):
    def __init__(self): super().__init__("Research Agent", "Internet research", "🔍", "#3b82f6")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["research","dhundho","pata karo","news","latest","information"])
    def execute(self, c, p, cid):
        q = p.get("query", c)
        from tools.web_scraper import search_web
        from brain.llm import ask_llm_direct
        r = search_web(q, num=5)
        st = ""
        for i, x in enumerate(r, 1): st += f"{i}. {x['title']}\n   {x['snippet']}\n\n"
        return f"Research: {q}\n\n{ask_llm_direct(f'Summarize: {st[:2000]}. Hindi/Hinglish.')}"


class FileAgentClass(BaseAgent):
    def __init__(self): super().__init__("File Agent", "File upload + analysis", "📄", "#f59e0b")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["file","pdf","document","analyze","upload","read file"]) and "phone" not in c.lower()
    def execute(self, c, p, cid):
        from memory.memory import get_file_info
        fi = get_file_info(cid)
        if not fi or "path" not in fi: return "Pehle file upload karo."
        from agents.file_agent import analyze_uploaded_file
        return analyze_uploaded_file(fi["path"], c)


class BrowserAgentClass(BaseAgent):
    def __init__(self): super().__init__("Browser Agent", "Browser automation", "🌐", "#6366f1")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["browser","browse","navigate","wikipedia","website me jao"])
    def execute(self, c, p, cid):
        from agents.browser_agent import run_browser_task
        return run_browser_task(c)


class CodeAgent(BaseAgent):
    def __init__(self): super().__init__("Code Agent", "Code likhta hai, run karta hai", "💻", "#8b5cf6")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["code","program","script","write code","python","run code","debug","fix code","coding"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "history" in cmd: from tools.code_runner import show_code_history; return show_code_history()
        if "fix" in cmd or "debug" in cmd:
            co = p.get("code",""); er = p.get("error","")
            if co and er: from tools.code_runner import fix_code; return fix_code(co, er)
            return "Code aur error dono batao."
        purpose = p.get("purpose", c)
        from tools.code_runner import run_purpose_code; return run_purpose_code(purpose)


class SystemAgent(BaseAgent):
    def __init__(self): super().__init__("System Agent", "PC system control", "🖥️", "#0ea5e9")
    def can_handle(self, c):
        return any(k in c.lower() for k in ["system","cpu","ram","process","network","wifi","port","startup","pc info","disk","performance"])
    def execute(self, c, p, cid):
        cmd = c.lower()
        if "info" in cmd or "system" in cmd or "pc" in cmd: from tools.system_control import get_system_info; return get_system_info()
        if "process" in cmd:
            if "kill" in cmd:
                pid = p.get("pid","")
                if pid: from tools.system_control import kill_process; return kill_process(pid)
                return "PID batao."
            from tools.system_control import list_processes; return list_processes()
        if "network" in cmd: from tools.system_control import run_network_scan; return run_network_scan()
        if "wifi" in cmd: from tools.system_control import get_wifi_passwords; return get_wifi_passwords()
        if "port" in cmd: from tools.system_control import open_port_scan; return open_port_scan()
        if "startup" in cmd: from tools.system_control import manage_startup; return manage_startup()
        return "System info, Processes, Network, WiFi, Ports, Startup"