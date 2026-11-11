import os

def process_file(path):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            text = ""
            for p in reader.pages[:10]:
                text += p.extract_text() or ""
            return {"type": "pdf", "text": text[:5000], "filename": os.path.basename(path)}
        except Exception as e:
            return {"type": "pdf", "error": str(e)}

    elif ext in [".png", ".jpg", ".jpeg", ".gif"]:
        return {"type": "image", "filename": os.path.basename(path), "path": path}

    elif ext in [".txt", ".py", ".js", ".json", ".csv", ".md", ".html", ".css"]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(5000)
            return {"type": "text", "content": content, "filename": os.path.basename(path)}
        except Exception as e:
            return {"type": "text", "error": str(e)}

    return {"type": "unknown", "filename": os.path.basename(path)}