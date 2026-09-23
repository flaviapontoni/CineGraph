import os
from pathlib import Path

print("="*80)
print("CINEGRAPH PROJECT CLEANUP")
print("="*80)

# File da eliminare
files_to_delete = [
    # Raw dataset (already processed)
    'credits.csv',
    'keywords.csv',
    'links.csv',
    'links_small.csv',
    'movies_metadata.csv',
    'ratings.csv',
    'ratings_small.csv',
    
    # Old/temp Python scripts
    'check_duplicates.py',
    'clean_cast_csv.py',
    'clean_cast_truncate.py',
    'clean_duplicates.py',
    'clean_neo4j.py',
    'debug_cast.py',
    'reload_cast.py',
    'reloard_cast.py',  # Typo!
    'test_load.py',
    'etl_process.py',
    'load_cast_direct.py',
]

# Old CSV files
old_csv_files = [
    'data/processed/cast.csv',
    'data/processed/cast_clean.csv',
]

print("\n📋 FILE DA ELIMINARE:\n")

total_size = 0
all_files = []

# Check CSV files
for f in files_to_delete:
    path = Path(f)
    if path.exists():
        size_mb = path.stat().st_size / (1024*1024)
        total_size += path.stat().st_size
        all_files.append(f)
        print(f"  ❌ {f} ({size_mb:.1f} MB)")

# Check old processed CSV
for f in old_csv_files:
    path = Path(f)
    if path.exists():
        size_mb = path.stat().st_size / (1024*1024)
        total_size += path.stat().st_size
        all_files.append(f)
        print(f"  ❌ {f} ({size_mb:.1f} MB)")

print(f"\n📊 TOTALE DA ELIMINARE: {total_size / (1024*1024):.1f} MB")
print(f"📦 FILE TOTALI: {len(all_files)}")

# Ask for confirmation
print("\n" + "="*80)
confirm = input("Sei sicuro? (s/n): ").strip().lower()

if confirm == 's':
    deleted_count = 0
    for f in all_files:
        try:
            path = Path(f)
            if path.exists():
                path.unlink()
                deleted_count += 1
                print(f"✓ Eliminato: {f}")
        except Exception as e:
            print(f"✗ Errore eliminando {f}: {e}")
    
    print(f"\n✅ ELIMINATI {deleted_count} FILE!")
    print(f"✅ SPAZIO LIBERATO: {total_size / (1024*1024):.1f} MB")
else:
    print("❌ Operazione annullata")

print("\n" + "="*80)
print("FILE RIMANENTI (da MANTENERE):")
print("="*80)
print("""
✓ load_postgresql.py      - Carica CSV in PostgreSQL
✓ load_neo4j.py          - Carica dati in Neo4j
✓ etl_complete.py        - ETL originale (reference)

✓ data/processed/actors.csv
✓ data/processed/genres.csv
✓ data/processed/movies.csv
✓ data/processed/movie_genres.csv
✓ data/processed/cast_final.csv  ← NUOVO! (valido)
""")
print("="*80)