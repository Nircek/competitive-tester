#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")  # nopep8
from gi.repository import Gtk, GLib

from concurrent.futures import ThreadPoolExecutor

from time import sleep
from random import random


class SystemRepo:
    def __init__(self, tpe):
        self.tpe = tpe

    def _test(self, prog, test):
        res = random() ** 2 * 3
        if res > 2:
            res = None
        sleep(2 if res is None else res)
        return "TLE" if res is None else f'{res:.2f}'

    def test(self, prog, test, cb):
        fut = self.tpe.submit(self._test, prog, test)
        fut.add_done_callback(lambda x: GLib.idle_add(lambda: cb(x.result())))


class TesterApp(Gtk.Window):
    def set_label(self, x, y, label):
        self.grid.get_child_at(x, y).set_label(label)

    def run_test(self, x, y):
        self.system.test(x, y, lambda r: self.set_label(x, y, r))

    def click(self, x, y):
        if x == -1:
            for col, _ in enumerate(self.progs):
                self.run_test(col, y)
        elif y == -1:
            for row, _ in enumerate(self.tests):
                self.run_test(x, row)
        else:
            self.run_test(x, y)

    def detach(self, x, y):
        self.grid.remove(self.grid.get_child_at(x, y))

    def attach(self, x, y, label=""):
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda _: self.click(x, y))
        self.grid.attach(button, x, y, 1, 1)

    def entry_init(self, col=False):
        entry = Gtk.Entry()
        entry.connect("activate", self.add_col if col else self.add_row)
        entry.set_placeholder_text("test" if col else "prog")
        entry.set_width_chars(8 if col else 4)
        self.grid.attach(
            entry, len(self.progs) if col else -1, -
            1 if col else len(self.tests), 1, 1
        )
        return entry

    def __init__(self, system):
        Gtk.Window.__init__(self, title="Table")
        self.system = system
        self.progs = []
        self.tests = []

        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=1, row_spacing=1)
        self.add(self.grid)

        self.entry_init(False)
        self.entry_init(True)

    def add_row(self, entry):
        test = entry.get_text()
        self.detach(-1, len(self.tests))
        self.attach(-1, len(self.tests), test)
        for col, _ in enumerate(self.progs):
            self.attach(col, len(self.tests), "-")
        self.tests += [test]
        self.set_focus(self.entry_init(False))
        self.grid.show_all()

    def add_col(self, entry):
        prog = entry.get_text()
        self.detach(len(self.progs), -1)
        self.attach(len(self.progs), -1, prog)
        for row, _ in enumerate(self.tests):
            self.attach(len(self.progs), row, "-")
        self.progs += [prog]
        self.set_focus(self.entry_init(True))
        self.grid.show_all()


with ThreadPoolExecutor(max_workers=1) as executor:
    table_window = TesterApp(SystemRepo(executor))
    table_window.connect("delete-event", Gtk.main_quit)
    table_window.show_all()
    Gtk.main()
