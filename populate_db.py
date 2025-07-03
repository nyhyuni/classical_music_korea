#!/usr/bin/env python3
"""
Import Open Opus JSON data into SQLite database
Python equivalent of the PHP index.phtml script
"""

import json
import sqlite3
import requests
from typing import Dict, Any

def fetch_openopus_data(url: str = "https://api.openopus.org/work/dump.json") -> Dict[str, Any]:
    """Fetch data from Open Opus API"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def import_openopus_data(json_file_path: str = None, db_path: str = "openopus.db"):
    """Import Open Opus JSON data into SQLite database"""
    
    # Load data from file or API
    if json_file_path:
        print(f"Loading data from {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("Fetching data from Open Opus API...")
        data = fetch_openopus_data()
        if not data:
            print("Failed to fetch data")
            return
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM work")
    cursor.execute("DELETE FROM composer")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('composer', 'work')")
    
    inserted_composers = 0
    inserted_works = 0
    
    print("Importing composers and works...")
    
    # Import composers and their works
    for composer in data["composers"]:
        # Insert composer
        insert_composer = {
            "name": composer.get("name"),
            "complete_name": composer.get("complete_name"),
            "birth": composer.get("birth"),
            "death": composer.get("death"),
            "epoch": composer.get("epoch"),
            "recommended": composer.get("recommended", 0),
            "popular": composer.get("popular", 0)
        }
        
        cursor.execute('''
            INSERT INTO composer (name, complete_name, birth, death, epoch, recommended, popular)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            insert_composer["name"],
            insert_composer["complete_name"],
            insert_composer["birth"],
            insert_composer["death"],
            insert_composer["epoch"],
            insert_composer["recommended"],
            insert_composer["popular"]
        ))
        
        composer_id = cursor.lastrowid
        inserted_composers += 1
        
        # Insert works for this composer
        for work in composer.get("works", []):
            insert_work = {
                "composer_id": composer_id,
                "title": work.get("title"),
                "subtitle": work.get("subtitle"),
                "searchterms": work.get("searchterms"),
                "popular": work.get("popular", 0),
                "recommended": work.get("recommended", 0),
                "genre": work.get("genre")
            }
            
            cursor.execute('''
                INSERT INTO work (composer_id, title, subtitle, searchterms, popular, recommended, genre)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                insert_work["composer_id"],
                insert_work["title"],
                insert_work["subtitle"],
                insert_work["searchterms"],
                insert_work["popular"],
                insert_work["recommended"],
                insert_work["genre"]
            ))
            
            inserted_works += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Import complete!")
    print(f"   Composers inserted: {inserted_composers}")
    print(f"   Works inserted: {inserted_works}")
    print(f"   Database: {db_path}")

def test_import(db_path: str = "openopus.db"):
    """Test the imported data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test queries
    cursor.execute("SELECT COUNT(*) FROM composer")
    composer_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM work")
    work_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM composer WHERE popular = 1")
    popular_composers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM work WHERE popular = 1")
    popular_works = cursor.fetchone()[0]
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total composers: {composer_count}")
    print(f"   Total works: {work_count}")
    print(f"   Popular composers: {popular_composers}")
    print(f"   Popular works: {popular_works}")
    
    # Show some sample data
    print(f"\n🎼 Sample Popular Composers:")
    cursor.execute('''
        SELECT name, complete_name, epoch, 
               (SELECT COUNT(*) FROM work WHERE composer_id = composer.id) as work_count
        FROM composer 
        WHERE popular = 1 
        ORDER BY name 
        LIMIT 5
    ''')
    
    for row in cursor.fetchall():
        print(f"   {row[0]} - {row[1]} ({row[2]}) - {row[3]} works")
    
    print(f"\n🎵 Sample Popular Works:")
    cursor.execute('''
        SELECT c.name, w.title, w.genre
        FROM work w
        JOIN composer c ON w.composer_id = c.id
        WHERE w.popular = 1
        ORDER BY c.name, w.title
        LIMIT 5
    ''')
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} ({row[2]})")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    # Usage: python script.py [json_file_path] [db_path]
    json_file = sys.argv[1] if len(sys.argv) > 1 else None
    db_path = sys.argv[2] if len(sys.argv) > 2 else "openopus.db"
    
    # Make sure database exists first
    if not sqlite3.connect(db_path).execute("SELECT name FROM sqlite_master WHERE type='table' AND name='composer'").fetchone():
        print("❌ Database schema not found. Please run the schema creation script first.")
        sys.exit(1)
    
    # Import data
    import_openopus_data(json_file, db_path)
    
    # Test the import
    test_import(db_path)