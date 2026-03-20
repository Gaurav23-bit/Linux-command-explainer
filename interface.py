"""
interface.py - GUI for Linux Command Explainer & Risk Detector
Flat-layout version: all files in the same directory.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, font as tkfont

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BASE_DIR)

from parser import parse_command
from risk_detector import detect_risks, RISK_COLORS, RISK_ICONS

# ─────────────────────────── Palette ────────────────────────────────────────

P = {
    "bg_dark":      "#0F1117",
    "bg_card":      "#1A1D27",
    "bg_input":     "#13151E",
    "border":       "#2A2D3E",
    "border_focus": "#5865F2",
    "accent":       "#5865F2",
    "accent_hover": "#7289DA",
    "text_primary": "#E8EAF0",
    "text_secondary":"#8B8FA8",
    "text_muted":   "#4A4E6B",
    "green":        "#3ECF6A",
    "yellow":       "#F5C400",
    "orange":       "#FF7A00",
    "red":          "#FF2020",
    "blue":         "#4BB9FF",
}

CATEGORY_COLORS = {
    "COMMAND":  "#5865F2",
    "FLAG":     "#3ECF6A",
    "PATH":     "#FF9F1C",
    "GLOB":     "#A78BFA",
    "PIPE":     "#38BDF8",
    "REDIRECT": "#38BDF8",
    "OPERATOR": "#F472B6",
    "VARIABLE": "#34D399",
    "ARGUMENT": "#8B8FA8",
}

RISK_BADGE = {
    "CRITICAL": "#FF2020",
    "HIGH":     "#FF7A00",
    "MEDIUM":   "#F5C400",
    "LOW":      "#4BB9FF",
    "SAFE":     "#3ECF6A",
}


# ─────────────────────────── Scrollable frame ────────────────────────────────

class _ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg=P["bg_dark"], **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg=bg)
        self.inner.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))


# ─────────────────────────── Main window ─────────────────────────────────────

class CommandExplainerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Linux Command Explainer & Risk Detector")
        self.geometry("920x740")
        self.minsize(680, 520)
        self.configure(bg=P["bg_dark"])
        self._fonts()
        self._build()
        self._shortcuts()

    # ── fonts ────────────────────────────────────────────────────────────────

    def _fonts(self):
        self.f_title   = tkfont.Font(family="DejaVu Sans",      size=13, weight="bold")
        self.f_label   = tkfont.Font(family="DejaVu Sans",      size=10)
        self.f_small   = tkfont.Font(family="DejaVu Sans",      size=9)
        self.f_mono    = tkfont.Font(family="DejaVu Sans Mono", size=10)
        self.f_mono_sm = tkfont.Font(family="DejaVu Sans Mono", size=9)
        self.f_badge   = tkfont.Font(family="DejaVu Sans",      size=8,  weight="bold")
        self.f_heading = tkfont.Font(family="DejaVu Sans",      size=10, weight="bold")

    # ── layout ───────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=P["bg_card"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⌨  Linux Command Explainer", font=self.f_title,
                 bg=P["bg_card"], fg=P["text_primary"], padx=20).pack(side="left")
        tk.Label(hdr, text="v1.0", font=self.f_small,
                 bg=P["bg_card"], fg=P["text_muted"], padx=20).pack(side="right")
        tk.Frame(self, bg=P["accent"], height=2).pack(fill="x")

        # Content
        self._content = tk.Frame(self, bg=P["bg_dark"])
        self._content.pack(fill="both", expand=True, padx=18, pady=14)

        # Input card
        ic = self._card(self._content)
        ic.pack(fill="x", pady=(0, 8))
        tk.Label(ic, text="Enter a Linux command:", font=self.f_label,
                 bg=P["bg_card"], fg=P["text_secondary"]).pack(anchor="w", padx=14, pady=(10, 4))

        row = tk.Frame(ic, bg=P["bg_card"])
        row.pack(fill="x", padx=14, pady=(0, 10))

        self.cmd_var = tk.StringVar()
        self.entry = tk.Entry(row, textvariable=self.cmd_var, font=self.f_mono,
                              bg=P["bg_input"], fg=P["text_primary"],
                              insertbackground=P["accent"], relief="flat", bd=0,
                              highlightthickness=2, highlightbackground=P["border"],
                              highlightcolor=P["border_focus"])
        self.entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.entry.focus_set()

        self._btn(row, "Explain  ▶", self._explain, P["accent"], P["accent_hover"]).pack(side="right")
        self._btn(row, "Clear", self._clear, P["border"], "#3A3D52").pack(side="right", padx=(0, 6))

        # Risk banner (hidden initially)
        self._banner = tk.Frame(self._content, bg=P["bg_card"],
                                highlightthickness=1, highlightbackground=P["border"])
        self._banner_icon  = tk.Label(self._banner, text="", bg=P["bg_card"],
                                      fg=P["text_primary"],
                                      font=tkfont.Font(family="DejaVu Sans", size=18))
        self._banner_icon.pack(side="left", padx=(14, 8), pady=10)
        bf = tk.Frame(self._banner, bg=P["bg_card"])
        bf.pack(side="left", fill="both", expand=True, pady=10)
        self._banner_level   = tk.Label(bf, text="", font=self.f_heading,
                                        bg=P["bg_card"], fg=P["text_primary"], anchor="w")
        self._banner_level.pack(anchor="w")
        self._banner_summary = tk.Label(bf, text="", font=self.f_small,
                                        bg=P["bg_card"], fg=P["text_secondary"],
                                        anchor="w", wraplength=700, justify="left")
        self._banner_summary.pack(anchor="w")

        # Tabs
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("T.TNotebook", background=P["bg_dark"], borderwidth=0, tabmargins=[0,0,0,0])
        style.configure("T.TNotebook.Tab", background=P["bg_card"], foreground=P["text_secondary"],
                        padding=[14, 7], font=self.f_label, borderwidth=0)
        style.map("T.TNotebook.Tab",
                  background=[("selected", P["bg_dark"])],
                  foreground=[("selected", P["accent"])])

        nb = ttk.Notebook(self._content, style="T.TNotebook")
        nb.pack(fill="both", expand=True, pady=(8, 0))

        # Tab 1 — Breakdown
        t1 = tk.Frame(nb, bg=P["bg_dark"])
        nb.add(t1, text=" ⚙  Breakdown ")
        self._breakdown_host = t1
        self._show_placeholder(t1, "Enter a command above and click Explain.")

        # Tab 2 — Risks
        t2 = tk.Frame(nb, bg=P["bg_dark"])
        nb.add(t2, text=" ⚠  Risk Details ")
        self._risk_scroll = _ScrollableFrame(t2, bg=P["bg_dark"])
        self._risk_scroll.pack(fill="both", expand=True)
        self._show_placeholder(self._risk_scroll.inner, "Risk analysis will appear here.")

        # Status bar
        sb_frame = tk.Frame(self, bg=P["bg_card"], pady=5)
        sb_frame.pack(fill="x", side="bottom")
        tk.Frame(sb_frame, bg=P["border"], height=1).pack(fill="x")
        self._status = tk.StringVar(value="  Enter a command and press Enter or click Explain.")
        tk.Label(sb_frame, textvariable=self._status, font=self.f_small,
                 bg=P["bg_card"], fg=P["text_muted"], anchor="w").pack(fill="x", padx=10, pady=(4, 0))

    # ── events ───────────────────────────────────────────────────────────────

    def _shortcuts(self):
        self.entry.bind("<Return>", lambda e: self._explain())
        self.bind("<Control-l>", lambda e: self._clear())
        self.bind("<Escape>",    lambda e: self._clear())

    def _explain(self):
        cmd = self.cmd_var.get().strip()
        if not cmd:
            self._status.set("  ⚠  Please enter a command first.")
            return
        self._status.set(f"  Analysing: {cmd[:70]}…" if len(cmd) > 70 else f"  Analysing: {cmd}")
        self.update_idletasks()

        parsed = parse_command(cmd)
        risk   = detect_risks(cmd)

        self._render_breakdown(parsed)
        self._render_banner(risk)
        self._render_risk_details(risk)

        level = risk["overall_level"]
        n     = len(risk["matches"])
        self._status.set(
            f"  ✔  {len(parsed['tokens'])} token(s) parsed  ·  "
            f"Risk: {level}  ·  {n} warning{'s' if n!=1 else ''}  |  Ctrl+L / Esc to clear")

    def _clear(self):
        self.cmd_var.set("")
        self.entry.focus_set()
        self._banner.pack_forget()
        self._show_placeholder(self._breakdown_host, "Enter a command above and click Explain.")
        self._show_placeholder(self._risk_scroll.inner, "Risk analysis will appear here.")
        self._status.set("  Enter a command and press Enter or click Explain.")

    # ── renderers ────────────────────────────────────────────────────────────

    def _show_placeholder(self, parent, text):
        for w in parent.winfo_children():
            w.destroy()
        tk.Label(parent, text=text, font=self.f_label,
                 bg=P["bg_dark"], fg=P["text_muted"], justify="center").pack(expand=True, pady=30)

    def _render_breakdown(self, parsed):
        for w in self._breakdown_host.winfo_children():
            w.destroy()
        if not parsed["tokens"]:
            self._show_placeholder(self._breakdown_host, "Could not parse this command.")
            return

        scroll = _ScrollableFrame(self._breakdown_host, bg=P["bg_dark"])
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # Summary
        sc = self._card(inner)
        sc.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(sc, text=f"📋  {parsed['summary']}", font=self.f_label,
                 bg=P["bg_card"], fg=P["text_primary"], wraplength=760,
                 justify="left", padx=14, pady=10).pack(anchor="w")

        # Token pipeline
        pc = self._card(inner)
        pc.pack(fill="x", padx=10, pady=(0, 6))
        pip = tk.Frame(pc, bg=P["bg_card"])
        pip.pack(fill="x", padx=14, pady=8)
        for i, comp in enumerate(parsed["components"]):
            color = CATEGORY_COLORS.get(comp["category"], P["text_secondary"])
            pill = tk.Frame(pip, bg=color)
            pill.pack(side="left", padx=(0, 3))
            tk.Label(pill, text=f" {comp['token']} ", font=self.f_mono_sm,
                     bg=color, fg="#0F1117", pady=3).pack()
            if i < len(parsed["components"]) - 1:
                tk.Label(pip, text="›", font=self.f_mono_sm,
                         bg=P["bg_card"], fg=P["text_muted"]).pack(side="left", padx=(0, 3))

        # Component cards
        for comp in parsed["components"]:
            color = CATEGORY_COLORS.get(comp["category"], P["text_secondary"])
            cc = self._card(inner)
            cc.pack(fill="x", padx=10, pady=2)
            tk.Frame(cc, bg=color, width=4).pack(side="left", fill="y")
            body = tk.Frame(cc, bg=P["bg_card"])
            body.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            hr = tk.Frame(body, bg=P["bg_card"])
            hr.pack(fill="x")
            tk.Label(hr, text=comp["token"], font=self.f_mono,
                     bg=P["bg_card"], fg=color).pack(side="left")
            tk.Label(hr, text=f" {comp['category']} ", font=self.f_badge,
                     bg=color, fg="#0F1117", padx=4, pady=1).pack(side="left", padx=(8, 0))
            for line in comp["explanation"].split("\n"):
                if line.strip():
                    tk.Label(body, text=line, font=self.f_small, bg=P["bg_card"],
                             fg=P["text_secondary"], justify="left", anchor="w",
                             wraplength=740).pack(anchor="w")

    def _render_banner(self, risk):
        level = risk["overall_level"]
        color = RISK_BADGE.get(level, P["green"])
        self._banner.configure(highlightbackground=color)
        self._banner_icon.configure(text=risk["overall_icon"], fg=color)
        if level == "SAFE":
            self._banner_level.configure(text="Safe", fg=color)
            self._banner_summary.configure(text="No known risks detected.")
        else:
            n = len(risk["matches"])
            titles = ", ".join(m["title"] for m in risk["matches"][:3])
            if n > 3:
                titles += f" +{n-3} more"
            self._banner_level.configure(text=f"{level} RISK", fg=color)
            self._banner_summary.configure(text=titles)
        try:
            self._banner.pack_info()
        except tk.TclError:
            self._banner.pack(in_=self._content, fill="x", pady=(0, 6),
                              before=self._content.winfo_children()[-1])

    def _render_risk_details(self, risk):
        inner = self._risk_scroll.inner
        for w in inner.winfo_children():
            w.destroy()
        level   = risk["overall_level"]
        color   = RISK_BADGE.get(level, P["green"])
        matches = risk["matches"]

        hdr = tk.Frame(inner, bg=color)
        hdr.pack(fill="x", pady=(0, 8))
        tk.Label(hdr, text=f"  {risk['overall_icon']}  Overall Risk: {level}",
                 font=self.f_heading, bg=color, fg="#0F1117", pady=8, padx=10).pack(anchor="w")

        if not matches:
            tk.Label(inner, text="✔  No risks detected.", font=self.f_label,
                     bg=P["bg_dark"], fg=RISK_BADGE["SAFE"], pady=12).pack(anchor="w", padx=14)
            return

        for m in matches:
            mc = RISK_BADGE.get(m["level"], P["text_secondary"])
            card = self._card(inner)
            card.pack(fill="x", padx=10, pady=3)
            tk.Frame(card, bg=mc, width=4).pack(side="left", fill="y")
            body = tk.Frame(card, bg=P["bg_card"])
            body.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            tr = tk.Frame(body, bg=P["bg_card"])
            tr.pack(fill="x")
            tk.Label(tr, text=f"{m['icon']}  {m['title']}", font=self.f_heading,
                     bg=P["bg_card"], fg=mc).pack(side="left")
            tk.Label(tr, text=f" {m['level']} ", font=self.f_badge,
                     bg=mc, fg="#0F1117", padx=4, pady=1).pack(side="left", padx=(8, 0))
            tk.Label(body, text=m["message"], font=self.f_small, bg=P["bg_card"],
                     fg=P["text_secondary"], wraplength=740, justify="left",
                     anchor="w").pack(anchor="w", pady=(4, 0))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _card(self, parent):
        return tk.Frame(parent, bg=P["bg_card"],
                        highlightbackground=P["border"], highlightthickness=1)

    def _btn(self, parent, text, cmd, bg, hover_bg):
        b = tk.Button(parent, text=text, font=self.f_label, bg=bg, fg="#FFFFFF",
                      activebackground=hover_bg, activeforeground="#FFFFFF",
                      relief="flat", bd=0, padx=16, pady=8, cursor="hand2", command=cmd)
        b.bind("<Enter>", lambda e: b.configure(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        return b


def launch():
    app = CommandExplainerApp()
    app.mainloop()


if __name__ == "__main__":
    launch()
