import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


DB_NAME = 'hotel.db'


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            number TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            guest_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            nights INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("SELECT COUNT(*) FROM rooms")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO rooms (number, category, price, capacity) VALUES (?, ?, ?, ?)",
            [
                ('101', 'Стандарт', 2500.0, 2),
                ('102', 'Стандарт', 2500.0, 2),
                ('201', 'Люкс', 5500.0, 2),
                ('301', 'Апартаменты', 8500.0, 4),
                ('401', 'Эконом', 1500.0, 1),
            ],
        )
        cur.executemany(
            "INSERT INTO guests (full_name, phone) VALUES (?, ?)",
            [
                ('Иванова Анна', '+7-900-111-22-33'),
                ('Петров Сергей', '+7-900-444-55-66'),
            ],
        )

    conn.commit()
    conn.close()


def add_room(number, category, price, capacity):
    conn = get_connection()
    conn.execute(
        "INSERT INTO rooms (number, category, price, capacity) VALUES (?, ?, ?, ?)",
        (number, category, price, capacity),
    )
    conn.commit()
    conn.close()


def get_rooms(search=None):
    conn = get_connection()
    cur = conn.cursor()
    if search:
        cur.execute(
            "SELECT id, number, category, price, capacity FROM rooms "
            "WHERE number LIKE ? ORDER BY number",
            (f'%{search}%',),
        )
    else:
        cur.execute("SELECT id, number, category, price, capacity FROM rooms ORDER BY number")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_guest(full_name, phone):
    conn = get_connection()
    conn.execute("INSERT INTO guests (full_name, phone) VALUES (?, ?)", (full_name, phone))
    conn.commit()
    conn.close()


def get_guests():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name, phone FROM guests ORDER BY full_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_booking(guest_id, room_id, nights, total):
    conn = get_connection()
    conn.execute(
        "INSERT INTO bookings (guest_id, room_id, nights, total) VALUES (?, ?, ?, ?)",
        (guest_id, room_id, nights, total),
    )
    conn.commit()
    conn.close()


