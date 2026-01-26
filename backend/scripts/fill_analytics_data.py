#!/usr/bin/env python3
"""
Script to fill analytics data for testing and development.
Generates sample entries with various metrics, categories, and units.

Usage:
  python scripts/fill_analytics_data.py [username] [--days N] [--entries-per-day N] [--clear]
  
Examples:
  python scripts/fill_analytics_data.py
  python scripts/fill_analytics_data.py admin --days 60 --entries-per-day 3
  python scripts/fill_analytics_data.py admin --clear  # Clear existing data first
"""
import sys
import os
import asyncio
import random
from datetime import datetime, UTC, timedelta
from typing import List, Dict, Any

# Ensure backend root is on path and cwd for .env
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(backend_root)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.core.config import settings
from app.db.base import SessionLocal
from app.models.user import User
from app.db.mongodb import connect_mongodb, get_mongodb, close_mongodb


# Sample data templates
METRIC_TEMPLATES = {
    'health': [
        {'metric': 'weight', 'unit': 'kg', 'min': 60, 'max': 90, 'trend': 'stable'},
        {'metric': 'blood_pressure_systolic', 'unit': 'mmHg', 'min': 110, 'max': 140, 'trend': 'stable'},
        {'metric': 'blood_pressure_diastolic', 'unit': 'mmHg', 'min': 70, 'max': 90, 'trend': 'stable'},
        {'metric': 'heart_rate', 'unit': 'bpm', 'min': 60, 'max': 100, 'trend': 'stable'},
        {'metric': 'sleep_hours', 'unit': 'hours', 'min': 6, 'max': 9, 'trend': 'stable'},
    ],
    'fitness': [
        {'metric': 'steps', 'unit': 'steps', 'min': 5000, 'max': 15000, 'trend': 'increasing'},
        {'metric': 'calories', 'unit': 'kcal', 'min': 1500, 'max': 3000, 'trend': 'variable'},
        {'metric': 'distance', 'unit': 'km', 'min': 3, 'max': 10, 'trend': 'increasing'},
        {'metric': 'workout_duration', 'unit': 'minutes', 'min': 20, 'max': 90, 'trend': 'variable'},
        {'metric': 'active_calories', 'unit': 'kcal', 'min': 200, 'max': 800, 'trend': 'variable'},
    ],
    'productivity': [
        {'metric': 'hours', 'unit': 'hours', 'min': 4, 'max': 10, 'trend': 'stable'},
        {'metric': 'tasks_completed', 'unit': 'tasks', 'min': 3, 'max': 15, 'trend': 'increasing'},
        {'metric': 'focus_time', 'unit': 'minutes', 'min': 60, 'max': 240, 'trend': 'variable'},
        {'metric': 'meetings', 'unit': 'meetings', 'min': 0, 'max': 6, 'trend': 'stable'},
    ],
    'mood': [
        {'metric': 'mood_score', 'unit': 'score', 'min': 1, 'max': 10, 'trend': 'variable'},
        {'metric': 'energy_level', 'unit': 'score', 'min': 1, 'max': 10, 'trend': 'variable'},
        {'metric': 'stress_level', 'unit': 'score', 'min': 1, 'max': 10, 'trend': 'variable'},
    ],
    'finance': [
        {'metric': 'expense', 'unit': 'USD', 'min': 10, 'max': 200, 'trend': 'variable'},
        {'metric': 'income', 'unit': 'USD', 'min': 0, 'max': 500, 'trend': 'stable'},
        {'metric': 'savings', 'unit': 'USD', 'min': 0, 'max': 1000, 'trend': 'increasing'},
    ],
}

NOTES_TEMPLATES = [
    "Feeling great today!",
    "Had a productive session",
    "Need to improve tomorrow",
    "Best day this week!",
    "Could be better",
    "On track with goals",
    "Feeling motivated",
    "Need more rest",
    None,  # Some entries without notes
    None,
]


def generate_value(template: Dict[str, Any], day_index: int, total_days: int) -> float:
    """Generate a value based on template and trend"""
    base_min = template['min']
    base_max = template['max']
    trend = template.get('trend', 'stable')
    
    # Calculate base value
    base_value = random.uniform(base_min, base_max)
    
    # Apply trend
    if trend == 'increasing':
        # Gradually increase over time
        progress = day_index / total_days
        trend_factor = 1 + (progress * 0.3)  # 30% increase over period
        base_value *= trend_factor
    elif trend == 'variable':
        # Add more randomness
        base_value *= random.uniform(0.7, 1.3)
    
    # Add some daily variation
    variation = random.uniform(0.9, 1.1)
    value = base_value * variation
    
    # Round based on unit
    if template['unit'] in ['kg', 'USD']:
        return round(value, 2)
    elif template['unit'] in ['hours', 'minutes', 'score']:
        return round(value, 1)
    else:
        return round(value)
    
    return value


