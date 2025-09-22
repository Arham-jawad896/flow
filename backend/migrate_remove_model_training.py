import sqlite3

def migrate_remove_model_training(db_path="database/flow_ml.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if model_trained column exists and remove it
        cursor.execute("PRAGMA table_info(datasets)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'model_trained' in columns:
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            print("Removing model_trained column...")
            
            # Get the current table structure
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='datasets'")
            old_sql = cursor.fetchone()[0]
            
            # Create new table without model training columns
            new_sql = """
            CREATE TABLE datasets_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL,
                file_path VARCHAR NOT NULL,
                processed_file_path VARCHAR,
                original_filename VARCHAR NOT NULL,
                file_type VARCHAR NOT NULL,
                file_size INTEGER NOT NULL,
                rows_count INTEGER,
                columns_count INTEGER,
                preprocessing_status VARCHAR DEFAULT 'pending',
                preprocessing_log TEXT,
                preprocessing_options TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
            
            cursor.execute(new_sql)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO datasets_new 
                (id, name, file_path, processed_file_path, original_filename, file_type, 
                 file_size, rows_count, columns_count, preprocessing_status, preprocessing_log, 
                 created_at, updated_at, user_id)
                SELECT id, name, file_path, processed_file_path, original_filename, file_type,
                       file_size, rows_count, columns_count, preprocessing_status, preprocessing_log,
                       created_at, updated_at, user_id
                FROM datasets
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE datasets")
            cursor.execute("ALTER TABLE datasets_new RENAME TO datasets")
            
            print("Successfully removed model training columns")
        else:
            print("model_trained column not found, skipping removal")
            
        # Add preprocessing_options column if it doesn't exist
        if 'preprocessing_options' not in columns:
            cursor.execute("ALTER TABLE datasets ADD COLUMN preprocessing_options TEXT")
            print("Added preprocessing_options column")
        else:
            print("preprocessing_options column already exists")

        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_remove_model_training()
