import tkinter as tk
from screens.base import BaseScreen, CARD_COLOR, TEXT_COLOR, thai_font, CARD_W, CARD_H
from config import TEST_CONFIG

INSTRUCTION_LINES = [
    "1. ควรเปิดหน้าจอไว้ก่อน 30 นาที",
    "2. ระยะห่างของการทดสอบตั้งแต่ระยะสายตาของผู้ทดสอบถึงหน้าจอ ควรมีระยะห่าง\n"
    "    ประมาณหนึ่งช่วงแขน (ประมาณ 65 เซนติเมตร)",
    "3. ทำความสะอาดหน้าจอก่อนตามที่บริษัทผู้ผลิตแนะนำการทดสอบ",
]


class InstructionsScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=CARD_W, height=CARD_H)

        self.card_header(card, "คำแนะนำในการทดสอบระบบ", bg="white", size=24)

        body = tk.Frame(card, bg=CARD_COLOR)
        body.pack(fill="both", expand=True, padx=30, pady=28)

        for line in INSTRUCTION_LINES:
            tk.Label(body, text=line, font=thai_font(28), bg=CARD_COLOR,
                     fg=TEXT_COLOR, anchor="w", justify="left",
                     wraplength=620).pack(anchor="w", pady=8)

        btn_frame = tk.Frame(card, bg=CARD_COLOR)
        btn_frame.pack(side="bottom", fill="x", padx=16, pady=12)
        self.primary_btn(btn_frame, "ถัดไป",    self._next,                  fontsize=26, width=12).pack(side="right", padx=4)
        self.primary_btn(btn_frame, "ย้อนกลับ", lambda: app.show("confirm"), fontsize=26, width=12).pack(side="right", padx=4)

    def on_show(self, **_):
        session = self.app.session
        screen_type = session.get("screen_type", "diagnostic")
        period      = session.get("period", "monthly")

        groups = TEST_CONFIG.get(screen_type, {}).get(period, [])
        items = []
        idx = 1
        for group in groups:
            for item in group["items"]:
                items.append({**item,
                               "group_id":    group["group_id"],
                               "group_title": group["group_title"],
                               "image_index": idx})
                idx += 1

        session["test_items"]       = items
        session["current_item_idx"] = 0
        session["answers"]          = {}

    def _next(self):
        self.app.show("test_runner")
