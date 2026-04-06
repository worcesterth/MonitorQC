import os
import platform
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk
from screens.base import (
    BaseScreen, BG_COLOR, CARD_COLOR, TEXT_COLOR, BORDER_CLR,
    PASS_GREEN, FAIL_RED, thai_font, bind_treeview_tooltip,
)
from config import TEST_CONFIG


def _send_to_printer(path: str):
    system = platform.system()
    if system == "Darwin":
        result = subprocess.run(["open", "--print", path])
        if result.returncode != 0:
            subprocess.run(["open", path], check=True)
    elif system == "Windows":
        try:
            os.startfile(path, "print")
        except OSError:
            os.startfile(path)
    else:
        subprocess.run(["lp", path], check=True)


class HistoryResultScreen(BaseScreen):
    """Read-only version of results.py — shows a saved evaluation from history."""

    def __init__(self, parent, app):
        super().__init__(parent, app)

    
        self.card_header(self, "ผลการประเมิน (ประวัติ)", size=self.fs(24))

        # ── info bar ──────────────────────────────────────────────────────
        info_bar = tk.Frame(self, bg=BG_COLOR, bd=1, relief="solid")
        info_bar.pack(fill="x", padx=20, pady=(8, 4))
        self.info_lbl = tk.Label(info_bar, text="", font=thai_font(self.fs(26)),
                                  bg=BG_COLOR, fg=TEXT_COLOR)
        self.info_lbl.pack(side="left")

        # ── table ─────────────────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(4, 12))

        style = ttk.Style()
        style.configure("HistRes.Treeview",
                         font=thai_font(self.fs(26)), rowheight=max(22, int(36 * self._s)),
                         background="#FFFFFF", fieldbackground=CARD_COLOR,
                         foreground=TEXT_COLOR)
        style.configure("HistRes.Treeview.Heading",
                         font=thai_font(self.fs(26), "bold"),
                         background="#FFFFFF", foreground=TEXT_COLOR, relief="flat")
        style.map("HistRes.Treeview", background=[("selected", "#b0c8e8")])

        cols = ("หัวข้อการประเมิน", "ผลการประเมิน", "หมายเหตุ")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", style="HistRes.Treeview")
        self.tree.heading("หัวข้อการประเมิน", text="หัวข้อการประเมิน", anchor="w")
        self.tree.heading("ผลการประเมิน",    text="ผลการประเมิน",    anchor="center")
        self.tree.heading("หมายเหตุ",        text="หมายเหตุ",        anchor="w")
        self.tree.column("หัวข้อการประเมิน", width=int(520 * self._s), anchor="w",    stretch=True)
        self.tree.column("ผลการประเมิน",    width=int(140 * self._s), anchor="center", stretch=False)
        self.tree.column("หมายเหตุ",        width=int(260 * self._s), anchor="w",    stretch=True)

        self.tree.tag_configure("pass",   foreground=PASS_GREEN)
        self.tree.tag_configure("fail",   foreground=FAIL_RED)
        self.tree.tag_configure("group",  background="#c8c8c8", font=thai_font(self.fs(26), "bold"))
        self.tree.tag_configure("no_ans", foreground="#888888")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        bind_treeview_tooltip(self.tree)

        # ── bottom bar ────────────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=20, pady=12)

        self.primary_btn(btn_bar, "เปรียบเทียบครั้งก่อนหน้า",
                         self._compare, fontsize=self.fs(26), width=22).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "ดาวน์โหลด PDF",
                         self._export_pdf, fontsize=self.fs(26), width=16).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "พิมพ์",
                         self._print_result, fontsize=self.fs(26), width=10).pack(side="left", padx=4)
        self.back_btn(btn_bar, "กลับประวัติ",
                      lambda: app.show("history"), fontsize=self.fs(26), width=14).pack(side="right", padx=4)

    # ── on_show ───────────────────────────────────────────────────────────

    def on_show(self, **_):
        ev = self.app.session.get("history_eval")
        if not ev:
            return

        import datetime
        import database as _db
        type_map   = {"diagnostic": "Diagnostic", "modality": "Modality", "clinic": "Clinical Review"}
        period_map = {"monthly": "รายเดือน", "quarterly": "ราย 3 เดือน", "annual": "ประจำปี"}
        stype  = type_map.get(ev.get("screen_type", ""), "")
        period = period_map.get(ev.get("period", ""), "")
        self._current_rank = _db.get_eval_rank(ev.get("screen_type", ""), ev.get("period", ""), ev["id"])
        rank = self._current_rank
        baseline_mark = "  ★ Baseline" if ev.get("is_baseline") else ""
        
        eval_dt_str = ev.get('eval_datetime', '')
        try:
            dt_obj = datetime.datetime.strptime(eval_dt_str, "%Y-%m-%d %H:%M:%S")
            display_date = f"{dt_obj.day:02d}/{dt_obj.month:02d}/{dt_obj.year + 543} {dt_obj.strftime('%H:%M:%S')}"
        except Exception:
            display_date = eval_dt_str

        self.info_lbl.configure(
            text=f"โรงพยาบาล: {ev.get('hospital_name','')}  |  ผู้ประเมิน: {ev.get('evaluator_name','')}  |  ครั้งที่ {rank}  |  ประเภท: {stype}  |  รอบ: {period}  |  วันที่: {display_date}{baseline_mark}"
        )

        # rebuild table from TEST_CONFIG
        self.tree.delete(*self.tree.get_children())
        screen_type = ev.get("screen_type", "")
        period_key  = ev.get("period", "")
        groups = TEST_CONFIG.get(screen_type, {}).get(period_key, [])
        answers = ev.get("answers", {})

        for group in groups:
            self.tree.insert("", "end",
                              values=(group["group_title"], "", ""),
                              tags=("group",))
            for item in group["items"]:
                item_id = item["item_id"]
                ans = answers.get(item_id)
                if ans:
                    result_text = "ผ่าน" if ans["passed"] else "ไม่ผ่าน"
                    tag = "pass" if ans["passed"] else "fail"
                    notes = ans.get("notes", "")
                    if ans.get("failed_channels"):
                        fc = ans["failed_channels"]
                        ch_str = ", ".join(str(c) for c in fc)
                        if item.get("question_type") == "yes_no_channels_text":
                            notes = f"จำนวนภาพที่ Pixel ไม่สม่ำเสมอ: {len(fc)} ช่อง  \nค่า Pixel ของช่องที่ไม่เห็น: {ch_str}" + (f"  {notes}" if notes else "")
                        else:
                            notes = f"ค่า Pixel ของช่องที่ไม่เห็น: {ch_str}" + (f"  {notes}" if notes else "")
                else:
                    result_text = "ไม่ได้ตอบ"
                    tag = "no_ans"
                    notes = ""

                self.tree.insert("", "end",
                                  values=(f"  {item['title']}", result_text, notes),
                                  tags=(tag,))

    # ── actions ───────────────────────────────────────────────────────────

    def _print_result(self):
        from tkinter import messagebox
        from reports.pdf_export import export_history_result
        ev = self.app.session.get("history_eval")
        if not ev:
            return
        if not messagebox.askyesno("ยืนยันการพิมพ์", "ต้องการพิมพ์ผลการประเมินนี้ ใช่หรือไม่?"):
            return
        try:
            screen_type = ev.get("screen_type", "")
            period_key  = ev.get("period", "")
            groups = TEST_CONFIG.get(screen_type, {}).get(period_key, [])
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                tmp = f.name
            export_history_result(ev, groups, tmp, rank=getattr(self, "_current_rank", 0))
            _send_to_printer(tmp)
            messagebox.showinfo("ส่งพิมพ์สำเร็จ", "ส่งรายการพิมพ์เรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถพิมพ์ได้\n{e}")

    def _export_pdf(self):
        from tkinter import filedialog, messagebox
        from reports.pdf_export import export_history_result
        ev = self.app.session.get("history_eval")
        if not ev:
            return
        screen_type = ev.get("screen_type", "")
        period_key  = ev.get("period", "")
        groups = TEST_CONFIG.get(screen_type, {}).get(period_key, [])
        default_name = f"ผลการประเมิน_{ev.get('hospital_name','')}_{ev.get('eval_datetime','')}.pdf".replace(" ", "_").replace(":", "-")
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
        )
        if not path:
            return
        try:
            export_history_result(ev, groups, path, rank=getattr(self, "_current_rank", 0))
            messagebox.showinfo("บันทึกสำเร็จ", f"บันทึก PDF เรียบร้อย\n{path}")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถสร้าง PDF ได้\n{e}")

    def _compare(self):
        from tkinter import messagebox
        import database
        import datetime
        from screens.base import CARD_COLOR, TEXT_COLOR, BORDER_CLR, thai_font, ENTRY_BG

        ev = self.app.session.get("history_eval")
        if not ev:
            return

        prev_evals = database.get_evaluations_before(
            ev.get("screen_type", ""), ev.get("period", ""),
            before_id=ev["id"],
        )
        if not prev_evals:
            messagebox.showinfo("เปรียบเทียบ", "นี่คือการประเมินครั้งแรก ยังไม่มีผลก่อนหน้าให้เปรียบเทียบ")
            return

        dlg = tk.Toplevel(self.app)
        dlg.title("เลือกรอบที่ต้องการเปรียบเทียบ")
        dlg.configure(bg=CARD_COLOR)
        dlg.resizable(False, False)
        dlg.transient(self.app)
        dlg.grab_set()

        w, h = int(680 * self._s), int(520 * self._s)
        px = self.app.winfo_x() + self.app.winfo_width()  // 2 - w // 2
        py = self.app.winfo_y() + self.app.winfo_height() // 2 - h // 2
        dlg.geometry(f"{w}x{h}+{px}+{py}")

        tk.Label(dlg, text="เลือกรอบที่ต้องการเทียบ Baseline",
                 font=thai_font(self.fs(26), "bold"), bg=CARD_COLOR,
                 fg=TEXT_COLOR).pack(anchor="w", padx=20, pady=(16, 6))
        tk.Frame(dlg, bg=BORDER_CLR, height=1).pack(fill="x", padx=20)

        lb_frame = tk.Frame(dlg, bg=CARD_COLOR)
        lb_frame.pack(fill="both", expand=True, padx=20, pady=10)

        sb = tk.Scrollbar(lb_frame, orient="vertical")
        lb = tk.Listbox(lb_frame, font=thai_font(self.fs(24)), yscrollcommand=sb.set,
                        bg=ENTRY_BG, fg=TEXT_COLOR, selectbackground="#3b9be8",
                        selectforeground="white", activestyle="none",
                        height=min(8, len(prev_evals)), relief="flat", bd=0)
        sb.configure(command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.pack(side="left", fill="both", expand=True)

        for e in prev_evals:
            try:
                dt_obj = datetime.datetime.strptime(e['eval_datetime'], "%Y-%m-%d %H:%M:%S")
                disp_dt = f"{dt_obj.day:02d}/{dt_obj.month:02d}/{dt_obj.year + 543} {dt_obj.strftime('%H:%M:%S')}"
            except Exception:
                disp_dt = e['eval_datetime']
            lb.insert("end", f"ครั้งที่ {e['rank']}:  {disp_dt}  {e['evaluator_name']}")

        default_idx = len(prev_evals) - 1
        lb.selection_set(default_idx)
        lb.see(default_idx)

        err_lbl = tk.Label(dlg, text="", font=thai_font(self.fs(20)),
                           bg=CARD_COLOR, fg="#cc0000")
        err_lbl.pack(anchor="w", padx=20)

        btn_bar = tk.Frame(dlg, bg=CARD_COLOR)
        btn_bar.pack(fill="x", padx=20, pady=(4, 16))

        def confirm():
            sel = lb.curselection()
            if not sel:
                err_lbl.configure(text="กรุณาเลือกรอบที่ต้องการเทียบ")
                return
            chosen = prev_evals[sel[0]]
            baseline = database.get_evaluation(chosen["id"])
            if not baseline:
                err_lbl.configure(text="ไม่พบข้อมูลรอบที่เลือก")
                return
            dlg.destroy()
            self.app.session["compare_current"]  = ev
            self.app.session["compare_baseline"] = baseline
            self.app.show("comparison")

        self.primary_btn(btn_bar, "ยืนยัน", confirm,
                         fontsize=self.fs(24), width=12).pack(side="left", padx=(0, 8))
        self.primary_btn(btn_bar, "ยกเลิก", dlg.destroy,
                         fontsize=self.fs(24), width=12).pack(side="left")
