import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class TesterApp(Gtk.Window):
    def event(self, x, y, b):
        if x == 1:
            print(f'R{y-2}')
        elif y == 1:
            print(f'C{x-2}')
        else:
            print(f'{x-2},{y-2}')

    def detach(self, x, y):
        self.grid.remove(self.grid.get_child_at(x, y))

    def attach(self, x, y, label=''):
        button = Gtk.Button(label=label)
        button.connect("clicked", lambda b: self.event(x, y, b))
        self.grid.attach(button, x, y, 1, 1)

    def update(self):
        self.grid.show_all()

    def __init__(self):
        Gtk.Window.__init__(self, title="Table")
        self.cols = 0
        self.rows = 0

        self.grid = Gtk.Grid(column_spacing=1, row_spacing=1)
        self.add(self.grid)

        for col in range(self.cols):
            self.attach(col+2, 1, f'C{col}')
        for row in range(self.rows):
            self.attach(1, row+2, f'R{row}')

        for col in range(self.cols):
            for row in range(self.rows):
                self.attach(col+2, row+2, f'{col},{row}')

        row_entry = Gtk.Entry()
        row_entry.connect("activate", self.add_row)
        self.grid.attach(row_entry, 1, self.rows+2, 1, 1)
        col_entry = Gtk.Entry()
        col_entry.connect("activate", self.add_col)
        self.grid.attach(col_entry, self.cols+2, 1, 1, 1)

    def add_row(self, button):
        self.detach(1, self.rows+2)
        self.attach(1, self.rows+2, f'R{self.rows}')
        for col in range(self.cols):
            self.attach(col+2, self.rows+2,
                        f'{col},{self.rows}')
        self.rows += 1
        row_entry = Gtk.Entry()
        row_entry.connect("activate", self.add_row)
        self.grid.attach(row_entry, 1, self.rows+2, 1, 1)
        self.update()
        self.set_focus(row_entry)

    def add_col(self, button):
        self.detach(self.cols+2, 1)
        self.attach(self.cols+2, 1, f'C{self.cols}')
        for row in range(self.rows):
            self.attach(self.cols+2, row+2,
                        f'{self.cols},{row}')
        self.cols += 1
        col_entry = Gtk.Entry()
        col_entry.connect("activate", self.add_col)
        self.grid.attach(col_entry, self.cols+2, 1, 1, 1)
        self.update()
        self.set_focus(col_entry)

table_window = TesterApp()
table_window.connect("delete-event", Gtk.main_quit)
table_window.show_all()
Gtk.main()
