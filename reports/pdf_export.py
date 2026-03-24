"""PDF export utilities using reportlab + THSarabunNew font."""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "THSarabunNew.ttf")
_FONT_REGISTERED = False


def _register():
    global _FONT_REGISTERED
    if not _FONT_REGISTERED:
        pdfmetrics.registerFont(TTFont("Thai", _FONT_PATH))
        pdfmetrics.registerFont(TTFont("ThaiBd", _FONT_PATH))   # same ttf, bolder via size
        _FONT_REGISTERED = True


def _p(text, size=12, bold=False, fg=colors.black, align="LEFT"):
    """Create a Paragraph with Thai font."""
    _register()
    style = ParagraphStyle(
        "t",
        fontName="ThaiBd" if bold else "Thai",
        fontSize=size,
        textColor=fg,
        alignment={"LEFT": 0, "CENTER": 1, "RIGHT": 2}.get(align, 0),
        leading=size * 1.5,
        wordWrap="CJK",
    )
    safe = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


_BASE_STYLE = [
    ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#d0d0d0")),
]


# ── History Result ─────────────────────────────────────────────────────────────

def export_history_result(ev: dict, groups: list, filepath: str, copies: int = 1, rank: int = 0) -> None:
    _register()

    type_map   = {"diagnostic": "Diagnostic", "modality": "Modality", "clinic": "Clinical Review"}
    period_map = {"monthly": "รายเดือน", "quarterly": "ราย 3 เดือน", "annual": "ประจำปี"}
    stype  = type_map.get(ev.get("screen_type", ""), "")
    period = period_map.get(ev.get("period", ""), "")

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    story = [
        _p("ผลการประเมิน", size=20, bold=True, align="CENTER"),
        Spacer(1, 3*mm),
        _p(f"{ev.get('hospital_name','')}  |  {ev.get('evaluator_name','')}  |  {('ครั้งที่ ' + str(rank)) if rank else ''}  |  {stype}  |  {period}  |  {ev.get('eval_datetime','')}", size=13),
        Spacer(1, 4*mm),
    ]

    # usable width ≈ A4(595) – 30mm = 510pt
    col_w = [105*mm, 32*mm, 40*mm]

    answers = ev.get("answers", {})
    data = [[
        _p("หัวข้อการประเมิน", 13, bold=True),
        _p("ผลการประเมิน",    13, bold=True, align="CENTER"),
        _p("หมายเหตุ",        13, bold=True),
    ]]
    style_extra = []

    CLR_PASS = colors.HexColor("#007700")
    CLR_FAIL = colors.HexColor("#cc0000")
    CLR_NONE = colors.HexColor("#888888")

    for group in groups:
        ri = len(data)
        data.append([_p(group["group_title"], 13, bold=True), _p(""), _p("")])
        style_extra += [
            ("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#c8c8c8")),
            ("SPAN",       (0, ri), (-1, ri)),
        ]

        for item in group["items"]:
            ans = answers.get(item["item_id"])
            if ans:
                res   = "ผ่าน ✓" if ans["passed"] else "ไม่ผ่าน ✗"
                rfg   = CLR_PASS  if ans["passed"] else CLR_FAIL
                notes = ans.get("notes", "")
                if ans.get("failed_channels"):
                    ch_str = ", ".join(str(c) for c in ans["failed_channels"])
                    notes  = f"ช่องที่ไม่เห็น: {ch_str}" + (f"  {notes}" if notes else "")
            else:
                res, rfg, notes = "ไม่ได้ตอบ", CLR_NONE, ""

            ri = len(data)
            data.append([
                _p(f"  {item['title']}", 12),
                _p(res, 12, fg=rfg, align="CENTER"),
                _p(notes, 12),
            ])

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle(_BASE_STYLE + style_extra))
    story.append(tbl)

    if copies > 1:
        full = []
        for i in range(copies):
            full.extend(story)
            if i < copies - 1:
                full.append(PageBreak())
        doc.build(full)
    else:
        doc.build(story)


# ── Comparison ─────────────────────────────────────────────────────────────────

def export_comparison(current: dict, baseline: dict, row_data: list, filepath: str) -> None:
    """
    row_data: list of dicts with keys:
        is_group, title, b_text, c_text, result_text, description, tag
    """
    _register()

    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    now_txt  = f"ครั้งนี้: {current.get('hospital_name','')}  {current.get('evaluator_name','')}  {current.get('eval_datetime','')}"
    base_txt = f"ครั้งก่อนหน้า: {baseline.get('hospital_name','')}  {baseline.get('evaluator_name','')}  {baseline.get('eval_datetime','')}"

    story = [
        _p("เปรียบเทียบกับครั้งก่อนหน้า", size=20, bold=True, align="CENTER"),
        Spacer(1, 3*mm),
        _p(f"{now_txt}     |     {base_txt}", size=12),
        Spacer(1, 4*mm),
    ]

    # landscape A4 usable ≈ 842 – 30mm = 782pt ≈ 276mm
    col_w = [72*mm, 26*mm, 26*mm, 64*mm, 88*mm]

    TAG_FG = {
        "degraded": colors.HexColor("#cc0000"),
        "drift":    colors.HexColor("#b36b00"),
        "no_ans":   colors.HexColor("#888888"),
        "same":     colors.HexColor("#333333"),
    }

    data = [[
        _p("หัวข้อประเมิน",                      12, bold=True),
        _p("Baseline",                            12, bold=True, align="CENTER"),
        _p("Now",                                 12, bold=True, align="CENTER"),
        _p("ผลการเปรียบเทียบ",                   12, bold=True),
        _p("คำอธิบายเพิ่มเติมจากการเปรียบเทียบ", 12, bold=True),
    ]]
    style_extra = []

    for row in row_data:
        ri = len(data)
        if row["is_group"]:
            data.append([_p(row["title"], 12, bold=True),
                         _p(""), _p(""), _p(""), _p("")])
            style_extra += [
                ("BACKGROUND", (0, ri), (-1, ri), colors.HexColor("#c8c8c8")),
                ("SPAN",       (0, ri), (-1, ri)),
            ]
        else:
            fg = TAG_FG.get(row["tag"], colors.black)
            data.append([
                _p(row["title"],       11, fg=fg),
                _p(row["b_text"],      11, fg=fg, align="CENTER"),
                _p(row["c_text"],      11, fg=fg, align="CENTER"),
                _p(row["result_text"], 11, fg=fg),
                _p(row["description"], 11, fg=fg),
            ])

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle(_BASE_STYLE + style_extra))
    story.append(tbl)
    doc.build(story)
