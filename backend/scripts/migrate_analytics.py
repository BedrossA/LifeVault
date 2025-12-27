"""Create analytics tables"""
import sys
sys.path.append('/home/bpi/projects/LifeVault/backend')

from app.db.base import Base, engine
from app.models.user import User
from app.models.analytics import (
    SleepLog, MoodLog, ExerciseLog, NutritionLog,
    WeightLog, FinanceLog, WaterLog
)

def migrate():
    """Create all analytics tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Analytics tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        analytics_tables = [t for t in tables if t.endswith('_logs')]
        print(f"\n📊 Created {len(analytics_tables)} analytics tables:")
        for table in analytics_tables:
            print(f"  ✅ {table}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
