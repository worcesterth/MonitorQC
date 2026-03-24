import tkinter as tk
import platform

# ── Colors (Windows-classic palette) ────────────────────────────────────────
BG_COLOR   = "#c4c4c4"
CARD_COLOR = "#dbdbdb"
HEADER_BG  = "#c4c4c4"
TEXT_COLOR = "#000000"
BTN_BG     = "#c4c4c4"
BTN_ACTIVE = "#adadad"
PASS_GREEN = "#1a6e1a"
FAIL_RED   = "#cc0000"
ENTRY_BG   = "#ffffff"
BORDER_CLR = "#888888"

# Fixed card sizes (pixels) — ใช้เหมือนกันทุกหน้า
CARD_W  = 820   # ความกว้าง card มาตรฐาน
CARD_H  = 540   # ความสูง card มาตรฐาน
CARD_HL = 680   # ความสูง card แบบสูง (select_type)


def thai_font(size: int = 14, weight: str = "normal") -> tuple:
    system = platform.system()
    if system == "Darwin":
        families = ["TH Sarabun New", "TH SarabunNew", "Krungthep", "Thonburi", "Arial Unicode MS"]
    elif system == "Windows":
        families = ["TH SarabunNew", "Browallia New", "Cordia New", "Tahoma"]
    else:
        families = ["Garuda", "Norasi", "DejaVu Sans"]

    try:
        import tkinter.font as tkfont
        available = set(tkfont.families())
        family = next((f for f in families if f in available), "TkDefaultFont")
    except Exception:
        family = "TkDefaultFont"

    bold = "bold" if weight == "bold" else "normal"
    return (family, size, bold)


class BaseScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

    def on_show(self, **kwargs):
        pass

    # ── helpers ──────────────────────────────────────────────────────────────

    def _bg(self, parent) -> str:
        try:
            return parent.cget("bg")
        except Exception:
            return CARD_COLOR

    def title_label(self, parent, text: str, size: int = 22):
        return tk.Label(
            parent, text=text,
            font=thai_font(size, "bold"),
            bg=self._bg(parent), fg=TEXT_COLOR,
        )

    def label(self, parent, text: str, size: int = 14,
              bold: bool = False, color: str = TEXT_COLOR,
              wraplength: int = 0, anchor: str = "w", justify: str = "left"):
        return tk.Label(
            parent, text=text,
            font=thai_font(size, "bold" if bold else "normal"),
            bg=self._bg(parent), fg=color,
            wraplength=wraplength, anchor=anchor, justify=justify,
        )

    def primary_btn(self, parent, text: str, command,
                    width: int = 14, height=None, fontsize: int = 13,
                    pady: int = None, padx: int = None):
        _pady = pady if pady is not None else max(10, fontsize // 2)
        _padx = padx if padx is not None else max(16, fontsize)

        # wrapper frame = border
        wrapper = tk.Frame(parent, bg=BORDER_CLR, cursor="hand2")

        btn = tk.Label(
            wrapper, text=text,
            font=thai_font(fontsize),
            bg=BTN_BG, fg=TEXT_COLOR,
            relief="flat",
            highlightthickness=0,
            padx=_padx,
            pady=_pady,
            width=width,
            cursor="hand2",
        )
        btn.pack(padx=1, pady=1)

        for widget in (wrapper, btn):
            widget.bind("<ButtonRelease-1>", lambda _: command())
            widget.bind("<Enter>", lambda _: btn.configure(bg=BTN_ACTIVE))
            widget.bind("<Leave>", lambda _: btn.configure(bg=BTN_BG))

        return wrapper

    def grey_btn(self, parent, text: str, command, width: int = 14, height=None):
        return self.primary_btn(parent, text, command, width)

    def card(self, parent, **kwargs):
        return tk.Frame(
            parent, bg=CARD_COLOR,
            relief="flat",
            highlightbackground=BORDER_CLR,
            highlightthickness=1,
            **kwargs,
        )

    def card_header(self, card, text: str, bg: str = HEADER_BG, size: int = 12):
        hdr = tk.Canvas(card, height=max(31, size + 18), bg=bg, highlightthickness=0)
        hdr.pack(fill="x", side="top")
        h = max(30, size + 17)
        hdr.bind("<Configure>", lambda e: (
            hdr.delete("all"),
            hdr.create_rectangle(0, 0, e.width, h, fill=bg, outline=""),
            hdr.create_line(0, h, e.width, h, fill=BORDER_CLR),
            hdr.create_text(12, h // 2, text=text, font=thai_font(size), fill=TEXT_COLOR, anchor="w"),
        ))
        return hdr

    def entry(self, parent, width: int = 36):
        return tk.Entry(
            parent, font=thai_font(13),
            bg=ENTRY_BG, fg=TEXT_COLOR,
            relief="sunken", bd=2,
            width=width,
        )
