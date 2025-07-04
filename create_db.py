#!/usr/bin/env python3
"""
Convert Open Opus MySQL schema to SQLite
"""

import sqlite3
import os


def create_openopus_sqlite_db(db_path="openopus.db"):
    """Create SQLite database with exact Open Opus schema"""

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Composer table (MySQL -> SQLite conversion)
    cursor.execute(
        """
         CREATE TABLE composer (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE,
              name_ko TEXT,
              lastname_ko TEXT,
              complete_name TEXT,
              portrait TEXT,
              birth DATE NOT NULL,
              death DATE,
              epoch TEXT NOT NULL,
              country TEXT,
              recommended BOOLEAN DEFAULT 0,
              popular BOOLEAN DEFAULT 0
         )
    """
    )

    # Work table
    cursor.execute(
        """
         CREATE TABLE work (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              composer_id INTEGER NOT NULL,
              title TEXT,
              title_ko TEXT,
              subtitle TEXT,
              subtitle_ko TEXT,
              searchterms TEXT,
              genre TEXT NOT NULL,
              year DATE,
              recommended BOOLEAN DEFAULT 0,
              popular BOOLEAN DEFAULT 0,
              FOREIGN KEY (composer_id) REFERENCES composer (id)
         )
    """
    )

    # Create indexes
    cursor.execute("CREATE INDEX idx_composer_name ON composer (name)")
    cursor.execute("CREATE INDEX idx_composer_name_ko ON composer (name_ko)")
    cursor.execute("CREATE INDEX idx_composer_lastname_ko ON composer (lastname_ko)")
    cursor.execute(
        "CREATE INDEX idx_composer_complete_name ON composer (complete_name)"
    )
    cursor.execute("CREATE INDEX idx_composer_epoch ON composer (epoch)")
    cursor.execute("CREATE INDEX idx_composer_recommended ON composer (recommended)")
    cursor.execute("CREATE INDEX idx_composer_popular ON composer (popular)")

    cursor.execute("CREATE INDEX idx_work_composer_id ON work (composer_id)")
    cursor.execute("CREATE INDEX idx_work_title ON work (title)")
    cursor.execute("CREATE INDEX idx_work_title_ko ON work (title_ko)")
    cursor.execute("CREATE INDEX idx_work_genre ON work (genre)")
    cursor.execute("CREATE INDEX idx_work_recommended ON work (recommended)")
    cursor.execute("CREATE INDEX idx_work_popular ON work (popular)")

    cursor.execute("CREATE INDEX idx_performer_role ON performer (role)")

    conn.commit()
    conn.close()

    print(f"SQLite database created: {db_path}")
    return db_path


if __name__ == "__main__":
    create_openopus_sqlite_db()
