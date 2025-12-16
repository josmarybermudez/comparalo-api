import sqlite3
import os
from typing import List, Dict, Optional
from contextlib import contextmanager

# SQLite configuration
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "scraper.db")


class SQLiteDB:
    """SQLite database manager for product storage"""
    
    def __init__(self):
        self.db_path = DATABASE_FILE
        self.connection = None
    
    def connect(self):
        """Establish connection to SQLite and create table if needed"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            self._create_table()
            self._migrate_schema()  # Add migration check
            print(f"✓ Connected to SQLite database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"✗ Failed to connect to SQLite: {e}")
            return False
    
    def _create_table(self):
        """Create products table if it doesn't exist, with a UNIQUE constraint."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT NOT NULL,
                product_url TEXT NOT NULL,
                store TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- 🆕 Ensures no two entries share the same URL within the same store.
                -- This is critical for the INSERT OR REPLACE (UPSERT) logic.
                UNIQUE(product_url, store) 
            )
        """)
        self.connection.commit()
        print("✓ Products table ready (with UNIQUE constraint on product_url and store)")
    
    # def _migrate_schema(self):
    #     """Migrate existing database schema if needed"""
    #     cursor = self.connection.cursor()
        
    #     # Check if 'store' column exists
    #     cursor.execute("PRAGMA table_info(products)")
    #     columns = [column[1] for column in cursor.fetchall()]
        
    #     if 'store' not in columns:
    #         print("⚠ Migrating database: adding 'store' column...")
    #         cursor.execute("ALTER TABLE products ADD COLUMN store TEXT DEFAULT 'unknown'")
    #         self.connection.commit()
    #         print("✓ Database migration complete")
    
    def _migrate_schema(self):
        """Migrate existing database schema if needed (ensures UNIQUE constraint)."""
        cursor = self.connection.cursor()
        
        # 1. Check if 'store' column exists (your original check)
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'store' not in columns:
            print("⚠ Migrating database: adding 'store' column...")
            cursor.execute("ALTER TABLE products ADD COLUMN store TEXT DEFAULT 'unknown'")
            self.connection.commit()
            print("✓ Database migration complete (added 'store')")

        # 2. 🆕 Check if the UNIQUE constraint exists
        # Get the index list for the 'products' table
        cursor.execute("PRAGMA index_list(products)")
        indexes = cursor.fetchall()
        
        # Look for a unique index that covers both product_url and store
        has_unique_constraint = False
        for index in indexes:
            
            # 🛑 CORRECTED LINE: Check index[2] which is the integer 'unique' flag (1 or 0)
            if index[2] == 1: 
                # Check the columns of the index
                index_name = index[1]
                cursor.execute(f"PRAGMA index_info({index_name})")
                index_columns = sorted([info[2] for info in cursor.fetchall()])
                
                # Check if this unique index covers the required columns
                if index_columns == ['product_url', 'store']:
                    has_unique_constraint = True
                    break

        if not has_unique_constraint:
            print("⚠ Migrating database: UNIQUE constraint (product_url, store) missing.")
            print("   Temporarily dropping and recreating table to apply constraint.")
            
            # This is the easiest way to add complex constraints in SQLite
            # Backup table data first (optional, but highly recommended in production)
            
            # For simplicity in a development environment, we will just drop and recreate:
            
            try:
                # Execute the command you tried to run: DROP TABLE
                cursor.execute("DROP TABLE products") 
                self.connection.commit()
                print("   Table dropped.")
                
                # Now call the method that creates the table with the new UNIQUE constraint
                self._create_table()
                
            except sqlite3.Error as e:
                print(f"✗ Failed to drop/recreate table: {e}. Please manually check scraper.db.")
                sys.exit(1)

            print("✓ Database migration complete (added UNIQUE constraint)")

    def clear_products(self, store: Optional[str] = None):
        """
        Clear products from the table
        
        Args:
            store: If provided, only clear products from this store. If None, clear all products.
        """
        if self.connection:
            cursor = self.connection.cursor()
            if store:
                cursor.execute("DELETE FROM products WHERE store = ?", (store,))
                print(f"✓ Cleared products from store: {store}")
            else:
                cursor.execute("DELETE FROM products")
                print(f"✓ Cleared all products from database")
            self.connection.commit()
            deleted_count = cursor.rowcount
            print(f"  ({deleted_count} products deleted)")
            return deleted_count
        return 0
    

    def insert_products(self, products: list[dict], store: str):
        """
        Inserts or UPDATES a list of products using ON CONFLICT DO UPDATE.
        Requires the 'store' name as a positional argument (which you are now passing).
        """
        if self.connection and products:
            cursor = self.connection.cursor()
            
            # 1. Define the SQL statement using ON CONFLICT
            # We assume the table has a UNIQUE constraint on (product_url, store).
            sql_query = """
            INSERT INTO products 
                (product_name, price, image_url, product_url, store, created_at) 
            VALUES 
                (?, ?, ?, ?, ?, ?)
            ON CONFLICT (product_url, store) 
            DO UPDATE SET
                price = excluded.price,
                product_name = excluded.product_name,
                image_url = excluded.image_url,
                created_at = excluded.created_at;
            """
            
            # 2. Prepare the data with all six values (including a dynamic timestamp)
            import time
            current_time = int(time.time()) # Or use datetime if you prefer
            
            data_to_insert = [
                (
                    p['product_name'], 
                    p['price'], 
                    p['image_url'], 
                    p['product_url'], 
                    store, 
                    current_time  # The created_at is the 6th value
                ) 
                for p in products
            ]
            
            # 3. Execute the statement
            cursor.executemany(sql_query, data_to_insert)
            self.connection.commit()
            
            print(f"✓ Processed {len(products)} product records (Insert/Update) from {store}")
            return len(products)
        return 0
    
    def get_all_products(self) -> List[Dict]:
        """Retrieve all products from the database"""
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT product_name, price, image_url, product_url, store FROM products")
            rows = cursor.fetchall()
            # Convert Row objects to dictionaries
            products = [dict(row) for row in rows]
            return products
        return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ SQLite connection closed")


# Singleton instance
db = SQLiteDB()
