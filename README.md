# TG270 Monitor QC System

ระบบประเมินคุณภาพจอภาพทางการแพทย์ตามมาตรฐาน **AAPM TG-270** รองรับ 4 ชนิดหน้าจอ ครอบคลุมทุกรอบการประเมิน บันทึกผลลงฐานข้อมูล และสร้างรายงาน PDF/Excel

**ภาควิชารังสีเทคนิค คณะสหเวชศาสตร์ มหาวิทยาลัยนเรศวร**

---

## ทีมผู้พัฒนา

**ที่ปรึกษา**
- ผู้ช่วยศาสตราจารย์ ดร.ธัญรัตน์ ชูศิลป์
- ผู้ช่วยศาสตราจารย์ ดร.สุธาสินี ฉิมเล็ก

**ผู้พัฒนาระบบ**
- นางสาวชำนิกานต์ แก้วนา
- นายภาณุวิชญ์ จันเสนา
- นายณัฐวุฒิ โรจน์บุณถึง
- นายอธิวัฒน์ ยศปัญญา
- นางสาววรฤทัย มหาวงษ์

**ติดต่อ:** thunyarutc@nu.ac.th · chumnikarnk66@nu.ac.th · panuwitj66@nu.ac.th

---

## Tech Stack

| ส่วน | รายละเอียด |
|------|-----------|
| ภาษา | Python 3.11 |
| GUI | Tkinter (built-in) |
| รูปภาพ | Pillow (PIL) |
| PDF รายงาน | ReportLab + THSarabunNew.ttf |
| PDF คู่มือ | Playwright (Chromium) + pypdf |
| Excel | openpyxl |
| ฐานข้อมูล | SQLite (`data/screenqc.db`) |
| Build | PyInstaller (onefile) — Windows EXE & macOS .app |
| CI/CD | GitHub Actions (push → main → build artifacts) |

---

## วิธีรันโปรแกรม

```bash
# ติดตั้ง dependencies
pip install pillow reportlab openpyxl

# รัน
python main.py
```

---

## โครงสร้างไฟล์

```
Desktop1QC/
├── main.py              # Entry point — ติดตั้งฟอนต์ไทย, สร้าง Tk window, ลงทะเบียน screens
├── config.py            # TEST_CONFIG, SCREEN_TYPES, PERIODS, PERIOD_LABELS
├── database.py          # SQLite ORM-like: init_db, users, evaluations, answers
├── patterns.py          # สร้าง test pattern image แบบ fallback ด้วย Pillow
│
├── screens/
│   ├── base.py          # BaseScreen, color constants, thai_font(), rich_label(), helpers
│   ├── home.py          # หน้าแรก (โลโก้ + ปุ่มนำทาง + popup ทีมผู้พัฒนา/เอกสารอ้างอิง)
│   ├── select_type.py   # เลือกชนิดหน้าจอ (4 แบบ พร้อมรูปและ popup นิยาม)
│   ├── select_period.py # เลือกรอบการประเมิน (พร้อม color bar แสดงสี period)
│   ├── login.py         # ล็อกอิน + แสดงข้อมูลโรงพยาบาล/หน้าจอ (color bar ตาม period)
│   ├── confirm.py       # ยืนยัน metadata ก่อนเริ่มทดสอบ (color bar ตาม period)
│   ├── instructions.py  # คำแนะนำก่อนทดสอบ (warm-up, ระยะดู, ทำความสะอาด)
│   ├── test_runner.py   # หน้าทำข้อสอบ — แสดงรูป, ตอบ yes/no, ระบุช่องที่ fail
│   ├── results.py       # ตารางผลการประเมิน (pass/fail รายข้อ) — Canvas-based
│   ├── after_save.py    # สรุปหลังบันทึก — ตั้ง baseline, พิมพ์, ดูเกณฑ์
│   ├── criteria.py      # ตารางเกณฑ์การประเมินและวิธีแก้ไข (กรองตามชนิดหน้าจอ)
│   ├── comparison.py    # เปรียบเทียบผลกับ baseline — export PDF
│   ├── history.py       # ค้นหาประวัติการประเมิน (filter วันที่, ชนิดหน้าจอ)
│   ├── history_result.py# ดูผลการประเมินในอดีต (Canvas-based)
│   ├── register.py      # ตั้งค่าครั้งแรก (ชื่อโรงพยาบาล, รุ่นหน้าจอ, สร้าง user แรก)
│   └── user_list.py     # จัดการผู้ใช้ (เพิ่ม/แก้ไข/ลบ)
│
├── assets/
│   ├── fonts/THSarabunNew.ttf   # ฟอนต์ไทย (bundled)
│   ├── logo/                    # โลโก้แอปและโลโก้มหาวิทยาลัย (.png, .icns, .ico)
│   ├── display/                 # รูปประกอบชนิดหน้าจอ 4 แบบ
│   └── test_patterns/           # รูปแบบทดสอบ (PNG/TIFF)
│
├── reports/
│   └── pdf_export.py    # สร้าง PDF รายงานการประเมินด้วย ReportLab (landscape A4)
│
├── manual/
│   ├── manual.md        # ต้นฉบับคู่มือภาษาไทย (Markdown)
│   ├── build_custom.py  # สร้าง PDF คู่มือ (Playwright + NU branding สี #F58220/#A7A9AC)
│   ├── capture_screens.py # แคปภาพหน้าจอแอปจริงสำหรับคู่มือ (PIL ImageGrab)
│   ├── shots/           # ภาพหน้าจอ 11 รูป (01-home.png ถึง 11-history-result.png)
│   └── คู่มือการใช้งาน-TG270.pdf  # PDF คู่มือ 22 หน้า
│
├── scripts/
│   └── create_ico.py    # แปลง PNG → ICO สำหรับ Windows
│
└── data/
    └── screenqc.db      # SQLite database (สร้างอัตโนมัติเมื่อรันครั้งแรก)
```