def get_bookings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, g.full_name, r.number, b.nights, b.total, b.created_at
        FROM bookings b
        JOIN guests g ON g.id = b.guest_id
        JOIN rooms r ON r.id = b.room_id
        ORDER BY b.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HotelApp — Гостиница")
        self.root.geometry("950x600")

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tab_rooms = tk.Frame(notebook)
        self.tab_guests = tk.Frame(notebook)
        self.tab_bookings = tk.Frame(notebook)
        self.tab_search = tk.Frame(notebook)

        notebook.add(self.tab_rooms, text='Номера')
        notebook.add(self.tab_guests, text='Гости')
        notebook.add(self.tab_bookings, text='Бронирования')
        notebook.add(self.tab_search, text='Поиск')

        self.build_rooms()
        self.build_guests()
        self.build_bookings()
        self.build_search()

    def build_rooms(self):
        form = tk.LabelFrame(self.tab_rooms, text="Добавить номер")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Номер:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.r_number = tk.Entry(form, width=25)
        self.r_number.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Категория:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.r_category = ttk.Combobox(
            form, values=["Эконом", "Стандарт", "Люкс", "Апартаменты"], width=18
        )
        self.r_category.grid(row=0, column=3, padx=4, pady=4)
        self.r_category.set("Стандарт")

        tk.Label(form, text="Цена за сутки:").grid(row=1, column=0, padx=4, pady=4, sticky='w')
        self.r_price = tk.Entry(form, width=25)
        self.r_price.grid(row=1, column=1, padx=4, pady=4)

        tk.Label(form, text="Вместимость:").grid(row=1, column=2, padx=4, pady=4, sticky='w')
        self.r_capacity = tk.Entry(form, width=18)
        self.r_capacity.grid(row=1, column=3, padx=4, pady=4)

        tk.Button(form, text="Добавить", command=self.add_room_click).grid(
            row=2, column=0, columnspan=4, pady=6
        )

        cols = ('ID', 'Номер', 'Категория', 'Цена/сутки', 'Вместимость')
        self.tree_rooms = ttk.Treeview(self.tab_rooms, columns=cols, show='headings')
        for c in cols:
            self.tree_rooms.heading(c, text=c)
            self.tree_rooms.column(c, width=150, anchor='center')
        self.tree_rooms.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_rooms()

    def add_room_click(self):
        try:
            number = self.r_number.get().strip()
            if not number:
                raise ValueError("Введите номер")
            price = float(self.r_price.get())
            capacity = int(self.r_capacity.get())
            if price <= 0 or capacity <= 0:
                raise ValueError("Цена > 0, вместимость > 0")
            add_room(number, self.r_category.get(), price, capacity)
            self.r_number.delete(0, tk.END)
            self.r_price.delete(0, tk.END)
            self.r_capacity.delete(0, tk.END)
            self.refresh_rooms()
            messagebox.showinfo("Готово", "Номер добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такой номер уже существует")

    def refresh_rooms(self):
        for row in self.tree_rooms.get_children():
            self.tree_rooms.delete(row)
        for row in get_rooms():
            self.tree_rooms.insert('', 'end', values=row)

    def build_guests(self):
        form = tk.LabelFrame(self.tab_guests, text="Добавить гостя")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="ФИО:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.g_name = tk.Entry(form, width=30)
        self.g_name.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Телефон:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.g_phone = tk.Entry(form, width=20)
        self.g_phone.grid(row=0, column=3, padx=4, pady=4)

        tk.Button(form, text="Добавить", command=self.add_guest_click).grid(
            row=1, column=0, columnspan=4, pady=6
        )

        cols = ('ID', 'ФИО', 'Телефон')
        self.tree_guests = ttk.Treeview(self.tab_guests, columns=cols, show='headings')
        for c in cols:
            self.tree_guests.heading(c, text=c)
            self.tree_guests.column(c, width=200, anchor='center')
        self.tree_guests.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.refresh_guests()

    def add_guest_click(self):
        try:
            name = self.g_name.get().strip()
            phone = self.g_phone.get().strip()
            if not name or not phone:
                raise ValueError("Заполните ФИО и телефон")
            add_guest(name, phone)
            self.g_name.delete(0, tk.END)
            self.g_phone.delete(0, tk.END)
            self.refresh_guests()
            messagebox.showinfo("Готово", "Гость добавлен")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такой телефон уже есть")

    def refresh_guests(self):
        for row in self.tree_guests.get_children():
            self.tree_guests.delete(row)
        for row in get_guests():
            self.tree_guests.insert('', 'end', values=row)

    def build_bookings(self):
        form = tk.LabelFrame(self.tab_bookings, text="Оформить бронирование")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Гость:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.b_guest = ttk.Combobox(form, width=30, state='readonly')
        self.b_guest.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="Номер:").grid(row=0, column=2, padx=4, pady=4, sticky='w')
        self.b_room = ttk.Combobox(form, width=30, state='readonly')
        self.b_room.grid(row=0, column=3, padx=4, pady=4)

        tk.Label(form, text="Ночей:").grid(row=1, column=0, padx=4, pady=4, sticky='w')
        self.b_nights = tk.Entry(form, width=10)
        self.b_nights.grid(row=1, column=1, padx=4, pady=4, sticky='w')

        tk.Button(form, text="Забронировать", command=self.add_booking_click).grid(
            row=2, column=0, columnspan=2, pady=6
        )
        tk.Button(form, text="Обновить списки", command=self.load_booking_lists).grid(
            row=2, column=3, padx=4, pady=6, sticky='e'
        )

        cols = ('ID', 'Гость', 'Номер', 'Ночей', 'Сумма', 'Дата')
        self.tree_bookings = ttk.Treeview(self.tab_bookings, columns=cols, show='headings')
        for c in cols:
            self.tree_bookings.heading(c, text=c)
            self.tree_bookings.column(c, width=130, anchor='center')
        self.tree_bookings.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.load_booking_lists()
        self.refresh_bookings()

    def load_booking_lists(self):
        self.guests_data = get_guests()
        self.rooms_data = get_rooms()
        self.b_guest['values'] = [f"{g[0]} — {g[1]}" for g in self.guests_data]
        self.b_room['values'] = [
            f"{r[0]} — №{r[1]} ({r[2]}, {r[3]} руб./сут., до {r[4]} чел.)"
            for r in self.rooms_data
        ]

    def add_booking_click(self):
        try:
            if not self.b_guest.get() or not self.b_room.get():
                raise ValueError("Выберите гостя и номер")
            guest_id = int(self.b_guest.get().split(' — ')[0])
            room_id = int(self.b_room.get().split(' — ')[0])
            nights = int(self.b_nights.get())
            if nights <= 0:
                raise ValueError("Количество ночей > 0")

            room = next(r for r in self.rooms_data if r[0] == room_id)
            total = nights * room[3]

            add_booking(guest_id, room_id, nights, total)
            self.b_nights.delete(0, tk.END)
            self.refresh_bookings()
            messagebox.showinfo("Готово", f"Бронирование оформлено. Сумма: {total:.2f} руб.")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_bookings(self):
        for row in self.tree_bookings.get_children():
            self.tree_bookings.delete(row)
        for row in get_bookings():
            self.tree_bookings.insert('', 'end', values=row)

    def build_search(self):
        form = tk.LabelFrame(self.tab_search, text="Поиск номера")
        form.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(form, text="Номер:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.s_query = tk.Entry(form, width=40)
        self.s_query.grid(row=0, column=1, padx=4, pady=4)

        tk.Button(form, text="Найти", command=self.do_search).grid(row=0, column=2, padx=4, pady=4)
        tk.Button(form, text="Сбросить", command=lambda: self.do_search(clear=True)).grid(
            row=0, column=3, padx=4, pady=4
        )

        cols = ('ID', 'Номер', 'Категория', 'Цена/сутки', 'Вместимость')
        self.tree_search = ttk.Treeview(self.tab_search, columns=cols, show='headings')
        for c in cols:
            self.tree_search.heading(c, text=c)
            self.tree_search.column(c, width=150, anchor='center')
        self.tree_search.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.do_search(clear=True)

    def do_search(self, clear=False):
        query = '' if clear else self.s_query.get().strip()
        if clear:
            self.s_query.delete(0, tk.END)
        for row in self.tree_search.get_children():
            self.tree_search.delete(row)
        for row in get_rooms(query or None):
            self.tree_search.insert('', 'end', values=row)


if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()
