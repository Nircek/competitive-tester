#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')  # nopep8
from gi.repository import Gtk, GLib

from concurrent.futures import ThreadPoolExecutor

from time import time
from pathlib import Path
from subprocess import run, PIPE, TimeoutExpired

from typing import Optional, Tuple, Callable, Any


class SystemRepo:
    def __init__(self, tpe: ThreadPoolExecutor):
        self.tpe = tpe

    def ensure_bin(self, prog: str) -> Path:
        path = Path(prog)
        if not path.is_file():
            path = Path(f'prog/{prog}')
        if not path.is_file():
            raise ValueError()
        bindir = Path('bin')
        bindir.mkdir(parents=True, exist_ok=True)
        exe = bindir / prog
        if not exe.is_file() or path.stat().st_mtime > exe.stat().st_mtime:
            cmd = ['g++', '-O3', '-o', exe, path]
            print(f'Running: {cmd}')
            run(cmd)
            print('end')
        assert exe.is_file()
        return exe

    def find_test(self, test: str) -> Path:
        path = Path(test)
        if not path.is_file():
            path = Path(f'{test}.in')
        if not path.is_file():
            path = Path(f'in/{test}')
        if not path.is_file():
            path = Path(f'in/{test}.in')
        if not path.is_file():
            raise ValueError()
        return path

    def time_bin(self, bin: str | Path, inp: str | Path, timeout: float | int = 2.0) -> Optional[Tuple[float, str]]:
        inp = inp.open('rb', 0)
        try:
            t = time()
            p = run(bin, stdin=inp,
                    capture_output=True, timeout=timeout)
            t = time() - t
            inp.close()
        except TimeoutExpired:
            return None
        return (t, str(len(p.stdout)))

        return None

    def _test(self, prog: str, test: str) -> str:
        bin, inp = None, None
        try:
            bin = self.ensure_bin(prog)
            inp = self.find_test(test)
        except ValueError:
            return '---t404---' if bin is not None else '---p404---'

        x = self.time_bin(bin, inp)
        TLE = '---TLE---'
        if x is None:
            return TLE
        x2 = self.time_bin(bin, inp)
        if x2 is None:
            return TLE
        x3 = self.time_bin(bin, inp)
        if x3 is None:
            return TLE
        time, sha = x
        time = (time + x2[0] + x3[0]) / 3
        return f'{time:.2f}s:{sha[:4]}'

    def test(self, prog: str, test: str, cb: Callable[[str], Any]) -> None:
        fut = self.tpe.submit(self._test, prog, test)
        fut.add_done_callback(lambda x: GLib.idle_add(lambda: cb(x.result())))


class TesterApp(Gtk.Window):
    def set_label(self, x: int, y: int, label: str) -> None:
        self.grid.get_child_at(x, y).set_label(label)

    def run_test(self, x: int, y: int) -> None:
        test, prog = self.tests[x], self.progs[y]
        self.system.test(prog, test, lambda r: self.set_label(x, y, r))

    def click(self, x: int, y: int) -> None:
        if x == -1:
            for col, _ in enumerate(self.tests):
                self.run_test(col, y)
        elif y == -1:
            for row, _ in enumerate(self.progs):
                self.run_test(x, row)
        else:
            self.run_test(x, y)

    def detach(self, x: int, y: int) -> None:
        self.grid.remove(self.grid.get_child_at(x, y))

    def attach(self, x: int, y: int, label: str = '') -> None:
        button = Gtk.Button(label=label)
        button.connect('clicked', lambda _: self.click(x, y))
        self.grid.attach(button, x, y, 1, 1)

    def entry_init(self, col: bool = False) -> Gtk.Entry:
        entry = Gtk.Entry()
        entry.connect('activate', self.add_col if col else self.add_row)
        entry.set_placeholder_text('test' if col else 'prog')
        entry.set_width_chars(10 if col else 4)
        self.grid.attach(
            entry, len(self.tests) if col else -1, -
            1 if col else len(self.progs), 1, 1
        )
        return entry

    def __init__(self, system: SystemRepo) -> None:
        Gtk.Window.__init__(self, title='Table')
        self.system = system
        self.tests = []
        self.progs = []

        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=1, row_spacing=1)
        self.add(self.grid)

        self.entry_init(False)
        self.entry_init(True)

    def add_row(self, entry: Gtk.Entry) -> None:
        test = entry.get_text()
        self.detach(-1, len(self.progs))
        self.attach(-1, len(self.progs), test)
        for col, _ in enumerate(self.tests):
            self.attach(col, len(self.progs), '-')
        self.progs += [test]
        self.set_focus(self.entry_init(False))
        self.grid.show_all()

    def add_col(self, entry: Gtk.Entry) -> None:
        prog = entry.get_text()
        self.detach(len(self.tests), -1)
        self.attach(len(self.tests), -1, prog)
        for row, _ in enumerate(self.progs):
            self.attach(len(self.tests), row, '-')
        self.tests += [prog]
        self.set_focus(self.entry_init(True))
        self.grid.show_all()


with ThreadPoolExecutor(max_workers=1) as executor:
    table_window = TesterApp(SystemRepo(executor))
    table_window.connect('delete-event', Gtk.main_quit)
    table_window.show_all()
    Gtk.main()
