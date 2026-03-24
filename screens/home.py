import tkinter as tk
from screens.base import BaseScreen, CARD_COLOR, CARD_W, CARD_HL


class HomeScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=CARD_W, height=CARD_HL)

        self.card_header(card, "โปรแกรมตรวจคุณภาพหน้าจอ", bg="white", size=24)

        body = tk.Frame(card, bg=CARD_COLOR)
        body.pack(fill="both", expand=True)

        self.title_label(body, "โปรแกรมตรวจคุณภาพหน้าจอ", size=70).pack(pady=(40, 80))

        self.primary_btn(
            body, "เริ่มการทดสอบ",
            command=lambda: app.show("select_type"),
            width=20, fontsize=50, pady=10, padx=20,
        ).pack()

        self.primary_btn(
            body, "ประวัติการทดสอบ",
            command=lambda: app.show("history"),
            width=20, fontsize=50, pady=10, padx=20,
        ).pack(pady=(20, 0))

        self.primary_btn(
            body, "ลงทะเบียน",
            command=lambda: app.show("register"),
            width=20, fontsize=50, pady=10, padx=20,
        ).pack(pady=(20, 0))
