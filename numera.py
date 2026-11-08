"""NUMERA Pixel Edition — a converter and binary calculator by Dash #3.

Copyright (c) 2026 Dash #3. All rights reserved.
Run with Python 3.8+ and Tkinter. No third-party packages required.
"""

import sys
import os
import tkinter as tk
from tkinter import font as tkfont
import unicodedata
from fractions import Fraction

__author__ = "Dash #3"
__version__ = "2.1.0"
COPYRIGHT = "© 2026 Dash #3"
DIGITS = "0123456789ABCDEF"
BASES = {
    10: ("DECIMAL", "عشري", "255"),
    2: ("BINARY", "ثنائي", "11111111"),
    8: ("OCTAL", "ثماني", "377"),
    16: ("HEXADECIMAL", "ست عشري", "FF"),
}
OPERATIONS = {"+": "+", "-": "−", "*": "×", "/": "÷"}

# Change the theme here. Pixel artwork is drawn directly, without font files.
BG = "#080F1B"
PANEL = "#101B2D"
FIELD = "#0B1423"
BORDER = "#2B3D57"
TEXT = "#E9F0FC"
MUTED = "#A0B2CB"
ACCENT = "#6AF0C6"
ACCENT_DARK = "#153C36"
ERROR = "#FF93A5"

PIXEL_FONT = {
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    " ": ("000",) * 7,
}


# ==================== Conversion ====================
def check_base(base):
    if type(base) is not int or base not in BASES:
        raise ValueError("الأساس يجب أن يكون 2 أو 8 أو 10 أو 16")


def normalize_digits(text):
    result = []
    for ch in text:
        try:
            result.append(str(unicodedata.decimal(ch)))
        except ValueError:
            result.append(ch)
    return "".join(result)


def from_decimal(n, base):
    check_base(base)
    if type(n) is not int:
        raise ValueError("التحويل يدعم الأعداد الصحيحة فقط")
    if n == 0:
        return "0"
    negative = n < 0
    n = abs(n)
    result = []
    while n:
        n, remainder = divmod(n, base)
        result.append(DIGITS[remainder])
    return ("-" if negative else "") + "".join(reversed(result))


def to_decimal(s, base):
    check_base(base)
    s = normalize_digits(s.strip()).upper()
    if not s:
        raise ValueError("أدخل رقمًا أولًا")
    negative = s.startswith("-")
    if s[:1] in {"-", "+"}:
        s = s[1:]
    if not s:
        raise ValueError("أدخل رقمًا بعد الإشارة")
    result = 0
    for ch in s:
        val = DIGITS.find(ch)
        if not 0 <= val < base:
            raise ValueError(f"الرمز {ch!r} غير صالح للأساس {base}")
        result = result * base + val
    return -result if negative else result


def calculate_binary(left, right, operation):
    """Exact arithmetic on two signed binary integers; no float or eval."""
    if operation not in OPERATIONS:
        raise ValueError("اختر إحدى العمليات الأربع")
    numbers = []
    for text, label in ((left, "الرقم الأول"), (right, "الرقم الثاني")):
        try:
            numbers.append(to_decimal(text, 2))
        except ValueError as exc:
            raise ValueError(f"{label}: {exc}") from exc
    a, b = numbers
    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "*":
        return a * b
    if b == 0:
        raise ValueError("لا يمكن القسمة على صفر")
    return Fraction(a, b)


def format_number(value, base):
    """Format exact fractions, using parentheses for repeating digits.

    Fall back to an exact numerator/denominator after 64 fractional digits,
    rather than silently rounding or dropping part of the result.
    """
    check_base(base)
    if type(value) is int:
        return from_decimal(value, base)
    if not isinstance(value, Fraction):
        raise ValueError("القيمة يجب أن تكون عددًا صحيحًا أو كسرًا دقيقًا")
    if value.denominator == 1:
        return from_decimal(value.numerator, base)
    sign = "-" if value < 0 else ""
    whole, remainder = divmod(abs(value.numerator), value.denominator)
    prefix = sign + from_decimal(whole, base) + "."
    digits, seen = [], {}
    while remainder:
        if remainder in seen:
            start = seen[remainder]
            return prefix + "".join(digits[:start]) + "(" + "".join(digits[start:]) + ")"
        if len(digits) >= 64:
            return from_decimal(value.numerator, base) + "/" + from_decimal(value.denominator, base)
        seen[remainder] = len(digits)
        digit, remainder = divmod(remainder * base, value.denominator)
        digits.append(DIGITS[digit])
    return prefix + "".join(digits)


