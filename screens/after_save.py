import tkinter as tk
from tkinter import messagebox
from screens.base import (
    BaseScreen, BG_COLOR, CARD_COLOR, TEXT_COLOR, BORDER_CLR,
    thai_font,
)
import database


class AfterSaveScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        card = self.card(self)
        card.place(relx=0.5, rely=0.5, anchor="center", width=700, height=460)

        inner = tk.Frame(card, bg=CARD_COLOR)
        inner.pack(fill="both", expand=True, padx=40, pady=24)

        # ── title (underlined) ─────────────────────────────────────────────
        self.title_lbl = tk.Label(
            inner, text="", font=thai_font(26, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR, anchor="w",
        )
        self.title_lbl.pack(fill="x")
        tk.Frame(inner, bg=TEXT_COLOR, height=2).pack(fill="x", pady=(2, 12))

        # ── period type ────────────────────────────────────────────────────
        self.period_lbl = tk.Label(
            inner, text="", font=thai_font(26),
            bg=CARD_COLOR, fg=TEXT_COLOR, anchor="w",
        )
        self.period_lbl.pack(fill="x", pady=(0, 10))

        # ── labeled fields ─────────────────────────────────────────────────
        fields_frame = tk.Frame(inner, bg=CARD_COLOR)
        fields_frame.pack(fill="x")
        fields_frame.grid_columnconfigure(1, weight=1)

        LABEL_W = 34   # character width for the left label column

        field_defs = [
            ("hospital",  "ชื่อโรงพยาบาล:"),
            ("evaluator", "ชื่อผู้ประเมิน:"),
            ("model",     "ชื่อรุ่น/ยี่ห้อ/หมายเลขจอภาพที่ใช้ในการทดสอบ:"),
            ("datetime",  "วันที่และเวลาในการทดสอบ:"),
        ]
        self._vals: dict[str, tk.Label] = {}
        for r, (key, label_text) in enumerate(field_defs):
            tk.Label(
                fields_frame, text=label_text, font=thai_font(26),
                bg=CARD_COLOR, fg=TEXT_COLOR, anchor="w", width=LABEL_W,
            ).grid(row=r, column=0, sticky="nw", pady=6)

            val = tk.Label(
                fields_frame, text="", font=thai_font(26),
                bg=CARD_COLOR, fg=TEXT_COLOR, anchor="w", justify="left",
                wraplength=300,
            )
            val.grid(row=r, column=1, sticky="nw", padx=(8, 0), pady=6)
            self._vals[key] = val

        # ── bottom buttons ─────────────────────────────────────────────────
        btn_bar = tk.Frame(card, bg=CARD_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=16, pady=16)

        self.primary_btn(btn_bar, "เกณฑ์และวิธีการแก้ไขปัญหา",
                         self._view_results, fontsize=26, width=20).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "ทำการเทียบกับ Baseline",
                         self._compare, fontsize=26, width=18).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "กลับหน้าหลัก",
                         self._home, fontsize=26, width=20).pack(side="right", padx=4)

    # ── on_show ───────────────────────────────────────────────────────────

    def on_show(self, **_):
        session = self.app.session

        # บันทึกถ้ายังไม่ได้บันทึก
        if not session.get("eval_id"):
            try:
                eval_id = database.save_evaluation(session)
                session["eval_id"] = eval_id
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"บันทึกไม่สำเร็จ\n{e}")
                self.app.show("results")
                return

        eval_id    = session.get("eval_id", 0)
        screen_type = session.get("screen_type", "")
        period      = session.get("period", "")
        rank = database.get_eval_rank(screen_type, period, eval_id)
        self.title_lbl.configure(
            text=f"บันทึกข้อมูลการทดสอบครั้งที่ {rank} สำเร็จ"
        )

        period_map = {
            "monthly":   "การประเมินประจำเดือน",
            "quarterly": "การประเมินราย 3 เดือน",
            "annual":    "การประเมินประจำปี",
        }
        self.period_lbl.configure(
            text=period_map.get(session.get("period", ""), "")
        )

        self._vals["hospital"].configure(text=session.get("hospital_name", ""))
        self._vals["evaluator"].configure(text=session.get("evaluator_name", ""))
        self._vals["model"].configure(text=session.get("screen_model", ""))
        self._vals["datetime"].configure(text=session.get("eval_datetime", ""))

    # ── actions ───────────────────────────────────────────────────────────

    def _view_results(self):
        self.app.session["criteria_from"] = "after_save"
        self.app.show("criteria")

    def _compare(self):
        session     = self.app.session
        eval_id     = session.get("eval_id", 0)
        screen_type = session.get("screen_type", "")
        period      = session.get("period", "")

        prev_evals = database.get_evaluations_before(screen_type, period,
                                                     before_id=eval_id)
        if not prev_evals:
            messagebox.showinfo(
                "Baseline",
                "เนื่องจากเป็นการทำการทดสอบครั้งที่ 1 จึงจะนำผลการทดสอบครั้งนี้เป็นค่าพื้นฐานที่วัดได้ในครั้งแรก (Baseline) "
                "ซึ่งจะนำไปใช้ในการเปรียบเทียบผลในครั้งต่อ ๆ ไป",
            )
            return

        self._open_pick_dialog(prev_evals)

    def _open_pick_dialog(self, prev_evals: list):
        from screens.base import CARD_COLOR, TEXT_COLOR, BORDER_CLR, thai_font, ENTRY_BG

        dlg = tk.Toplevel(self.app)
        dlg.title("เลือกรอบที่ต้องการเปรียบเทียบ")
        dlg.configure(bg=CARD_COLOR)
        dlg.resizable(False, False)
        dlg.transient(self.app)
        dlg.grab_set()

        w, h = 680, 520
        px = self.app.winfo_x() + self.app.winfo_width()  // 2 - w // 2
        py = self.app.winfo_y() + self.app.winfo_height() // 2 - h // 2
        dlg.geometry(f"{w}x{h}+{px}+{py}")

        tk.Label(dlg, text="เลือกรอบที่ต้องการเทียบ Baseline",
                 font=thai_font(26, "bold"), bg=CARD_COLOR,
                 fg=TEXT_COLOR).pack(anchor="w", padx=20, pady=(16, 6))
        tk.Frame(dlg, bg=BORDER_CLR, height=1).pack(fill="x", padx=20)

        # listbox
        lb_frame = tk.Frame(dlg, bg=CARD_COLOR)
        lb_frame.pack(fill="both", expand=True, padx=20, pady=10)

        sb = tk.Scrollbar(lb_frame, orient="vertical")
        lb = tk.Listbox(lb_frame, font=thai_font(24), yscrollcommand=sb.set,
                        bg=ENTRY_BG, fg=TEXT_COLOR, selectbackground="#3b9be8",
                        selectforeground="white", activestyle="none",
                        height=min(8, len(prev_evals)), relief="flat", bd=0)
        sb.configure(command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.pack(side="left", fill="both", expand=True)

        # prev_evals[0] = newest, prev_evals[-1] = oldest (8th back)
        for ev in prev_evals:
            lb.insert("end", f"ครั้งที่ {ev['rank']}:  {ev['eval_datetime']}  {ev['evaluator_name']}")

        # default = oldest (index len-1 = ครั้งแรกของกลุ่ม 8)
        default_idx = len(prev_evals) - 1
        lb.selection_set(default_idx)
        lb.see(default_idx)

        err_lbl = tk.Label(dlg, text="", font=thai_font(20),
                           bg=CARD_COLOR, fg="#cc0000")
        err_lbl.pack(anchor="w", padx=20)

        btn_bar = tk.Frame(dlg, bg=CARD_COLOR)
        btn_bar.pack(fill="x", padx=20, pady=(4, 16))

        def confirm():
            sel = lb.curselection()
            if not sel:
                err_lbl.configure(text="กรุณาเลือกรอบที่ต้องการเทียบ")
                return
            chosen_ev = prev_evals[sel[0]]
            baseline  = database.get_evaluation(chosen_ev["id"])
            if not baseline:
                err_lbl.configure(text="ไม่พบข้อมูลรอบที่เลือก")
                return
            current = database.get_evaluation(self.app.session.get("eval_id"))
            dlg.destroy()
            self.app.session["compare_current"]  = current
            self.app.session["compare_baseline"] = baseline
            self.app.show("comparison")

        self.primary_btn(btn_bar, "ยืนยัน", confirm,
                         fontsize=24, width=12).pack(side="left", padx=(0, 8))
        self.primary_btn(btn_bar, "ยกเลิก", dlg.destroy,
                         fontsize=24, width=12).pack(side="left")

    def _home(self):
        self.app.session.clear()
        self.app.show("home")
