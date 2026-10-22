import unittest
import tempfile
import os
import sqlite3


import hotel
from hotel import (
    init_db, add_room, get_rooms,
    add_guest, get_guests,
    add_booking, get_bookings,
)


class TestHotel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Подменяем БД на временный файл, чтобы не портить рабочую базу
        cls._original_db = hotel.DB_NAME
        cls._tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        hotel.DB_NAME = cls._tmp.name
        init_db()

    @classmethod
    def tearDownClass(cls):
        hotel.DB_NAME = cls._original_db
        if os.path.exists(cls._tmp.name):
            os.remove(cls._tmp.name)

    def test_01_add_room(self):
        before = len(get_rooms())

        add_room('999', 'Стандарт', 2500.0, 2)

        self.assertEqual(len(get_rooms()), before + 1)

    def test_02_get_rooms(self):
        add_room('998', 'Люкс', 5500.0, 2)

        rooms = get_rooms()

        self.assertTrue(len(rooms) >= 1)

    def test_03_add_guest(self):
        before = len(get_guests())

        add_guest('Тестов Тест', '+7-900-000-00-01')

        self.assertEqual(len(get_guests()), before + 1)

    def test_04_add_booking(self):
        add_room('997', 'Апартаменты', 8000.0, 4)
        r = get_rooms('997')[0]
        g = get_guests()[0]

        add_booking(g[0], r[0], 2, 16000.0)

        self.assertTrue(len(get_bookings()) >= 1)

    def test_05_booking_total(self):
        add_room('996', 'Эконом', 1500.0, 1)
        r = get_rooms('996')[0]
        g = get_guests()[0]

        nights = 3
        total = nights * r[3]  # 3 ночи × 1500 руб.
        add_booking(g[0], r[0], nights, total)

        self.assertEqual(get_bookings()[0][4], 4500.0)

    def test_06_search(self):
        add_room('123-уникальный', 'Стандарт', 2500.0, 2)

        result = get_rooms('уникальный')

        self.assertTrue(len(result) >= 1)

    def test_07_duplicate_room(self):
        add_room('555-дубль', 'Стандарт', 2000.0, 2)

        with self.assertRaises(sqlite3.IntegrityError):
            add_room('555-дубль', 'Стандарт', 2000.0, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
