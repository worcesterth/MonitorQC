import tkinter as tk
from tkinter import ttk
from screens.base import (
    BaseScreen, BG_COLOR, CARD_COLOR, TEXT_COLOR,
    BORDER_CLR, PASS_GREEN, FAIL_RED, thai_font,
)


class ResultsScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        # ── header ────────────────────────────────────────────────────
        self.card_header(self, "ผลการประเมินคุณภาพหน้าจอ", size=self.fs(26))

        # ── info bar ──────────────────────────────────────────────────
        info_bar = tk.Frame(self, bg=BG_COLOR, bd=1, relief="solid")
        info_bar.pack(fill="x", padx=20, pady=(8, 4))
        self.info_lbl = tk.Label(info_bar, text="", font=thai_font(self.fs(26)),
                                  bg=BG_COLOR, fg=TEXT_COLOR)
        self.info_lbl.pack(side="left")

        # ── table ─────────────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=4)

        style = ttk.Style()
        style.configure("Results.Treeview",
                         font=thai_font(self.fs(26)),
                         rowheight=max(22, int(36 * self._s)),
                         background=CARD_COLOR,
                         fieldbackground=CARD_COLOR,
                         foreground=TEXT_COLOR)
        style.configure("Results.Treeview.Heading",
                         font=thai_font(self.fs(26), "bold"),
                         background=BG_COLOR,
                         foreground=TEXT_COLOR,
                         relief="flat")
        style.map("Results.Treeview",
                  background=[("selected", "#b0c8e8")])

        cols = ("หัวข้อการประเมิน", "ผลการประเมิน", "หมายเหตุ")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", style="Results.Treeview")

        self.tree.heading("หัวข้อการประเมิน", text="หัวข้อการประเมิน", anchor="w")
        self.tree.heading("ผลการประเมิน",    text="ผลการประเมิน",    anchor="center")
        self.tree.heading("หมายเหตุ",        text="หมายเหตุ",        anchor="w")

        self.tree.column("หัวข้อการประเมิน", width=int(520 * self._s), anchor="w",    stretch=True)
        self.tree.column("ผลการประเมิน",    width=int(140 * self._s), anchor="center", stretch=False)
        self.tree.column("หมายเหตุ",        width=int(260 * self._s), anchor="w",    stretch=True)

        # tag สี
        self.tree.tag_configure("pass",    foreground=PASS_GREEN)
        self.tree.tag_configure("fail",    foreground=FAIL_RED)
        self.tree.tag_configure("group",   background="#c8c8c8", font=thai_font(self.fs(26), "bold"))
        self.tree.tag_configure("no_ans",  foreground="#888888")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        # ── ปุ่มล่าง ──────────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=20, pady=12)

        self.primary_btn(btn_bar, "บันทึกผล",
                         self._save, fontsize=self.fs(26), width=14).pack(side="right", padx=4)
        self.primary_btn(btn_bar, "ไม่บันทึกผล",
                         self._discard, fontsize=self.fs(26), width=14).pack(side="right", padx=4)

        self.primary_btn(btn_bar, "ทดสอบใหม่",
                         self._retest, fontsize=self.fs(26), width=14).pack(side="left", padx=4)

    # ── on_show ───────────────────────────────────────────────────────

    def on_show(self, **_):
        session = self.app.session
        items   = session.get("test_items", [])
        answers = session.get("answers", {})

        # info bar
        type_map   = {"diagnostic": "Diagnostic", "modality": "Modality", "clinic": "Clinical Review"}
        period_map = {"monthly": "ประจำเดือน", "quarterly": "ประจำ 3 เดือน", "annual": "ประจำปี"}
        stype  = type_map.get(session.get("screen_type", ""), "")
        period = period_map.get(session.get("period", ""), "")
        
        eval_dt_str = session.get("eval_datetime", "")
        try:
            import datetime
            dt_obj = datetime.datetime.strptime(eval_dt_str, "%Y-%m-%d %H:%M:%S")
            thai_year = dt_obj.year + 543
            display_date = f"{dt_obj.day:02d}/{dt_obj.month:02d}/{thai_year} {dt_obj.strftime('%H:%M:%S')}"
        except Exception:
            display_date = eval_dt_str
            
        self.info_lbl.configure(
            text=f"{session.get('hospital_name','')}  |  {session.get('evaluator_name','')}  |  {stype}  |  {period}  |  {display_date}"
        )

        # สร้างตาราง
        self.tree.delete(*self.tree.get_children())

        overall_pass = True
        current_group = None

        for item in items:
            # group header row
            if item["group_id"] != current_group:
                current_group = item["group_id"]
                self.tree.insert("", "end",
                                  values=(item["group_title"], "", ""),
                                  tags=("group",))

            ans = answers.get(item["item_id"])
            if ans:
                result_text = "ผ่าน" if ans["passed"] else "ไม่ผ่าน"
                tag = "pass" if ans["passed"] else "fail"
                notes = ans.get("notes", "")
                if ans.get("failed_channels"):
                    fc = ans["failed_channels"]
                    if item.get("question_type") == "yes_no_channels_text":
                        ch_str = ", ".join(str(c) for c in fc)
                        notes = f"จำนวนภาไที่ Pixel ไม่สม่ำเสมอ: {len(fc)} ภาพ  \nค่า Pixel ของภาพที่ไม่เห็น: {ch_str}" + (f"  {notes}" if notes else "")
                    else:
                        ch_str = ", ".join(str(c) for c in fc)
                        notes = f"ค่า Pixel ของช่องที่ไม่เห็น: {ch_str}" + (f"  {notes}" if notes else "")
                if not ans["passed"]:
                    overall_pass = False
            else:
                result_text = "ไม่ได้ตอบ"
                tag = "no_ans"
                notes = ""
                overall_pass = False

            self.tree.insert("", "end",
                              values=(f"  {item['title']}", result_text, notes),
                              tags=(tag,))

        session["overall_pass"] = overall_pass

    # ── actions ───────────────────────────────────────────────────────

    def _save(self):
        self.app.show("after_save")

    def _discard(self):
        self.app.session.clear()
        self.app.show("home")

    def _print_dialog(self):
        from tkinter import filedialog, messagebox
        from screens.base import CARD_COLOR, TEXT_COLOR, BORDER_CLR, ENTRY_BG, thai_font
        from config import TEST_CONFIG
        from reports.pdf_export import export_history_result

        session = self.app.session

        dlg = tk.Toplevel(self.app)
        dlg.title("บันทึก PDF")
        dlg.configure(bg=CARD_COLOR)
        dlg.resizable(False, False)
        dlg.transient(self.app)
        dlg.grab_set()
        w, h = int(400 * self._s), int(200 * self._s)
        px = self.app.winfo_x() + self.app.winfo_width()  // 2 - w // 2
        py = self.app.winfo_y() + self.app.winfo_height() // 2 - h // 2
        dlg.geometry(f"{w}x{h}+{px}+{py}")

        tk.Label(dlg, text="จำนวนชุดที่ต้องการ", font=thai_font(self.fs(26), "bold"),
                 bg=CARD_COLOR, fg=TEXT_COLOR).pack(pady=(20, 8))

        spin_var = tk.IntVar(value=1)
        tk.Spinbox(dlg, from_=1, to=99, textvariable=spin_var,
                   font=thai_font(self.fs(26)), width=6, justify="center",
                   bg=ENTRY_BG, fg=TEXT_COLOR, relief="sunken", bd=2).pack()

        err_lbl = tk.Label(dlg, text="", font=thai_font(self.fs(20)), bg=CARD_COLOR, fg="#cc0000")
        err_lbl.pack(pady=(4, 0))

        btn_bar = tk.Frame(dlg, bg=CARD_COLOR)
        btn_bar.pack(pady=12)

        def save():
            import os
            copies = spin_var.get()
            ev = {
                "hospital_name":  session.get("hospital_name", ""),
                "evaluator_name": session.get("evaluator_name", ""),
                "eval_datetime":  session.get("eval_datetime", ""),
                "screen_type":    session.get("screen_type", ""),
                "period":         session.get("period", ""),
                "answers":        session.get("answers", {}),
            }
            groups = TEST_CONFIG.get(ev["screen_type"], {}).get(ev["period"], [])
            base_name = (f"ผลการประเมิน_{ev['hospital_name']}_{ev['eval_datetime']}"
                         .replace(" ", "_").replace(":", "-"))

            if copies == 1:
                path = filedialog.asksaveasfilename(
                    parent=dlg, defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"{base_name}.pdf",
                )
                if not path:
                    return
                paths = [path]
            else:
                folder = filedialog.askdirectory(parent=dlg, title="เลือกโฟลเดอร์ที่จะบันทึก")
                if not folder:
                    return
                paths = [os.path.join(folder, f"{base_name}_{i+1}.pdf")
                         for i in range(copies)]

            try:
                for path in paths:
                    export_history_result(ev, groups, path)
                dlg.destroy()
                messagebox.showinfo("บันทึกสำเร็จ",
                                    f"บันทึก PDF {copies} ชุด เรียบร้อย")
            except Exception as e:
                err_lbl.configure(text=f"ไม่สามารถสร้าง PDF ได้: {e}")

        self.primary_btn(btn_bar, "บันทึก PDF", save,
                         fontsize=self.fs(24), width=14).pack(side="left", padx=(0, 8))
        self.primary_btn(btn_bar, "ยกเลิก", dlg.destroy,
                         fontsize=self.fs(24), width=10).pack(side="left")

    def _retest(self):
        session = self.app.session
        session["current_item_idx"] = 0
        session["answers"] = {}
        self.app.show("test_runner")
