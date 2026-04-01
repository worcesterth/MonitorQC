import os
import platform
import subprocess
import tempfile
import tkinter as tk
from tkinter import ttk
from screens.base import (
    BaseScreen, BG_COLOR, CARD_COLOR, TEXT_COLOR, BORDER_CLR, thai_font,
)
from config import SCREEN_TYPES, PERIODS, PERIOD_LABELS
import database


def _send_to_printer(path: str):
    """ส่งไฟล์ PDF ไปยังเครื่องพิมพ์ default"""
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


class HistoryScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        self.card_header(self, "ประวัติการทดสอบ", size=24)

        # ── search bar ────────────────────────────────────────────────────
        search_bar = tk.Frame(self, bg=BG_COLOR)
        search_bar.pack(fill="x", padx=20, pady=(8, 4))

        tk.Label(search_bar, text="ชื่อผู้ประเมิน:", font=thai_font(26),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.hospital_var = tk.StringVar()
        hospital_entry = tk.Entry(search_bar, textvariable=self.hospital_var,
                                  font=thai_font(26), width=20,
                                  bg="#ffffff", relief="sunken", bd=2)
        hospital_entry.pack(side="left", padx=(4, 16))

        tk.Label(search_bar, text="ชนิดหน้าจอ:", font=thai_font(26),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.type_var = tk.StringVar(value="")
        type_choices = [("ทั้งหมด", "")] + [(v.split("(")[0].strip(), k)
                                              for k, v in SCREEN_TYPES.items()]
        self._type_menu = self._build_optionmenu(search_bar, self.type_var,
                                                  type_choices)
        self._type_menu.pack(side="left", padx=(4, 16))

        tk.Label(search_bar, text="รอบ:", font=thai_font(26),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")
        self.period_var = tk.StringVar(value="")
        period_choices = [("ทั้งหมด", "")] + [(v, k) for k, v in PERIOD_LABELS.items()]
        self._period_menu = self._build_optionmenu(search_bar, self.period_var,
                                                    period_choices)
        self._period_menu.pack(side="left", padx=(4, 16))

        search_icon = tk.Label(search_bar, text="🔍", font=thai_font(26),
                               bg=BG_COLOR, cursor="hand2")
        search_icon.pack(side="left", padx=4)
        search_icon.bind("<ButtonRelease-1>", lambda _: self._search())

        # ── table ─────────────────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(4, 12))

        style = ttk.Style()
        style.configure("History.Treeview",
                         font=thai_font(26),
                         rowheight=36,
                         background=CARD_COLOR,
                         fieldbackground=CARD_COLOR,
                         foreground=TEXT_COLOR)
        style.configure("History.Treeview.Heading",
                         font=thai_font(26, "bold"),
                         background=BG_COLOR,
                         foreground=TEXT_COLOR,
                         relief="flat")
        style.map("History.Treeview",
                  background=[("selected", "#b0c8e8")])

        cols = ("วันที่", "โรงพยาบาล", "ชนิด", "รอบ", "ผู้ประเมิน", "รุ่นหน้าจอ")
        self.tree = ttk.Treeview(table_frame, columns=cols,
                                  show="headings", style="History.Treeview",
                                  selectmode="extended")

        widths  = [220, 240, 160, 150, 180, 200]
        anchors = ["center", "w", "center", "center", "w", "w"]
        for col, w, a in zip(cols, widths, anchors):
            self.tree.heading(col, text=col, anchor=a)
            self.tree.column(col, width=w, anchor=a, stretch=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)

        # ── bottom bar ────────────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=BG_COLOR)
        btn_bar.pack(side="bottom", fill="x", padx=20, pady=12)

        self.primary_btn(btn_bar, "ดูรายละเอียด",
                         self._view_selected, fontsize=26, width=14).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "ดาวน์โหลด PDF",
                         self._download_selected, fontsize=26, width=16).pack(side="left", padx=4)
        self.primary_btn(btn_bar, "พิมพ์",
                         self._print_selected, fontsize=26, width=10).pack(side="left", padx=4)
        self._hint_lbl = tk.Label(btn_bar, text="", font=thai_font(22),
                                  bg=BG_COLOR, fg="#cc0000")
        self._hint_lbl.pack(side="left", padx=8)
        self.back_btn(btn_bar, "กลับหน้าหลัก",
                      lambda: app.show("home"), fontsize=26, width=14).pack(side="right", padx=4)

        self._rows: list[dict] = []

    # ── helpers ───────────────────────────────────────────────────────────

    def _build_optionmenu(self, parent, var, choices):
        labels = [c[0] for c in choices]
        values = [c[1] for c in choices]
        var.set(values[0])

        wrapper = tk.Frame(parent, bg=BORDER_CLR)
        display_var = tk.StringVar(value=labels[0])
        inner = tk.Label(wrapper, textvariable=display_var, font=thai_font(26),
                          bg="#ffffff", fg=TEXT_COLOR, padx=6, pady=2, cursor="hand2")

        def pick(lbl, val):
            var.set(val)
            display_var.set(lbl)
            menu.unpost()

        menu = tk.Menu(wrapper, tearoff=0, font=thai_font(26))
        for lbl, val in zip(labels, values):
            menu.add_command(label=lbl, command=lambda l=lbl, v=val: pick(l, v))

        def show_menu(e):
            try:
                menu.tk_popup(inner.winfo_rootx(), inner.winfo_rooty() + inner.winfo_height())
            finally:
                menu.grab_release()

        inner.bind("<ButtonRelease-1>", show_menu)
        inner.pack(padx=1, pady=1)
        return wrapper

    # ── on_show ───────────────────────────────────────────────────────────

    def on_show(self, **_):
        self._search()

    def _search(self):
        rows = database.search_evaluations(
            evaluator=self.hospital_var.get().strip(),
            screen_type=self.type_var.get(),
            period=self.period_var.get(),
        )
        self._rows = rows
        self.tree.delete(*self.tree.get_children())

        type_map   = {"diagnostic": "Diagnostic", "modality": "Modality", "clinic": "Clinical"}
        period_map = {"monthly": "รายเดือน", "quarterly": "ราย 3 เดือน", "annual": "ประจำปี"}

        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["eval_datetime"],
                r["hospital_name"],
                type_map.get(r["screen_type"], r["screen_type"]),
                period_map.get(r["period"], r["period"]),
                r["evaluator_name"],
                r["screen_model"],
            ))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _on_double_click(self, _event):
        self._view_selected()

    def _download_selected(self):
        from tkinter import filedialog, messagebox
        from config import TEST_CONFIG
        from reports.pdf_export import export_history_result
        import os

        ids = [int(iid) for iid in self.tree.selection()]
        if not ids:
            self._hint_lbl.configure(text="กรุณาเลือกรายการที่ต้องการดาวน์โหลดก่อน")
            return
        self._hint_lbl.configure(text="")

        if len(ids) == 1:
            ev = database.get_evaluation(ids[0])
            if not ev:
                return
            groups = TEST_CONFIG.get(ev["screen_type"], {}).get(ev["period"], [])
            default = (f"ผลการประเมิน_{ev['hospital_name']}_{ev['eval_datetime']}.pdf"
                       .replace(" ", "_").replace(":", "-"))
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=default,
            )
            if not path:
                return
            try:
                r = database.get_eval_rank(ev["screen_type"], ev["period"], ev["id"])
                export_history_result(ev, groups, path, rank=r)
                messagebox.showinfo("บันทึกสำเร็จ", f"บันทึก PDF เรียบร้อย\n{path}")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", str(e))
        else:
            folder = filedialog.askdirectory(title=f"เลือกโฟลเดอร์บันทึก PDF {len(ids)} ชุด")
            if not folder:
                return
            errors = []
            for eval_id in ids:
                ev = database.get_evaluation(eval_id)
                if not ev:
                    continue
                groups = TEST_CONFIG.get(ev["screen_type"], {}).get(ev["period"], [])
                fname = (f"ผลการประเมิน_{ev['hospital_name']}_{ev['eval_datetime']}.pdf"
                         .replace(" ", "_").replace(":", "-"))
                try:
                    r = database.get_eval_rank(ev["screen_type"], ev["period"], ev["id"])
                    export_history_result(ev, groups, os.path.join(folder, fname), rank=r)
                except Exception as e:
                    errors.append(f"{fname}: {e}")
            if errors:
                messagebox.showerror("ข้อผิดพลาด", "\n".join(errors))
            else:
                messagebox.showinfo("บันทึกสำเร็จ",
                                    f"บันทึก PDF {len(ids)} ไฟล์ เรียบร้อย\nโฟลเดอร์: {folder}")

    def _print_selected(self):
        from config import TEST_CONFIG
        from reports.pdf_export import export_history_result

        ids = [int(iid) for iid in self.tree.selection()]
        if not ids:
            self._hint_lbl.configure(text="กรุณาเลือกรายการที่ต้องการพิมพ์ก่อน")
            return
        self._hint_lbl.configure(text="")

        from tkinter import messagebox
        if not messagebox.askyesno("ยืนยันการพิมพ์", f"ต้องการพิมพ์รายการที่เลือก {len(ids)} ชุด ใช่หรือไม่?"):
            return
        try:
            for eval_id in ids:
                ev = database.get_evaluation(eval_id)
                if not ev:
                    continue
                groups = TEST_CONFIG.get(ev["screen_type"], {}).get(ev["period"], [])
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    tmp = f.name
                r = database.get_eval_rank(ev["screen_type"], ev["period"], ev["id"])
                export_history_result(ev, groups, tmp, rank=r)
                _send_to_printer(tmp)
            messagebox.showinfo("ส่งพิมพ์สำเร็จ", f"ส่งรายการพิมพ์ {len(ids)} ชุด เรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถพิมพ์ได้\n{e}")

    def _view_selected(self):
        eval_id = self._selected_id()
        if eval_id is None:
            self._hint_lbl.configure(text="กรุณาเลือกรายการก่อน หรือดับเบิลคลิกที่แถว")
            return
        self._hint_lbl.configure(text="")
        ev = database.get_evaluation(eval_id)
        if not ev:
            return
        self.app.session["history_eval"] = ev
        self.app.show("history_result")
