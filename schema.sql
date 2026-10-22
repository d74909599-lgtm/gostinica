-- Таблица номеров гостиницы
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    number TEXT NOT NULL UNIQUE,       -- номер комнаты (например, '101')
    category TEXT NOT NULL,            -- категория номера
    price REAL NOT NULL,               -- цена за сутки
    capacity INTEGER NOT NULL          -- вместимость (чел.)
);

-- Таблица гостей
CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE
);

-- Таблица бронирований
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    nights INTEGER NOT NULL,           -- количество ночей
    total REAL NOT NULL,               -- итоговая стоимость
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Тестовые данные: номера
INSERT INTO rooms (number, category, price, capacity)
SELECT '101', 'Стандарт', 2500.00, 2
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE number = '101');

INSERT INTO rooms (number, category, price, capacity)
SELECT '102', 'Стандарт', 2500.00, 2
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE number = '102');

INSERT INTO rooms (number, category, price, capacity)
SELECT '201', 'Люкс', 5500.00, 2
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE number = '201');

INSERT INTO rooms (number, category, price, capacity)
SELECT '301', 'Апартаменты', 8500.00, 4
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE number = '301');

INSERT INTO rooms (number, category, price, capacity)
SELECT '401', 'Эконом', 1500.00, 1
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE number = '401');

-- Тестовые данные: гости
INSERT INTO guests (full_name, phone)
SELECT 'Иванова Анна', '+7-900-111-22-33'
WHERE NOT EXISTS (SELECT 1 FROM guests WHERE phone = '+7-900-111-22-33');

INSERT INTO guests (full_name, phone)
SELECT 'Петров Сергей', '+7-900-444-55-66'
WHERE NOT EXISTS (SELECT 1 FROM guests WHERE phone = '+7-900-444-55-66');
