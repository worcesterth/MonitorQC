import tkinter as tk
from screens.base import (BaseScreen, CARD_COLOR, BORDER_CLR, ENTRY_BG,
                           TEXT_COLOR, thai_font)
from database import get_all_users, delete_user, update_user, verify_user_password


class UserListScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=self.CARD_W, height=self.CARD_HL)

        self.card_header(card, "รายชื่อผู้ใช้งาน", size=self.fs(24))

        # ── ปุ่มล่าง (pack ก่อน list เพื่อให้ขอบล่างจอง space ก่อน) ──────────
        btn_row = tk.Frame(card, bg=CARD_COLOR)
        btn_row.pack(side="bottom", fill="x", padx=16, pady=12)
        self.back_btn(btn_row, "ย้อนกลับ", lambda: app.show("register"),
                      fontsize=self.fs(24), width=12).pack(side="left")

        # header row
        hdr = tk.Frame(card, bg="#FFFFFF")
        hdr.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(hdr, text="ชื่อ", font=thai_font(self.fs(24), "bold"), bg="#FFFFFF",
                 fg=TEXT_COLOR, width=16, anchor="w").pack(side="left", padx=(4, 0))
        tk.Label(hdr, text="นามสกุล", font=thai_font(self.fs(24), "bold"), bg="#FFFFFF",
                 fg=TEXT_COLOR, width=16, anchor="w").pack(side="left", padx=(8, 0))
        tk.Frame(card, bg=BORDER_CLR, height=1).pack(fill="x", padx=16, pady=(4, 0))

        # scrollable list
        list_container = tk.Frame(card, bg=CARD_COLOR)
        list_container.pack(fill="both", expand=True, padx=16, pady=4)

        canvas = tk.Canvas(list_container, bg=CARD_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(canvas, bg=CARD_COLOR)
        self._win_id = canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
                             lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._win_id, width=e.width))
        self._canvas = canvas

        # ── action panel (ซ่อนไว้ก่อน) ───────────────────────────────────────
        self._panel = tk.Frame(card, bg="#ebebeb",
                               highlightbackground=BORDER_CLR, highlightthickness=1)
        self._panel_msg  = tk.Label(self._panel, text="", font=thai_font(self.fs(22)),
                                    bg="#ebebeb", fg=TEXT_COLOR)
        self._panel_msg.pack(anchor="w", padx=12, pady=(10, 4))

        # password row
        pw_row = tk.Frame(self._panel, bg="#ebebeb")
        pw_row.pack(fill="x", padx=12, pady=4)
        tk.Label(pw_row, text="รหัส :", font=thai_font(self.fs(22)), bg="#ebebeb",
                 fg=TEXT_COLOR).pack(side="left")
        self._pw_entry = tk.Entry(pw_row, font=thai_font(self.fs(22)), bg=ENTRY_BG,
                                  fg=TEXT_COLOR, relief="sunken", bd=2, width=20, show="*")
        self._pw_entry.pack(side="left", padx=(8, 0))

        # edit fields (ซ่อนไว้ก่อน ใช้ตอน mode=edit หลัง verify)
        self._edit_frame = tk.Frame(self._panel, bg="#ebebeb")
        edit_fields = [("ชื่อ :", "edit_name"), ("นามสกุล :", "edit_lastname"), ("รหัสใหม่ :", "edit_password")]
        self._edit_entries: dict[str, tk.Entry] = {}
        for lbl_text, key in edit_fields:
            ef_row = tk.Frame(self._edit_frame, bg="#ebebeb")
            ef_row.pack(fill="x", pady=2)
            tk.Label(ef_row, text=lbl_text, font=thai_font(self.fs(22)), bg="#ebebeb",
                     fg=TEXT_COLOR, width=10, anchor="e").pack(side="left")
            show_char = "*" if key == "edit_password" else ""
            e = tk.Entry(ef_row, font=thai_font(self.fs(22)), bg=ENTRY_BG, fg=TEXT_COLOR,
                         relief="sunken", bd=2, width=22, show=show_char)
            e.pack(side="left", padx=(6, 0))
            self._edit_entries[key] = e
            if key == "edit_password":
                self._edit_pw_visible = False
                toggle = tk.Label(ef_row, text="แสดง", font=thai_font(self.fs(20)),
                                  bg="#ebebeb", fg="#0000cc", cursor="hand2")
                toggle.pack(side="left", padx=(6, 0))
                toggle.bind("<ButtonRelease-1>", self._toggle_edit_pw)
                self._edit_toggle_btn = toggle
        self._edit_err = tk.Label(self._edit_frame, text="", font=thai_font(self.fs(20)),
                                  bg="#ebebeb", fg="#cc0000")
        self._edit_err.pack(anchor="w", padx=4)

        # panel buttons
        panel_btns = tk.Frame(self._panel, bg="#ebebeb")
        panel_btns.pack(fill="x", padx=12, pady=(4, 10))
        self._confirm_btn = self.primary_btn(panel_btns, "ยืนยัน", self._confirm,
                                             fontsize=self.fs(20), width=10)
        self._confirm_btn.pack(side="left", padx=(0, 8))
        self.primary_btn(panel_btns, "ยกเลิก", self._close_panel,
                         fontsize=self.fs(20), width=10).pack(side="left")
        self._panel_err = tk.Label(self._panel, text="", font=thai_font(self.fs(20)),
                                   bg="#ebebeb", fg="#cc0000")
        self._panel_err.pack(anchor="w", padx=12, pady=(0, 6))

        # state
        self._pending_user: dict | None = None
        self._mode: str = ""   # "delete" | "verify_edit" | "edit"

    # ── list refresh ──────────────────────────────────────────────────────────

    def on_show(self, **_):
        self._close_panel()
        self._rebuild_list()

    def _rebuild_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        users = get_all_users()
        if not users:
            tk.Label(self.list_frame, text="ยังไม่มีผู้ใช้งานที่ลงทะเบียน",
                     font=thai_font(self.fs(24)), bg=CARD_COLOR, fg="#888888").pack(pady=20)
        else:
            for u in users:
                row = tk.Frame(self.list_frame, bg=CARD_COLOR)
                row.pack(fill="x", pady=2)

                tk.Label(row, text=u["name"], font=thai_font(self.fs(24)), bg=CARD_COLOR,
                         fg=TEXT_COLOR, width=16, anchor="w").pack(side="left", padx=(4, 0))
                tk.Label(row, text=u.get("lastname", ""), font=thai_font(self.fs(24)), bg=CARD_COLOR,
                         fg=TEXT_COLOR, width=16, anchor="w").pack(side="left", padx=(8, 0))

                edit_lbl = tk.Label(row, text="แก้ไข", font=thai_font(self.fs(22)),
                                    bg=CARD_COLOR, fg="#0055cc", cursor="hand2")
                edit_lbl.pack(side="right", padx=(4, 8))
                edit_lbl.bind("<ButtonRelease-1>", lambda _, usr=u: self._open_verify_edit(usr))

                del_lbl = tk.Label(row, text="ลบ", font=thai_font(self.fs(22)),
                                   bg=CARD_COLOR, fg="#cc0000", cursor="hand2")
                del_lbl.pack(side="right", padx=4)
                del_lbl.bind("<ButtonRelease-1>", lambda _, usr=u: self._open_delete(usr))

                tk.Frame(self.list_frame, bg=BORDER_CLR, height=1).pack(fill="x", pady=(0, 2))

        self.list_frame.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    # ── panel helpers ─────────────────────────────────────────────────────────

    def _open_delete(self, user: dict):
        self._pending_user = user
        self._mode = "delete"
        self._panel_msg.configure(
            text=f"ยืนยันลบ \"{user['name']} {user.get('lastname','')}\" — กรุณาใส่รหัส")
        self._edit_frame.pack_forget()
        self._pw_entry.configure(show="*")
        self._pw_entry.delete(0, "end")
        self._pw_entry.configure(highlightthickness=0)
        self._panel_err.configure(text="")
        self._panel.pack(fill="x", padx=16, pady=(0, 4), before=self._canvas.master)

    def _open_verify_edit(self, user: dict):
        self._pending_user = user
        self._mode = "verify_edit"
        self._panel_msg.configure(
            text=f"แก้ไข \"{user['name']} {user.get('lastname','')}\" — กรุณาใส่รหัสก่อน")
        self._edit_frame.pack_forget()
        self._pw_entry.configure(show="*")
        self._pw_entry.delete(0, "end")
        self._pw_entry.configure(highlightthickness=0)
        self._panel_err.configure(text="")
        self._panel.pack(fill="x", padx=16, pady=(0, 4), before=self._canvas.master)

    def _close_panel(self):
        self._pending_user = None
        self._mode = ""
        self._panel.pack_forget()
        self._edit_frame.pack_forget()
        self._panel_err.configure(text="")
        self._edit_err.configure(text="")

    def _confirm(self):
        if self._mode == "delete":
            self._do_delete()
        elif self._mode == "verify_edit":
            self._do_verify_then_edit()
        elif self._mode == "edit":
            self._do_save_edit()

    def _do_delete(self):
        pw = self._pw_entry.get()
        if not verify_user_password(self._pending_user["id"], pw):
            self._pw_entry.configure(highlightbackground="#cc0000",
                                     highlightthickness=2, highlightcolor="#cc0000")
            self._panel_err.configure(text="รหัสไม่ถูกต้อง")
            return
        delete_user(self._pending_user["id"])
        self._close_panel()
        self._rebuild_list()

    def _toggle_edit_pw(self, _=None):
        self._edit_pw_visible = not self._edit_pw_visible
        self._edit_entries["edit_password"].configure(
            show="" if self._edit_pw_visible else "*")
        self._edit_toggle_btn.configure(
            text="ซ่อน" if self._edit_pw_visible else "แสดง")

    def _do_verify_then_edit(self):
        pw = self._pw_entry.get()
        if not verify_user_password(self._pending_user["id"], pw):
            self._pw_entry.configure(highlightbackground="#cc0000",
                                     highlightthickness=2, highlightcolor="#cc0000")
            self._panel_err.configure(text="รหัสไม่ถูกต้อง")
            return
        # รหัสถูก — เปลี่ยนไป edit mode
        self._mode = "edit"
        self._panel_msg.configure(
            text=f"แก้ไขชื่อ-นามสกุล \"{self._pending_user['name']} {self._pending_user.get('lastname','')}\"")
        self._pw_entry.master.pack_forget()   # ซ่อน password row
        self._panel_err.configure(text="")
        self._edit_entries["edit_name"].delete(0, "end")
        self._edit_entries["edit_name"].insert(0, self._pending_user["name"])
        self._edit_entries["edit_lastname"].delete(0, "end")
        self._edit_entries["edit_lastname"].insert(0, self._pending_user.get("lastname", ""))
        self._edit_entries["edit_password"].delete(0, "end")
        self._edit_pw_visible = False
        self._edit_entries["edit_password"].configure(show="*")
        self._edit_toggle_btn.configure(text="แสดง")
        for e in self._edit_entries.values():
            e.configure(highlightthickness=0)
        self._edit_err.configure(text="")
        self._edit_frame.pack(fill="x", padx=12, pady=4)

    def _do_save_edit(self):
        name     = self._edit_entries["edit_name"].get().strip()
        lastname = self._edit_entries["edit_lastname"].get().strip()
        new_pw   = self._edit_entries["edit_password"].get().strip()
        has_error = False
        for key, entry in [("edit_name", self._edit_entries["edit_name"]),
                            ("edit_lastname", self._edit_entries["edit_lastname"])]:
            if not entry.get().strip():
                entry.configure(highlightbackground="#cc0000",
                                highlightthickness=2, highlightcolor="#cc0000")
                has_error = True
            else:
                entry.configure(highlightthickness=0)
        if has_error:
            self._edit_err.configure(text="กรุณากรอกชื่อและนามสกุลให้ครบ")
            return

        # ถ้าไม่ได้กรอกรหัสใหม่ ใช้รหัสเดิม
        password = new_pw if new_pw else self._pending_user["password"]
        err = update_user(self._pending_user["id"], name, lastname, password)
        if err:
            self._edit_err.configure(text=err)
            return

        self._close_panel()
        # คืน password row กลับมาสำหรับครั้งถัดไป
        pw_row = self._pw_entry.master
        pw_row.pack(fill="x", padx=12, pady=4)
        self._rebuild_list()