---

## config.py — โครงสร้างข้อมูลหลัก

### ชนิดหน้าจอ (`SCREEN_TYPES`)
| key | ความหมาย |
|-----|----------|
| `diagnostic` | หน้าจอชนิดใช้วินิจฉัยทางการแพทย์ (Diagnostic display) |
| `modality` | หน้าจอชนิดใช้แสดงทางการแพทย์ (Modality display) |
| `clinic` | หน้าจอตรวจทานทางการแพทย์ (Clinical Review display) |
| `ehr` | หน้าจอสำหรับงานเวชระเบียน (Electronic Health Record) |

### รอบการประเมิน (`PERIODS`)
| ชนิดหน้าจอ | รอบที่รองรับ |
|-----------|------------|
| diagnostic | monthly, quarterly |
| modality | monthly, quarterly, annual |
| clinic | annual |
| ehr | annual |

### `TEST_CONFIG` — โครงสร้างแต่ละ test item
```python
{
    "item_id":        "diag_lum_patches_m",      # unique ID สำหรับบันทึก DB
    "title":          "1.1) การประเมิน...",       # หัวข้อที่แสดงในหน้าทดสอบ
    "criteria_title": "1.1) ...",                 # หัวข้อที่แสดงในหน้า comparison
    "image_index":    1,                           # ชี้ไปยัง assets/test_patterns/
    "question_type":  "yes_no",                   # ดูตารางด้านล่าง
    "total_channels": 18,                          # (เฉพาะ yes_no_channels)
    "pass_criterion": "...",                       # เกณฑ์ผ่าน (รองรับ <u>text</u>)
    "fix_guide":      "...",                       # วิธีแก้ไขกรณีไม่ผ่าน
    "cmp_drift":      "A",                         # A หรือ B (ประเภทการเปรียบเทียบ)
}
```

**`question_type` ที่รองรับ:**
| ค่า | การแสดงผล |
|-----|----------|
| `yes_no` | ปุ่ม ผ่าน / ไม่ผ่าน |
| `yes_no_channels` | ปุ่ม ผ่าน / ไม่ผ่าน + checkbox ระบุช่องที่ fail (กำหนดจำนวนด้วย `total_channels`) |
| `yes_no_channels_text` | ปุ่ม ผ่าน / ไม่ผ่าน + text field ระบุช่องหรือช่วงที่ fail (เช่น `2-23, 34, 50`) |

---

## Database Schema

