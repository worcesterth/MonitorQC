import tkinter as tk
from screens.base import (BaseScreen, CARD_COLOR, BORDER_CLR, BTN_BG, BTN_ACTIVE,
                           ENTRY_BG, TEXT_COLOR, thai_font, CARD_W, CARD_HL)
from database import save_settings, get_settings, add_user


class RegisterScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=CARD_W, height=CARD_HL)

        self.card_header(card, "ลงทะเบียน", bg="white", size=24)

        body = tk.Frame(card, bg=CARD_COLOR)
        body.pack(fill="both", expand=True, padx=36, pady=16)

        # ── ส่วนที่ 1: ข้อมูลอุปกรณ์ ─────────────────────────────────────────
        tk.Label(body, text="ข้อมูลโรงพยาบาล / อุปกรณ์",
                 font=thai_font(26, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")
        tk.Frame(body, bg=BORDER_CLR, height=1).pack(fill="x", pady=(2, 10))

        dev_form = tk.Frame(body, bg=CARD_COLOR)
        dev_form.pack(fill="x")

        dev_fields = [
            ("ชื่อโรงพยาบาล :",    "hospital_name"),
            ("หมายเลขคุรุภัณฑ์ :", "screen_model"),
        ]

        self.dev_val_labels: dict[str, tk.Label] = {}
        self.dev_entries: dict[str, tk.Entry] = {}

        for row, (lbl_text, key) in enumerate(dev_fields):
            tk.Label(dev_form, text=lbl_text, font=thai_font(24), bg=CARD_COLOR,
                     fg=TEXT_COLOR, anchor="e").grid(row=row, column=0, sticky="e",
                                                     padx=(0, 10), pady=6)
            # label (view mode)
            lbl = tk.Label(dev_form, text="", font=thai_font(24), bg=CARD_COLOR,
                           fg=TEXT_COLOR, anchor="w", width=30)
            lbl.grid(row=row, column=1, sticky="w", pady=6)
            self.dev_val_labels[key] = lbl

            # entry (edit mode) — ซ่อนไว้ก่อน
            e = tk.Entry(dev_form, font=thai_font(24), bg=ENTRY_BG, fg=TEXT_COLOR,
                         relief="sunken", bd=2, width=34)
            e.grid(row=row, column=1, sticky="w", pady=6)
            e.grid_remove()
            self.dev_entries[key] = e

        self.dev_msg = tk.Label(body, text="", font=thai_font(20), bg=CARD_COLOR, fg="#cc0000")
        self.dev_msg.pack(anchor="w", pady=(2, 0))

        # ปุ่ม container — สลับปุ่มในนี้
        self._dev_btn_container = tk.Frame(body, bg=CARD_COLOR)
        self._dev_btn_container.pack(anchor="w", pady=(4, 12))
        self._dev_btn_save = self.primary_btn(
            self._dev_btn_container, "บันทึกข้อมูลอุปกรณ์", self._save_settings,
            fontsize=22, width=22, pady=6)
        self._dev_btn_edit = self.primary_btn(
            self._dev_btn_container, "แก้ไข", self._start_edit,
            fontsize=22, width=22, pady=6)

        # ── ส่วนที่ 2: เพิ่มผู้ใช้งาน ────────────────────────────────────────
        tk.Label(body, text="เพิ่มผู้ใช้งาน",
                 font=thai_font(26, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")
        tk.Frame(body, bg=BORDER_CLR, height=1).pack(fill="x", pady=(2, 10))

        user_form = tk.Frame(body, bg=CARD_COLOR)
        user_form.pack(fill="x")

        self.user_entries: dict[str, tk.Entry] = {}
        for row, (lbl_text, key) in enumerate([("ชื่อ :", "name"), ("นามสกุล :", "lastname"), ("รหัส :", "password")]):
            tk.Label(user_form, text=lbl_text, font=thai_font(24), bg=CARD_COLOR,
                     fg=TEXT_COLOR, anchor="e").grid(row=row, column=0, sticky="e",
                                                     padx=(0, 10), pady=6)
            e = tk.Entry(user_form, font=thai_font(24), bg=ENTRY_BG, fg=TEXT_COLOR,
                         relief="sunken", bd=2, width=34)
            e.grid(row=row, column=1, sticky="w", pady=6)
            self.user_entries[key] = e

        # toggle แสดง/ซ่อนรหัส
        self._pw_visible = False
        self.user_entries["password"].configure(show="*")
        self._toggle_btn = tk.Label(user_form, text="แสดง", font=thai_font(20),
                                    bg=CARD_COLOR, fg="#0000cc", cursor="hand2")
        self._toggle_btn.grid(row=2, column=2, padx=(6, 0))
        self._toggle_btn.bind("<ButtonRelease-1>", self._toggle_password)

        self.user_msg = tk.Label(body, text="", font=thai_font(20), bg=CARD_COLOR, fg="#cc0000")
        self.user_msg.pack(anchor="w", pady=(2, 0))

        # ── ปุ่มล่าง ──────────────────────────────────────────────────────────
        btn_row = tk.Frame(card, bg=CARD_COLOR)
        btn_row.pack(side="bottom", fill="x", padx=16, pady=12)
        self.primary_btn(btn_row, "เพิ่มผู้ใช้",     self._add_user,   fontsize=24, width=14).pack(side="right", padx=4)
        self.primary_btn(btn_row, "ดูรายชื่อผู้ใช้", self._show_users, fontsize=24, width=14).pack(side="right", padx=4)
        self.primary_btn(btn_row, "ย้อนกลับ",         self._back,       fontsize=24, width=12).pack(side="left",  padx=4)

    # ── mode helpers ──────────────────────────────────────────────────────────

    def _set_view_mode(self, settings: dict):
        """แสดงข้อมูลเป็น Label (ปุ่มแก้ไข)"""
        for key, lbl in self.dev_val_labels.items():
            lbl.configure(text=settings.get(key, ""))
            lbl.grid()
            self.dev_entries[key].grid_remove()
        self._dev_btn_save.pack_forget()
        self._dev_btn_edit.pack(anchor="w")

    def _set_edit_mode(self):
        """แสดง Entry (ปุ่มบันทึก)"""
        for key, e in self.dev_entries.items():
            e.delete(0, "end")
            e.insert(0, self.dev_val_labels[key].cget("text"))
            e.configure(highlightthickness=0)
            e.grid()
            self.dev_val_labels[key].grid_remove()
        self._dev_btn_edit.pack_forget()
        self._dev_btn_save.pack(anchor="w")

    def _start_edit(self):
        self.dev_msg.configure(text="")
        self._set_edit_mode()

    # ── on_show ───────────────────────────────────────────────────────────────

    def on_show(self, **_):
        self.dev_msg.configure(text="", fg="#cc0000")
        self.user_msg.configure(text="", fg="#cc0000")
        for e in self.user_entries.values():
            e.configure(highlightthickness=0)
            e.delete(0, "end")
        self._pw_visible = False
        self.user_entries["password"].configure(show="*")
        self._toggle_btn.configure(text="แสดง")

        settings = get_settings()
        if settings:
            self._set_view_mode(settings)
        else:
            self._set_edit_mode()

    # ── actions ───────────────────────────────────────────────────────────────

    def _toggle_password(self, _=None):
        self._pw_visible = not self._pw_visible
        self.user_entries["password"].configure(show="" if self._pw_visible else "*")
        self._toggle_btn.configure(text="ซ่อน" if self._pw_visible else "แสดง")

    def _back(self):
        self.app.show("home")

    def _show_users(self):
        self.app.show("user_list")

    def _save_settings(self):
        values = {}
        has_error = False
        for key, entry in self.dev_entries.items():
            val = entry.get().strip()
            if not val:
                entry.configure(highlightbackground="#cc0000", highlightthickness=2,
                                highlightcolor="#cc0000")
                has_error = True
            else:
                entry.configure(highlightthickness=0)
                values[key] = val

        if has_error:
            self.dev_msg.configure(text="กรุณากรอกข้อมูลให้ครบ", fg="#cc0000")
            return

        save_settings(hospital=values["hospital_name"], screen_model=values["screen_model"])
        self.dev_msg.configure(text="บันทึกข้อมูลอุปกรณ์เรียบร้อยแล้ว", fg="#1a6e1a")
        self._set_view_mode(values)

    def _add_user(self):
        values = {}
        has_error = False
        for key, entry in self.user_entries.items():
            val = entry.get().strip()
            if not val:
                entry.configure(highlightbackground="#cc0000", highlightthickness=2,
                                highlightcolor="#cc0000")
                has_error = True
            else:
                entry.configure(highlightthickness=0)
                values[key] = val

        if has_error:
            self.user_msg.configure(text="กรุณากรอกชื่อและรหัสให้ครบ", fg="#cc0000")
            return

        err = add_user(name=values["name"], lastname=values["lastname"], password=values["password"])
        if err:
            self.user_msg.configure(text=err, fg="#cc0000")
            return

        self.user_msg.configure(
            text=f"เพิ่มผู้ใช้ \"{values['name']} {values['lastname']}\" เรียบร้อยแล้ว", fg="#1a6e1a")
        for entry in self.user_entries.values():
            entry.delete(0, "end")
