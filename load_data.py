#!/usr/bin/env python3
"""
Load Open Opus SQLite data into Python dictionaries
"""

import sqlite3

def load_openopus_data(db_path="concert_project.db"):
   """Load composers and works into dictionaries for fuzzy matching"""
   
   conn = sqlite3.connect(db_path)
   cursor = conn.cursor()
   
   # Load composers into dictionary
   composers = {}
   cursor.execute('''
       SELECT id, name, name_ko, lastname_ko, complete_name, epoch, country, popular, recommended
       FROM catalog_composer
   ''')
   
   for row in cursor.fetchall():
       composers[row[0]] = {
           'id': row[0],
           'name': row[1],
           'name_ko': row[2],
           'lastname_ko': row[3],
           'complete_name': row[4],
           'epoch': row[5],
           'country': row[6],
           'popular': row[7],
           'recommended': row[8]
       }
   
   # Load works grouped by composer
   works_by_composer = {}
   cursor.execute('''
       SELECT composer_id, id, title, title_ko, subtitle, subtitle_ko, genre, popular, recommended
       FROM catalog_work
       ORDER BY composer_id, title
   ''')
   
   for row in cursor.fetchall():
       composer_id = row[0]
       if composer_id not in works_by_composer:
           works_by_composer[composer_id] = []
       
       works_by_composer[composer_id].append({
           'id': row[1],
           'title': row[2],
           'title_ko': row[3],
           'subtitle': row[4],
           'subtitle_ko': row[5],
           'genre': row[6],
           'popular': row[7],
           'recommended': row[8]
       })
   
   conn.close()
   
   print(f"Loaded {len(composers)} composers and {sum(len(works) for works in works_by_composer.values())} works")
   
   return composers, works_by_composer

if __name__ == "__main__":
   composers, works_by_composer = load_openopus_data()