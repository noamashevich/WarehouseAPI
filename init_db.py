import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'warehouse.db')

schema = """
CREATE TABLE IF NOT EXISTS Trucks (
    id TEXT PRIMARY KEY,
    length REAL NOT NULL CHECK (length > 0),
    width REAL NOT NULL CHECK (width > 0),
    height REAL NOT NULL CHECK (height > 0),
    volume REAL NOT NULL,
    available INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Packages (
    id TEXT PRIMARY KEY,
    length REAL NOT NULL CHECK (length > 0),
    width REAL NOT NULL CHECK (width > 0),
    height REAL NOT NULL CHECK (height > 0),
    volume REAL NOT NULL,
    assigned_truck_id TEXT,
    FOREIGN KEY (assigned_truck_id) REFERENCES Trucks(id) ON DELETE SET NULL
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database created: warehouse.db")

if __name__ == '__main__':
    init_db()
