import tkinter as tk
from screens.base import BaseScreen, CARD_COLOR, TEXT_COLOR, thai_font, CARD_W, CARD_HL


class SelectTypeScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=CARD_W, height=CARD_HL)

        self.card_header(card, "โปรแกรมตรวจคุณภาพหน้าจอ", bg="white", size=24)

        body = tk.Frame(card, bg=CARD_COLOR)
        body.pack(fill="both", expand=True)

        self.title_label(body, "โปรดเลือกชนิดหน้าจอ", size=50).pack(pady=(40, 50))

        types = [
            ("diagnostic", "หน้าจอชนิดใช้วินิจฉัยทางการแพทย์\n(Diagnostic)"),
            ("modality",   "หน้าจอชนิดใช้แสดงทางการแพทย์\n(Modality)"),
            ("clinic",     "หน้าจอตรวจทานทางการแพทย์ (Clinical Review)\nและหน้าจอสำหรับงานเวชระเบียน\n(Electronic Health Record)"),
        ]

        for key, label in types:
            self.primary_btn(
                body, label,
                command=lambda k=key: self._select(k),
                fontsize=26, padx=20, pady=6,
                width=46,
            ).pack(pady=8)

        bottom = tk.Frame(card, bg=CARD_COLOR)
        bottom.pack(side="bottom", fill="x", padx=16, pady=12)
        self.primary_btn(bottom, "ย้อนกลับ", lambda: app.show("home"), fontsize=26, width=12).pack(side="right", padx=4)

    def _select(self, screen_type: str):
        self.app.session["screen_type"] = screen_type
        self.app.show("select_period")
