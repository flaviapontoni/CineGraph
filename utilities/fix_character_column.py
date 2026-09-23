from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = "Daddo09@"
password_encoded = quote_plus(password)
engine = create_engine(f'postgresql://postgres:{password_encoded}@localhost:5432/cinegraph')

print("Altering character column to TEXT (unlimited)...")
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE "cast" ALTER COLUMN character TYPE TEXT'))
    conn.commit()
    print("✓ Column altered successfully")