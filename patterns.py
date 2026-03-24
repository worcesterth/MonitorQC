"""
patterns.py — สร้าง test pattern PNG อัตโนมัติถ้าไม่มีไฟล์จริง
ใช้ Pillow วาด TG270-style luminance patch pattern
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

PATTERN_DIR = os.path.join(os.path.dirname(__file__), "assets", "test_patterns")


def _ensure_dir():
    os.makedirs(PATTERN_DIR, exist_ok=True)


def _get_font(size=14):
    """หา font ที่ใช้ได้ ถ้าไม่มีให้ใช้ default"""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        pass
    return ImageFont.load_default()


# ค่า luminance 18 ช่อง (cd/m²) ตาม TG-270 (log-linear scale)
LUMINANCE_VALUES = [
    1.13, 2.32, 4.02, 5.60, 9.27, 18.32,
    36.58, 72.54, 148.41, 148.41, 72.54, 36.58,
    18.32, 9.27, 5.60, 4.02, 2.32, 1.13,
]

# ค่า grayscale (0–255) สำหรับแต่ละ patch (log-linear)
def _lum_to_gray(lum_val, lum_min=1.13, lum_max=148.41):
    t = (math.log(lum_val) - math.log(lum_min)) / (math.log(lum_max) - math.log(lum_min))
    return int(t * 255)


GRAY_VALUES = [_lum_to_gray(v) for v in LUMINANCE_VALUES]


def make_tg270_luminance(path: str, width=1200, height=800):
    """สร้าง TG270-style luminance patch image"""
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    font_sm = _get_font(14)
    font_md = _get_font(18)
    font_lg = _get_font(22)

    # Title
    draw.text((width // 2, 20), "TG270-QC Luminance Test Pattern",
              fill=(220, 220, 220), font=font_lg, anchor="mt")

    # Grid: 3 rows × 6 cols = 18 patches
    cols, rows = 6, 3
    margin_x, margin_y = 60, 60
    gap = 8
    patch_w = (width - margin_x * 2 - gap * (cols - 1)) // cols
    patch_h = (height - margin_y * 2 - gap * (rows - 1) - 80) // rows

    for i in range(18):
        col = i % cols
        row = i // cols
        x = margin_x + col * (patch_w + gap)
        y = margin_y + 50 + row * (patch_h + gap)

        gray = GRAY_VALUES[i]
        color = (gray, gray, gray)

        # วาด patch
        draw.rectangle([x, y, x + patch_w, y + patch_h], fill=color)

        # วาด line pairs เล็กๆ ที่มุมของ patch
        _draw_line_pairs(draw, x + 4, y + 4, 20, 3, gray)

        # เลข patch และ luminance value
        text_color = (255, 255, 255) if gray < 128 else (0, 0, 0)
        lbl = f"{i+1}\n{LUMINANCE_VALUES[i]:.2f}"
        draw.text((x + patch_w // 2, y + patch_h // 2),
                  lbl, fill=text_color, font=font_sm, anchor="mm", align="center")

    # Border square (มุมซ้ายล่าง)
    bx, by = margin_x, height - margin_y - 40
    draw.rectangle([bx, by, bx + 40, by + 40], fill=(0, 0, 0), outline=(150, 150, 150))

    # Legend
    draw.text((margin_x + 50, height - margin_y - 20),
              "ช่อง 1–9: ความสว่างจากต่ำ→สูง   ช่อง 10–18: ความสว่างจากสูง→ต่ำ",
              fill=(180, 180, 180), font=font_sm)

    img.save(path)
    print(f"[patterns] สร้าง {path}")


def _draw_line_pairs(draw, x, y, size, line_count, bg_gray):
    """วาดกลุ่มเส้นคู่เล็กๆ สำหรับทดสอบ spatial resolution"""
    fg = 255 if bg_gray < 128 else 0
    line_h = size // (line_count * 2)
    if line_h < 1:
        line_h = 1
    for k in range(line_count):
        ly = y + k * line_h * 2
        draw.rectangle([x, ly, x + size, ly + line_h - 1], fill=(fg, fg, fg))


def ensure_patterns():
    """เรียกตอน startup — สร้างรูปที่ยังไม่มีในโฟลเดอร์"""
    _ensure_dir()

    targets = {
        "tg270_luminance.png": make_tg270_luminance,
    }

    for filename, fn in targets.items():
        path = os.path.join(PATTERN_DIR, filename)
        if not os.path.exists(path):
            try:
                fn(path)
            except Exception as e:
                print(f"[patterns] สร้าง {filename} ไม่ได้: {e}")


if __name__ == "__main__":
    ensure_patterns()
    print("Done.")
