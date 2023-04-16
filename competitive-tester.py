#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from time import sleep, time
from concurrent.futures import ThreadPoolExecutor


class SystemRepo:
    def __init__(self, tpe):
        self.tpe = tpe

    def _test(self, prog, test):
        sleep(2)
        return time() % 3

    def test(self, prog, test, cb):
        self.tpe.submit(self._test, prog, test).add_done_callback(lambda x: GLib.idle_add(lambda: cb(x)))

class TesterApp(Gtk.Window):
    def update(self, x, y):
        self.system.test(x, y, lambda rf: self.grid.get_child_at(x, y).set_label(f'{x},{y}: {rf.result()}'))

    def event(self, x, y, b):
        if x == -1:
            for col in range(self.cols):
                self.update(col, y)
        elif y == -1:
            for row in range(self.rows):
                self.update(x, row)
        else:
            self.update(x, y)

    def detach(self, x, y):
        self.grid.remove(self.grid.get_child_at(x, y))

    def attach(self, x, y, label=''):
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda b: self.event(x, y, b))
        self.grid.attach(button, x, y, 1, 1)

    def __init__(self, system):
        Gtk.Window.__init__(self, title="Table")
        self.system = system
        self.cols = 0
        self.rows = 0

        self.grid = Gtk.Grid(column_spacing=1, row_spacing=1)
        self.add(self.grid)

        for col in range(self.cols):
            self.attach(col, -1, f'C{col}')
        for row in range(self.rows):
            self.attach(-1, row, f'R{row}')

        for col in range(self.cols):
            for row in range(self.rows):
                self.attach(col, row, f'{col},{row}')

        row_entry = Gtk.Entry()
        row_entry.connect("activate", self.add_row)
        self.grid.attach(row_entry, -1, self.rows, 1, 1)
        col_entry = Gtk.Entry()
        col_entry.connect("activate", self.add_col)
        self.grid.attach(col_entry, self.cols, -1, 1, 1)

    def add_row(self, button):
        self.detach(-1, self.rows)
        self.attach(-1, self.rows, f'R{self.rows}')
        for col in range(self.cols):
            self.attach(col, self.rows,
                        f'{col},{self.rows}')
        self.rows += 1
        row_entry = Gtk.Entry()
        row_entry.connect("activate", self.add_row)
        self.grid.attach(row_entry, -1, self.rows, 1, 1)
        self.grid.show_all()
        self.set_focus(row_entry)

    def add_col(self, button):
        self.detach(self.cols, -1)
        self.attach(self.cols, -1, f'C{self.cols}')
        for row in range(self.rows):
            self.attach(self.cols, row,
                        f'{self.cols},{row}')
        self.cols += 1
        col_entry = Gtk.Entry()
        col_entry.connect("activate", self.add_col)
        self.grid.attach(col_entry, self.cols, -1, 1, 1)
        self.grid.show_all()
        self.set_focus(col_entry)

with ThreadPoolExecutor(max_workers=1) as executor:
    table_window = TesterApp(SystemRepo(executor))
    table_window.connect("delete-event", Gtk.main_quit)
    table_window.show_all()
    Gtk.main()
