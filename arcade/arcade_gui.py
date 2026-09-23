#!/usr/bin/env python3
"""
crackme arcade — GTK window.

Same challenges and rules as ./arcade.py (solve L(n) to unlock L(n+1); the
launcher runs the real binary and checksums it first, so patching the gate
isn't a solve). This is just a nicer front door. Analyse the binaries with
Ghidra / gdb / objdump / r2; type the recovered key here.

    ./arcade_gui.py
"""
import os, sys, importlib.util
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

# import the shared core (level metadata, verify, progress, hints)
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("arcade_core", os.path.join(HERE, "arcade.py"))
core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)

CSS = b"""
.card        { padding: 8px 10px; margin: 2px 0; border-radius: 8px; }
.card.solved { background: alpha(@success_color, 0.18); }
.card.open   { background: alpha(@warning_color, 0.16); }
.card.locked { opacity: 0.45; }
.title       { font-weight: bold; font-size: 15px; }
.brief       { opacity: 0.85; }
.result-ok   { color: #3fb950; font-weight: bold; }
.result-no   { color: #f85149; font-weight: bold; }
.hintbox     { font-family: monospace; }
.mono        { font-family: monospace; }
"""

class Arcade(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="dev.local.crackme.arcade")

    def do_activate(self):
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.selected = None
        self.challenge = None  # for L4

        win = Gtk.ApplicationWindow(application=self)
        win.set_title("Crackme Arcade")
        win.set_default_size(760, 520)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin_top=12,
                       margin_bottom=12, margin_start=12, margin_end=12)
        win.set_child(root)

        head = Gtk.Label(xalign=0)
        head.set_markup("<span size='x-large' weight='bold'>⚙  Crackme Arcade</span>"
                        "   <span alpha='70%'>reverse each binary, enter the key</span>")
        root.append(head)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, vexpand=True)
        root.append(body)

        # left: level list
        left_scroll = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
        left_scroll.set_min_content_width(280)
        self.level_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        left_scroll.set_child(self.level_list)
        body.append(left_scroll)

        # right: detail panel
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        body.append(right)

        self.d_title = Gtk.Label(xalign=0); self.d_title.add_css_class("title")
        self.d_brief = Gtk.Label(xalign=0, wrap=True); self.d_brief.add_css_class("brief")
        self.d_bin   = Gtk.Label(xalign=0); self.d_bin.add_css_class("mono")
        right.append(self.d_title); right.append(self.d_brief); right.append(self.d_bin)

        # L4 challenge row (hidden unless L4)
        self.chal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.chal_lbl = Gtk.Label(xalign=0); self.chal_lbl.add_css_class("mono")
        chal_btn = Gtk.Button(label="new name"); chal_btn.connect("clicked", self.on_new_challenge)
        self.chal_box.append(self.chal_lbl); self.chal_box.append(chal_btn)
        right.append(self.chal_box)

        # key entry + Go
        entry_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.entry = Gtk.Entry(hexpand=True, placeholder_text="recovered key…")
        self.entry.connect("activate", self.on_submit)
        go = Gtk.Button(label="Check"); go.add_css_class("suggested-action")
        go.connect("clicked", self.on_submit)
        entry_row.append(self.entry); entry_row.append(go)
        right.append(entry_row)

        self.result = Gtk.Label(xalign=0)
        right.append(self.result)

        # hint
        hint_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hint_btn = Gtk.Button(label="💡 Hint"); hint_btn.connect("clicked", self.on_hint)
        hint_row.append(hint_btn)
        right.append(hint_row)
        self.hintbox = Gtk.Label(xalign=0, wrap=True, yalign=0, vexpand=True)
        self.hintbox.add_css_class("hintbox")
        right.append(self.hintbox)

        # bottom: progress
        self.prog = Gtk.ProgressBar(show_text=True)
        root.append(self.prog)

        self.refresh()
        # auto-select the first unsolved-but-open level
        solved = core.load()
        first_open = (max(solved) + 1) if solved else 1
        self.select(min(first_open, len(core.LEVELS)))
        win.present()

    # ---- state / rendering -------------------------------------------------
    def refresh(self):
        solved = core.load()
        highest_open = (max(solved) + 1) if solved else 1
        child = self.level_list.get_first_child()
        while child:
            nxt = child.get_next_sibling(); self.level_list.remove(child); child = nxt
        for num, name, tag, _ in core.LEVELS:
            unlocked = num <= highest_open
            if num in solved:  mark, state = "✓", "solved"
            elif unlocked:     mark, state = "○", "open"
            else:              mark, state = "🔒", "locked"
            btn = Gtk.Button()
            btn.add_css_class("card"); btn.add_css_class(state); btn.add_css_class("flat")
            lbl = Gtk.Label(xalign=0)
            lbl.set_markup(f"<b>L{num}</b>  {GLib.markup_escape_text(tag)}   {mark} {state}")
            btn.set_child(lbl)
            btn.set_sensitive(unlocked)
            btn.connect("clicked", lambda _b, n=num: self.select(n))
            self.level_list.append(btn)
        done = len(solved)
        self.prog.set_fraction(done / len(core.LEVELS))
        self.prog.set_text(f"{done}/{len(core.LEVELS)} solved")

    def select(self, num):
        self.selected = num
        lvl = next(l for l in core.LEVELS if l[0] == num)
        _, name, tag, brief = lvl
        self.d_title.set_text(f"L{num} · {tag}")
        self.d_brief.set_text(brief)
        self.d_bin.set_markup(f"<span alpha='70%'>binary:</span> arcade/{name}")
        self.result.set_text("")
        self.entry.set_text("")
        self.hintbox.set_text("")
        if num == 4:
            self.new_challenge()
            self.chal_box.set_visible(True)
            self.entry.set_placeholder_text("serial for the name above…")
        else:
            self.chal_box.set_visible(False)
            self.entry.set_placeholder_text("recovered key…")
        self.entry.grab_focus()

    def new_challenge(self):
        self.challenge = core.gen_challenge()
        self.chal_lbl.set_markup(f"produce the serial for:  <b>{self.challenge}</b>")

    def on_new_challenge(self, _btn):
        if self.selected == 4:
            self.new_challenge(); self.result.set_text("")

    # ---- actions -----------------------------------------------------------
    def on_submit(self, _w):
        if self.selected is None:
            return
        num = self.selected
        name = next(l[1] for l in core.LEVELS if l[0] == num)
        payload = self.entry.get_text().strip()
        if not payload:
            return
        ok, reason = core.run_check(num, name, payload, self.challenge if num == 4 else None)
        self.result.remove_css_class("result-ok"); self.result.remove_css_class("result-no")
        if ok:
            self.result.add_css_class("result-ok")
            self.result.set_text("✓ correct — level cleared.")
            solved = core.load(); solved.add(num); core.save(solved)
            self.refresh()
            if len(solved) == len(core.LEVELS):
                self.result.set_text("★ correct — and that's the whole ladder cleared. ★")
        else:
            self.result.add_css_class("result-no")
            self.result.set_text(f"✗ {reason}")
            if num == 4:
                self.new_challenge()  # rotate the name so they must actually keygen

    def on_hint(self, _btn):
        if self.selected is None:
            return
        shown, tiers = core.hint_text(self.selected)
        if shown is None:
            self.hintbox.set_markup("<span alpha='60%'>no more hints — the last one is as far as I go.</span>")
            return
        prev = self.hintbox.get_text()
        line = f"hint {shown+1}/{len(tiers)}:  {tiers[shown]}"
        self.hintbox.set_text((prev + "\n\n" + line).strip() if prev else line)

def main():
    app = Arcade()
    return app.run(None)

if __name__ == "__main__":
    sys.exit(main())