# ==================== Desktop interface ====================
class NumeraApp(tk.Tk):
    def __init__(self):
        # Prevent Windows from enlarging the whole window beyond the screen.
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                pass
        super().__init__()
        self.title("NUMERA Pixel Edition — Dash #3")
        self.configure(bg=BG)
        available_width, available_height = self.winfo_screenwidth(), self.winfo_screenheight()
        if os.name == "nt":
            try:
                from ctypes import wintypes
                work_area = wintypes.RECT()
                if ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(work_area), 0):
                    available_width = work_area.right - work_area.left
                    available_height = work_area.bottom - work_area.top
            except (AttributeError, OSError):
                pass
        self.scale = max(0.65, min(self.winfo_fpixels("1i") / 96,
                                  (available_width - 70) / 1000,
                                  (available_height - 80) / 660))
        self.geometry(f"{self.px(1000)}x{self.px(660)}+{self.px(24)}+{self.px(20)}")
        self.minsize(self.px(860), self.px(610))

        fonts = set(tkfont.families(self))
        self.ui_font = "Segoe UI" if "Segoe UI" in fonts else "DejaVu Sans" if "DejaVu Sans" in fonts else "Arial"
        self.mono_font = "Consolas" if "Consolas" in fonts else "DejaVu Sans Mono" if "DejaVu Sans Mono" in fonts else "Courier"
        self.input_value = tk.StringVar()
        self.second_value = tk.StringVar()
        self.base_value = tk.IntVar(value=10)
        self.mode_value = tk.StringVar(value="convert")
        self.operation_value = tk.StringVar(value="+")
        self.quotient_value = tk.StringVar()
        self.remainder_value = tk.StringVar()
        self.status_value = tk.StringVar(value="اختر النظام، ثم أدخل الرقم واضغط تحويل")
        self.result_values = {base: tk.StringVar() for base in BASES}
        self.copy_buttons = {}
        self.source_buttons = {}
        self.result_cards = {}
        self.result_entries = {}
        self.mode_buttons = {}
        self.operation_buttons = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.hero = tk.Canvas(self, height=self.px(132), bg=BG, highlightthickness=0)
        self.hero.grid(row=0, column=0, sticky="ew", padx=24, pady=(8, 0))
        self.hero.bind("<Configure>", self._draw_hero)

        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        body.columnconfigure(0, weight=2, minsize=self.px(310))
        body.columnconfigure(1, weight=3, minsize=self.px(440))
        body.rowconfigure(0, weight=1)
        self._build_input(body)
        self._build_results(body)

        footer = tk.Frame(self, bg=BG)
        footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 15))
        footer.columnconfigure(1, weight=1)
        self._label(footer, COPYRIGHT, color=ACCENT, mono=True).grid(row=0, column=0, sticky="w")
        self._label(footer, "NUMERA  /  PIXEL EDITION  /  2.1", mono=True, size=9).grid(row=0, column=1, sticky="e")

        self.input_value.trace_add("write", self._invalidate)
        self.second_value.trace_add("write", self._invalidate)
        self.base_value.trace_add("write", self._base_changed)
        self.mode_value.trace_add("write", self._mode_changed)
        self.operation_value.trace_add("write", self._operation_changed)
        self.bind("<Return>", self._on_return)
        self.bind("<Escape>", lambda event: self.clear())
        self.bind("<Control-l>", self._focus_input)
        self._style_sources()
        self._mode_changed()
        self.after_idle(self.input_entry.focus_set)

    def _label(self, parent, text="", color=MUTED, size=10, bold=False, mono=False, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=self.font(size, mono, bold),
                        **kwargs)

    def px(self, value):
        return max(1, round(value * self.scale))

    def font(self, size, mono=False, bold=False):
        return (self.mono_font if mono else self.ui_font, -self.px(size * 4 / 3),
                "bold" if bold else "normal")

    def _button(self, parent, text, command, primary=False, **kwargs):
        return tk.Button(
            parent, text=text, command=command, font=self.font(11, bold=True),
            bg=ACCENT if primary else FIELD, fg=BG if primary else TEXT,
            activebackground="#A5FFDF" if primary else ACCENT_DARK,
            activeforeground=BG if primary else ACCENT,
            disabledforeground="#60728D", relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT,
            cursor="hand2", padx=10, pady=7, takefocus=True, **kwargs)

    def _build_input(self, body):
        panel = tk.Frame(body, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(9, weight=1)
        modes = tk.Frame(panel, bg=PANEL)
        modes.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        for index, (mode, label) in enumerate((("convert", "تحويل الأنظمة"), ("binary", "حساب الباينري"))):
            modes.columnconfigure(index, weight=1, uniform="mode")
            button = self._button(modes, label, lambda m=mode: self.set_mode(m))
            button.grid(row=0, column=index, sticky="ew", padx=(0, 4) if index == 0 else (4, 0))
            self.mode_buttons[mode] = button
        heading = tk.Frame(panel, bg=PANEL)
        heading.grid(row=1, column=0, sticky="ew", padx=18, pady=(12, 10))
        heading.columnconfigure(1, weight=1)
        self.input_heading = self._label(heading, "01 / INPUT", color=ACCENT, mono=True, size=10)
        self.input_heading.grid(row=0, column=0, sticky="w")
        self.source_heading = self._label(heading, "النظام المصدر", color=TEXT, bold=True)
        self.source_heading.grid(row=0, column=1, sticky="e")

        sources = tk.Frame(panel, bg=PANEL)
        sources.grid(row=2, column=0, sticky="ew", padx=18)
        self.sources_panel = sources
        for col in (0, 1):
            sources.columnconfigure(col, weight=1, uniform="source")
        for index, (base, (name, arabic, _)) in enumerate(BASES.items()):
            button = self._button(sources, f"{name[:3]} / {base}\n{arabic}", lambda b=base: self.select_base(b))
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=(0, 6) if index % 2 == 0 else (6, 0), pady=(0, 10))
            self.source_buttons[base] = button

        self.operations_panel = tk.Frame(panel, bg=PANEL)
        self.operations_panel.grid(row=2, column=0, sticky="ew", padx=18)
        for index, (operation, symbol) in enumerate(OPERATIONS.items()):
            self.operations_panel.columnconfigure(index, weight=1, uniform="operation")
            button = self._button(self.operations_panel, symbol, lambda op=operation: self.set_operation(op))
            button.grid(row=0, column=index, sticky="ew", padx=(0, 5) if index < 3 else 0)
            self.operation_buttons[operation] = button

        self.first_label = self._label(panel, "الرقم المراد تحويله", color=TEXT, bold=True, anchor="e")
        self.first_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 5))
        self.input_entry = tk.Entry(panel, textvariable=self.input_value, width=12,
                                    font=self.font(20, mono=True), bg=FIELD, fg=TEXT,
                                    insertbackground=ACCENT, selectbackground=ACCENT_DARK,
                                    selectforeground=TEXT, relief="flat", bd=8,
                                    highlightthickness=1, highlightbackground=BORDER,
                                    highlightcolor=ACCENT, justify="left")
        self.input_entry.grid(row=4, column=0, sticky="ew", padx=18)
        self.input_entry.bind("<Control-a>", self._select_all)
        self.example_label = self._label(panel, "Example: 255  /  -255", mono=True, size=9, anchor="w")
        self.example_label.grid(row=5, column=0, sticky="ew", padx=18, pady=(5, 8))

        self.second_panel = tk.Frame(panel, bg=PANEL)
        self.second_panel.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.second_panel.columnconfigure(0, weight=1)
        self._label(self.second_panel, "الرقم الثاني", color=TEXT, bold=True, anchor="e").grid(
            row=0, column=0, sticky="ew", pady=(0, 5))
        self.second_entry = tk.Entry(self.second_panel, textvariable=self.second_value, width=12,
                                     font=self.font(20, mono=True), bg=FIELD, fg=TEXT,
                                     insertbackground=ACCENT, selectbackground=ACCENT_DARK,
                                     selectforeground=TEXT, relief="flat", bd=8,
                                     highlightthickness=1, highlightbackground=BORDER,
                                     highlightcolor=ACCENT, justify="left")
        self.second_entry.grid(row=1, column=0, sticky="ew")
        self.second_entry.bind("<Control-a>", self._select_all)

        actions = tk.Frame(panel, bg=PANEL)
        actions.grid(row=7, column=0, sticky="ew", padx=18)
        actions.columnconfigure(0, weight=1)
        self.convert_button = self._button(actions, "تحويل  ↵", self.run_action, primary=True)
        self.convert_button.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._button(actions, "مسح", self.clear).grid(row=0, column=1, sticky="ew")
        self.status_label = self._label(panel, textvariable=self.status_value, color=MUTED,
                                       anchor="ne", justify="right", wraplength=290, height=3)
        self.status_label.grid(row=8, column=0, sticky="ew", padx=18, pady=(9, 0))
        panel.bind("<Configure>", lambda event: self.status_label.configure(wraplength=max(120, event.width - 42)))

    def _build_results(self, body):
        panel = tk.Frame(body, bg=BG)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        heading = tk.Frame(panel, bg=BG)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        heading.columnconfigure(1, weight=1)
        self._label(heading, "02 / OUTPUT", color=ACCENT, mono=True, size=10).grid(row=0, column=0)
        self._label(heading, "النتائج", color=TEXT, bold=True, size=12).grid(row=0, column=1, sticky="e")

        for index, (base, (name, _, _)) in enumerate(BASES.items(), start=1):
            panel.rowconfigure(index, weight=1, uniform="result")
            card = tk.Frame(panel, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=index, column=0, sticky="nsew", pady=(0, 9) if index < 4 else 0)
            card.columnconfigure(0, weight=1)
            card.rowconfigure(1, weight=1)
            title = tk.Frame(card, bg=PANEL)
            title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 3))
            title.columnconfigure(1, weight=1)
            self._label(title, name, color=TEXT, size=9, mono=True, bold=True).grid(row=0, column=0, sticky="w")
            self._label(title, f"BASE {base:02}", size=9, mono=True).grid(row=0, column=1, sticky="e")
            entry = tk.Entry(card, textvariable=self.result_values[base], state="readonly", width=12,
                             font=self.font(17, mono=True), readonlybackground=PANEL,
                             fg=ACCENT, selectbackground=ACCENT_DARK, selectforeground=TEXT,
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=PANEL, highlightcolor=ACCENT,
                             exportselection=False, justify="left")
            entry.grid(row=1, column=0, sticky="ew", padx=(12, 6), pady=(0, 8))
            entry.bind("<Control-a>", self._select_all)
            copy = self._button(card, "نسخ", lambda b=base: self.copy_result(b), state="disabled")
            copy.grid(row=1, column=1, padx=(0, 12), pady=(0, 8))
            self.copy_buttons[base] = copy
            self.result_cards[base] = card
            self.result_entries[base] = entry

        self.division_panel = tk.Frame(panel, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        self.division_panel.grid(row=5, column=0, sticky="ew", pady=(9, 0))
        for column, (label, variable) in enumerate((("خارج صحيح (ثنائي)", self.quotient_value),
                                                   ("الباقي (ثنائي)", self.remainder_value))):
            self.division_panel.columnconfigure(column, weight=1, uniform="division")
            cell = tk.Frame(self.division_panel, bg=PANEL)
            cell.grid(row=0, column=column, sticky="ew", padx=12, pady=6)
            cell.columnconfigure(0, weight=1)
            self._label(cell, label, size=9, anchor="e").grid(row=0, column=0, sticky="ew")
            entry = tk.Entry(cell, textvariable=variable, width=8, state="readonly",
                             font=self.font(13, mono=True), readonlybackground=PANEL, fg=ACCENT,
                             relief="flat", bd=0, selectbackground=ACCENT_DARK,
                             selectforeground=TEXT, exportselection=False)
            entry.grid(row=1, column=0, sticky="ew", pady=(3, 0))
            entry.bind("<Control-a>", self._select_all)
        self.division_panel.grid_remove()

    def _draw_hero(self, event):
        canvas = self.hero
        canvas.delete("all")
        for x in range(3, event.width, self.px(16)):
            for y in range(self.px(7), self.px(122), self.px(16)):
                canvas.create_rectangle(x, y, x + 1, y + 1, fill="#24334B", outline="")
        canvas.create_text(8, self.px(18), anchor="w", text="A TOOL BY", fill=MUTED, font=self.font(9, mono=True))
        step, dot, x0, y0 = self.px(6), self.px(4), 8, self.px(40)
        for char in __author__.upper():
            glyph = PIXEL_FONT[char]
            for y, row in enumerate(glyph):
                for x, bit in enumerate(row):
                    if bit == "1":
                        px, py = x0 + x * step, y0 + y * step
                        canvas.create_rectangle(px + 2, py + 2, px + dot + 2, py + dot + 2, fill="#204C45", outline="")
                        canvas.create_rectangle(px, py, px + dot, py + dot, fill=ACCENT, outline="")
            x0 += (len(glyph[0]) + 1) * step
        canvas.create_text(8, self.px(103), anchor="w", text="NUMERA / PIXEL EDITION", fill=MUTED, font=self.font(9, mono=True))
        canvas.create_text(event.width - 8, self.px(52), anchor="e", text="محوّل الأعداد وحاسبة الباينري", fill=TEXT, font=self.font(18, bold=True))
        canvas.create_text(event.width - 8, self.px(86), anchor="e", text="CONVERTER  /  BINARY CALCULATOR", fill=MUTED, font=self.font(10, mono=True))

    def _style_sources(self):
        base = self.base_value.get()
        for value, button in self.source_buttons.items():
            selected = value == base
            button.configure(bg=ACCENT_DARK if selected else FIELD,
                             fg=ACCENT if selected else MUTED,
                             highlightbackground=ACCENT if selected else BORDER,
                             relief="sunken" if selected else "flat")
        if self.mode_value.get() == "convert":
            example = BASES[base][2]
            self.example_label.configure(text=f"Example: {example}  /  -{example}")

    def set_mode(self, mode):
        if mode not in {"convert", "binary"}:
            raise ValueError("الوضع غير صالح")
        self.mode_value.set(mode)
        self.input_entry.focus_set()

    def set_operation(self, operation):
        if operation not in OPERATIONS:
            raise ValueError("اختر إحدى العمليات الأربع")
        self.operation_value.set(operation)
        self.input_entry.focus_set()

    def _mode_changed(self, *_):
        binary = self.mode_value.get() == "binary"
        for mode, button in self.mode_buttons.items():
            selected = mode == self.mode_value.get()
            button.configure(bg=ACCENT_DARK if selected else FIELD,
                             fg=ACCENT if selected else MUTED,
                             highlightbackground=ACCENT if selected else BORDER)
        if binary:
            self.sources_panel.grid_remove()
            self.operations_panel.grid()
            self.second_panel.grid()
            self.input_heading.configure(text="01 / BINARY")
            self.source_heading.configure(text="العملية الحسابية")
            self.first_label.configure(text="الرقم الأول")
            self.example_label.configure(text="BINARY / BASE 02  |  1011 / -1011")
            self.convert_button.configure(text="احسب  ↵")
        else:
            self.operations_panel.grid_remove()
            self.second_panel.grid_remove()
            self.sources_panel.grid()
            self.input_heading.configure(text="01 / INPUT")
            self.source_heading.configure(text="النظام المصدر")
            self.first_label.configure(text="الرقم المراد تحويله")
            self.convert_button.configure(text="تحويل  ↵")
            self._style_sources()
        self._operation_changed()

    def _operation_changed(self, *_):
        for operation, button in self.operation_buttons.items():
            selected = operation == self.operation_value.get()
            button.configure(bg=ACCENT_DARK if selected else FIELD,
                             fg=ACCENT if selected else MUTED,
                             highlightbackground=ACCENT if selected else BORDER)
        if self.mode_value.get() == "binary" and self.operation_value.get() == "/":
            self.division_panel.grid()
        else:
            self.division_panel.grid_remove()
        self._invalidate()

    def _invalidate(self, *_):
        for base, value in self.result_values.items():
            value.set("")
            self.copy_buttons[base].configure(state="disabled")
            self.result_cards[base].configure(highlightbackground=BORDER)
        self.input_entry.configure(highlightbackground=BORDER, highlightcolor=ACCENT)
        self.second_entry.configure(highlightbackground=BORDER, highlightcolor=ACCENT)
        self.quotient_value.set("")
        self.remainder_value.set("")
        self.status_label.configure(fg=MUTED)
        self.status_value.set("أدخل رقمين ثنائيين واضغط احسب" if self.mode_value.get() == "binary"
                              else "جاهز للتحويل · الأرقام العربية مقبولة أيضًا")

    def _base_changed(self, *_):
        self._invalidate()
        self._style_sources()

    def select_base(self, base):
        check_base(base)
        self.base_value.set(base)
        self.input_entry.focus_set()

    def convert(self):
        self._invalidate()
        try:
            number = to_decimal(self.input_value.get(), self.base_value.get())
        except ValueError as exc:
            self.status_label.configure(fg=ERROR)
            self.status_value.set(str(exc))
            self.input_entry.configure(highlightbackground=ERROR, highlightcolor=ERROR)
            self.input_entry.focus_set()
            return
        for base, value in self.result_values.items():
            value.set(from_decimal(number, base))
            self.result_entries[base].xview_moveto(0)
            self.copy_buttons[base].configure(state="normal")
        self.result_cards[self.base_value.get()].configure(highlightbackground=ACCENT)
        self.status_label.configure(fg=ACCENT)
        self.status_value.set("تم التحويل · الإطار المضيء يحدّد النظام المصدر")

    def run_action(self):
        if self.mode_value.get() == "binary":
            self.calculate()
        else:
            self.convert()

    def calculate(self):
        self._invalidate()
        numbers = []
        for variable, entry, label in ((self.input_value, self.input_entry, "الرقم الأول"),
                                       (self.second_value, self.second_entry, "الرقم الثاني")):
            try:
                numbers.append(to_decimal(variable.get(), 2))
            except ValueError as exc:
                self._calculation_error(f"{label}: {exc}", entry)
                return
        try:
            number = calculate_binary(self.input_value.get(), self.second_value.get(), self.operation_value.get())
        except ValueError as exc:
            self._calculation_error(str(exc), self.second_entry)
            return
        for base, variable in self.result_values.items():
            variable.set(format_number(number, base))
            self.result_entries[base].xview_moveto(0)
            self.copy_buttons[base].configure(state="normal")
        self.result_cards[2].configure(highlightbackground=ACCENT)
        if self.operation_value.get() == "/":
            a, b = numbers
            quotient = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                quotient = -quotient
            self.quotient_value.set(from_decimal(quotient, 2))
            self.remainder_value.set(from_decimal(a - b * quotient, 2))
        self.status_label.configure(fg=ACCENT)
        self.status_value.set("تم الحساب · (...) كسر دوري، و / بسط ومقام" if isinstance(number, Fraction)
                              and number.denominator != 1 else "تم الحساب بالباينري بنجاح")

    def _calculation_error(self, message, entry):
        self.status_label.configure(fg=ERROR)
        self.status_value.set(message)
        entry.configure(highlightbackground=ERROR, highlightcolor=ERROR)
        entry.focus_set()

    def clear(self):
        self.input_value.set("")
        self.second_value.set("")
        self._invalidate()
        self.input_entry.focus_set()

    def copy_result(self, base):
        value = self.result_values[base].get()
        if not value:
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.status_label.configure(fg=ACCENT)
        self.status_value.set("تم نسخ القيمة كاملة")

    def _on_return(self, event):
        focused = self.focus_get()
        if isinstance(focused, tk.Button):
            focused.invoke()
        else:
            self.run_action()
        return "break"

    def _focus_input(self, event):
        self.input_entry.focus_set()
        self.input_entry.selection_range(0, tk.END)
        return "break"

    @staticmethod
    def _select_all(event):
        event.widget.selection_range(0, tk.END)
        return "break"


def main():
    try:
        app = NumeraApp()
        app.mainloop()
    except tk.TclError as exc:
        print("تعذّر فتح الواجهة الرسومية. شغّل الملف في بيئة سطح مكتب تدعم Tkinter.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
