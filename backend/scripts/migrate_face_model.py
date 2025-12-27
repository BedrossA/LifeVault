"""Migrate face table to add new columns"""
import sys
sys.path.append('/home/bpi/projects/LifeVault/backend')

from sqlalchemy import text
from app.db.base import engine

def migrate():
    """Add new columns to faces table"""
    
    with engine.connect() as conn:
        # Add new columns if they don't exist
        try:
            conn.execute(text("""
                ALTER TABLE faces 
                ADD COLUMN IF NOT EXISTS encoding_count INTEGER DEFAULT 1,
                ADD COLUMN IF NOT EXISTS average_quality FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS custom_threshold FLOAT,
                ADD COLUMN IF NOT EXISTS recognition_count INTEGER DEFAULT 0
            """))
            conn.commit()
            print("? Migration successful - new columns added")
            
            # Update existing records
            conn.execute(text("""
                UPDATE faces 
                SET encoding_count = 1,
                    average_quality = quality_score,
                    recognition_count = 0
                WHERE encoding_count IS NULL
            """))
            conn.commit()
            print("? Existing records updated")
            
        except Exception as e:
            print(f"Migration note: {e}")

if __name__ == "__main__":
    migrate()