```sql
-- ข้อมูลโรงพยาบาล/หน้าจอ (1 row)
CREATE TABLE settings (
    id            INTEGER PRIMARY KEY,
    hospital_name TEXT NOT NULL,
    screen_model  TEXT NOT NULL
);

-- ผู้ใช้งาน
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    lastname TEXT NOT NULL DEFAULT '',
    password TEXT NOT NULL
);

-- บันทึกการประเมินแต่ละครั้ง
CREATE TABLE evaluations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_name   TEXT    NOT NULL,
    evaluator_name  TEXT    NOT NULL,
    screen_model    TEXT    NOT NULL,
    screen_type     TEXT    NOT NULL,  -- diagnostic / modality / clinic / ehr
    period          TEXT    NOT NULL,  -- monthly / quarterly / annual
    eval_datetime   TEXT    NOT NULL,
    overall_pass    INTEGER NOT NULL,  -- 1=ผ่าน, 0=ไม่ผ่าน
    is_baseline     INTEGER NOT NULL DEFAULT 0
);

-- คำตอบรายข้อ
CREATE TABLE answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id   INTEGER NOT NULL REFERENCES evaluations(id),
    item_id         TEXT    NOT NULL,
    passed          INTEGER NOT NULL,
    failed_channels TEXT    NOT NULL DEFAULT '[]',  -- JSON array
    notes           TEXT    NOT NULL DEFAULT ''
);
```

**ตำแหน่ง DB:**
- Dev: `<project>/data/screenqc.db`
- macOS bundle: `~/Library/Application Support/MonitorQC/data/screenqc.db`
- Windows bundle: `%APPDATA%/MonitorQC/data/screenqc.db`

---

## Flow การทำงาน

```
home → select_type → select_period → login → confirm → instructions
  → test_runner → results → after_save
                               ↓
              [comparison / criteria / history / history_result]
```

---

## ฟีเจอร์สำคัญ

| ฟีเจอร์ | รายละเอียด |
|---------|-----------|
| **Multi-user** | หลายผู้ใช้ มี password; จัดการผ่าน user_list screen |
| **Test runner** | แสดง test pattern PNG/TIFF, pre-cache frames, ตอบ yes/no |
| **Channel tracking** | บันทึกช่องที่ fail ด้วย JSON array (checkbox หรือ text input) |
| **Range input** | ระบุช่อง fail แบบช่วงได้ เช่น `2-23, 34, 40-42, 55` |
| **Baseline** | กำหนดผลการประเมินใดก็ได้เป็น baseline สำหรับเปรียบเทียบ |
| **Comparison** | เทียบผลปัจจุบัน vs baseline ทีละข้อ แยก drift A/B |
| **History** | ค้นหาประวัติด้วย date range + ชนิดหน้าจอ filter |
| **PDF report** | สร้าง PDF landscape A4 ด้วย ReportLab + ฟอนต์ไทย |
| **Excel export** | export ผลเป็น .xlsx ด้วย openpyxl |
| **Canvas table** | results & history_result ใช้ Canvas-based table (text wrap) |
| **Responsive UI** | scale ทุก font/size จาก reference 1920×1080 |
| **Period color bar** | select_period, login, confirm แสดงแถบสีตาม period |
| **คู่มือ PDF** | คู่มือภาษาไทย 22 หน้า พร้อมภาพหน้าจอจริง (NU branding) |

---

## การ Build

```bash
# Windows
pyinstaller --noconfirm --onefile --windowed --name "MonitorQC" \
  --add-data "assets;assets" --add-data "screens;screens" --add-data "reports;reports" \
  --hidden-import "PIL._tkinter_finder" main.py

# macOS
pyinstaller --noconfirm --onedir --windowed --name "MonitorQC" \
  --add-data "assets:assets" --add-data "screens:screens" --add-data "reports:reports" \
  --hidden-import "PIL._tkinter_finder" main.py
```

GitHub Actions build อัตโนมัติทุก push to main → สร้าง artifacts `MonitorQC-windows` (`.exe`) และ `MonitorQC-macos` (`.zip`)

---

## เอกสารอ้างอิง

1. Bevins NB, Badano A, et al. *Display Quality Assurance — The Report of AAPM Task Group 270.* AAPM, 2019. https://www.aapm.org/pubs/reports/RPT_270.pdf
2. IAEA. *IAEA Human Health Series No. 47 — Handbook of Basic Quality Control Tests for Diagnostic Radiology.* Vienna, 2023.
3. กรมวิทยาศาสตร์การแพทย์. *การควบคุมคุณภาพเครื่องเอกซเรย์วินิจฉัยทางการแพทย์.* นนทบุรี, 2022.
4. ACR-AAPM-SIIM. *Technical Standard for Electronic Practice of Medical Imaging.* Reston (VA): ACR, 2022.
