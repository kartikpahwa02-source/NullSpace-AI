"""
Signature Tool — PDF/Document me signature add karo
"""

import os
from datetime import datetime


def create_signature(name, output_path=None):
    """Digital signature image banao"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        if not output_path:
            output_path = f"uploads/signature_{datetime.now().strftime('%H%M%S')}.png"

        # Create transparent image
        img = Image.new("RGBA", (400, 150), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Try to use a cursive-style font
        try:
            font = ImageFont.truetype("ariali.ttf", 50)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 50)
            except Exception:
                font = ImageFont.load_default()

        # Draw signature
        draw.text((20, 40), name, fill=(0, 0, 139), font=font)

        # Draw underline
        draw.line([(20, 100), (380, 100)], fill=(0, 0, 139), width=2)

        img.save(output_path)
        return f"Signature created: {output_path}"

    except Exception as e:
        return f"Signature Error: {e}"


def add_signature_to_pdf(pdf_path, signature_path, page_num=0, x=100, y=700):
    """PDF me signature add karo"""
    try:
        from PyPDF2 import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io

        # Create signature overlay
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.drawImage(signature_path, x, y, width=200, height=75)
        c.save()
        packet.seek(0)

        # Read original PDF
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Read signature overlay
        sig_reader = PdfReader(packet)

        for i, page in enumerate(reader.pages):
            if i == page_num:
                page.merge_page(sig_reader.pages[0])
            writer.add_page(page)

        # Save
        out_path = pdf_path.replace(".pdf", "_signed.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)

        return f"Signature added: {out_path}"

    except ImportError:
        return "Install reportlab: pip install reportlab"
    except Exception as e:
        return f"PDF Sign Error: {e}"


def add_watermark(text, output_path=None):
    """Watermark banao"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        if not output_path:
            output_path = f"uploads/watermark_{datetime.now().strftime('%H%M%S')}.png"

        img = Image.new("RGBA", (500, 500), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except Exception:
            font = ImageFont.load_default()

        draw.text((50, 200), text, fill=(128, 128, 128, 128), font=font)

        img.save(output_path)
        return f"Watermark created: {output_path}"

    except Exception as e:
        return f"Watermark Error: {e}"


def add_signature_to_image(image_path, signature_path, position="bottom-right"):
    """Image me signature add karo"""
    try:
        from PIL import Image

        img = Image.open(image_path).convert("RGBA")
        sig = Image.open(signature_path).convert("RGBA")

        # Resize signature
        sig = sig.resize((200, 75))

        if position == "bottom-right":
            pos = (img.width - sig.width - 20, img.height - sig.height - 20)
        elif position == "bottom-left":
            pos = (20, img.height - sig.height - 20)
        elif position == "top-right":
            pos = (img.width - sig.width - 20, 20)
        else:
            pos = (20, 20)

        img.paste(sig, pos, sig)

        out = image_path.replace(".", "_signed.")
        img.save(out)
        return f"Signature added to image: {out}"

    except Exception as e:
        return f"Image Sign Error: {e}"