async def clear_user_data(mongo_db, user_id: int):
    """Clear existing analytics entries and goals for user"""
    print(f"Clearing existing data for user {user_id}...")
    result_entries = await mongo_db.analytics_entries.delete_many({"user_id": user_id})
    result_goals = await mongo_db.goals.delete_many({"user_id": user_id})
    print(f"  Deleted {result_entries.deleted_count} entries and {result_goals.deleted_count} goals")


async def create_entries(mongo_db, user_id: int, days: int, entries_per_day: int):
    """Create analytics entries"""
    print(f"\nCreating {entries_per_day * days} entries over {days} days...")
    
    entries_created = 0
    start_date = datetime.now(UTC) - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Select random categories and metrics for this day
        categories_for_day = random.sample(
            list(METRIC_TEMPLATES.keys()),
            k=min(entries_per_day, len(METRIC_TEMPLATES))
        )
        
        for category in categories_for_day:
            templates = METRIC_TEMPLATES[category]
            template = random.choice(templates)
            
            # Generate value
            value = generate_value(template, day, days)
            
            # Random time during the day
            hour = random.randint(6, 22)
            minute = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Random notes
            notes = random.choice(NOTES_TEMPLATES)
            
            entry = {
                "user_id": user_id,
                "category": category,
                "metric": template['metric'],
                "value": value,
                "unit": template['unit'],
                "timestamp": timestamp,
                "notes": notes,
                "metadata": {
                    "source": "fill_script",
                    "day_index": day
                }
            }
            
            await mongo_db.analytics_entries.insert_one(entry)
            entries_created += 1
            
            if entries_created % 50 == 0:
                print(f"  Created {entries_created} entries...")
    
    print(f"✓ Created {entries_created} entries")
    return entries_created


async def create_goals(mongo_db, user_id: int):
    """Create sample goals"""
    print("\nCreating sample goals...")
    
    goals_created = 0
    
    # Create goals for popular metrics
    goal_templates = [
        {'metric': 'steps', 'category': 'fitness', 'target_value': 10000, 'unit': 'steps'},
        {'metric': 'calories', 'category': 'fitness', 'target_value': 2500, 'unit': 'kcal'},
        {'metric': 'sleep_hours', 'category': 'health', 'target_value': 8, 'unit': 'hours'},
        {'metric': 'tasks_completed', 'category': 'productivity', 'target_value': 10, 'unit': 'tasks'},
        {'metric': 'mood_score', 'category': 'mood', 'target_value': 7, 'unit': 'score'},
    ]
    
    for template in goal_templates:
        goal = {
            **template,
            "user_id": user_id,
            "current_value": 0.0,  # Will be calculated by API
            "is_active": True,
            "created_at": datetime.now(UTC),
            "deadline": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
        }
        
        await mongo_db.goals.insert_one(goal)
        goals_created += 1
    
    print(f"✓ Created {goals_created} goals")
    return goals_created


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fill analytics data for testing')
    parser.add_argument('username', nargs='?', default=None, help='Username (default: first user)')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate data for (default: 30)')
    parser.add_argument('--entries-per-day', type=int, default=2, help='Entries per day (default: 2)')
    parser.add_argument('--clear', action='store_true', help='Clear existing data first')
    
    args = parser.parse_args()
    
    # Connect to databases
    print("Connecting to databases...")
    await connect_mongodb()
    mongo_db = get_mongodb()
    
    db = SessionLocal()
    try:
        # Get or find user
        if args.username:
            user = db.query(User).filter(User.username == args.username).first()
            if not user:
                print(f"Error: User '{args.username}' not found.")
                print("Available users:")
                for u in db.query(User).all():
                    print(f"  - {u.username} (ID: {u.id})")
                return 1
        else:
            user = db.query(User).first()
            if not user:
                print("Error: No users found in database.")
                print("Please create a user first or specify a username.")
                return 1
        
        print(f"Using user: {user.username} (ID: {user.id})")
        
        # Clear data if requested
        if args.clear:
            await clear_user_data(mongo_db, user.id)
        
        # Create entries
        entries_count = await create_entries(mongo_db, user.id, args.days, args.entries_per_day)
        
        # Create goals
        goals_count = await create_goals(mongo_db, user.id)
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  User: {user.username}")
        print(f"  Entries created: {entries_count}")
        print(f"  Goals created: {goals_count}")
        print(f"  Date range: {(datetime.now(UTC) - timedelta(days=args.days)).date()} to {datetime.now(UTC).date()}")
        print(f"{'='*60}\n")
        
        print("✓ Data filling completed successfully!")
        print("\nYou can now:")
        print("  - View the dashboard to see goals progress")
        print("  - Check analytics charts with the new data")
        print("  - Test the mobile app with real data")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
        await close_mongodb()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
