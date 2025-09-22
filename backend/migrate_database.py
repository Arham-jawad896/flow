#!/usr/bin/env python3
"""
Database migration script to add model training columns to existing datasets table.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns to the datasets table for model training."""
    
    # Get the database path
    db_path = Path("database/flow_ml.db")
    
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        return
    
    # Connect to the database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if the new columns already exist
        cursor.execute("PRAGMA table_info(datasets)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'model_trained' not in columns:
            print("Adding model_trained column...")
            cursor.execute("ALTER TABLE datasets ADD COLUMN model_trained BOOLEAN DEFAULT 0")
        
        if 'model_type' not in columns:
            print("Adding model_type column...")
            cursor.execute("ALTER TABLE datasets ADD COLUMN model_type VARCHAR")
        
        if 'model_metrics' not in columns:
            print("Adding model_metrics column...")
            cursor.execute("ALTER TABLE datasets ADD COLUMN model_metrics TEXT")
        
        # Commit the changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
