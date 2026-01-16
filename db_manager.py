"""
Database Manager - SQLite operations for Library Manager
"""
import sqlite3
import pandas as pd
import os
from pathlib import Path


class DatabaseManager:
    """Manages library data in SQLite database"""
    
    COLUMNS = ['ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords']
    
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database and create books table if not exists"""
        os.makedirs(os.path.dirname(self.db_file) or '.', exist_ok=True)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ISBN TEXT,
                Title TEXT,
                Author TEXT,
                Publisher TEXT,
                Year TEXT,
                Signature TEXT UNIQUE,
                Description TEXT,
                Keywords TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_file)
    
    def get_all_records(self):
        """Get all records as list of tuples"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {', '.join(self.COLUMNS)} FROM books")
        records = []
        for row in cursor.fetchall():
            # Convert None values to empty strings for consistency
            sanitized = tuple('' if val is None else val for val in row)
            records.append(sanitized)
        conn.close()
        return records
    
    def add_record(self, book_data):
        """Add a new book record"""
        isbn, title, author, publisher, year, signature, description, keywords = book_data
        
        # Check for duplicate signature if provided
        if signature and signature.strip():
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books WHERE Signature = ?", (signature,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise ValueError(f"Signature '{signature}' already exists")
            conn.close()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (ISBN, Title, Author, Publisher, Year, Signature, Description, Keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, publisher, year, signature if signature else None, description, keywords))
        conn.commit()
        conn.close()
    
    def update_record(self, index, book_data, original_isbn=None):
        """Update a book record by finding it by ISBN
        
        Args:
            index: ignored (kept for compatibility)
            book_data: tuple of (isbn, title, author, publisher, year, signature, description, keywords)
            original_isbn: the original ISBN to use for lookup (if user changed ISBN)
        """
        isbn, title, author, publisher, year, signature, description, keywords = book_data
        lookup_isbn = original_isbn if original_isbn else isbn
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find the record by ISBN
        cursor.execute("SELECT id FROM books WHERE ISBN = ?", (lookup_isbn,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Book with ISBN '{lookup_isbn}' not found")
        
        record_id = row[0]
        
        # Check for duplicate signature on OTHER records
        if signature and signature.strip():
            cursor.execute("SELECT COUNT(*) FROM books WHERE Signature = ? AND id != ?", (signature, record_id))
            if cursor.fetchone()[0] > 0:
                conn.close()
                raise ValueError(f"Signature '{signature}' already exists")
        
        # Update the record
        cursor.execute('''
            UPDATE books 
            SET ISBN = ?, Title = ?, Author = ?, Publisher = ?, Year = ?, 
                Signature = ?, Description = ?, Keywords = ?
            WHERE id = ?
        ''', (isbn, title, author, publisher, year, signature if signature else None, description, keywords, record_id))
        
        conn.commit()
        conn.close()
    
    def delete_record(self, index):
        """Delete a book record by index in current view"""
        records = self.get_all_records()
        if index >= len(records):
            raise ValueError("Invalid record index")
        
        isbn = records[index][0]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE ISBN = ?", (isbn,))
        conn.commit()
        conn.close()
    
    def filter_records(self, filters):
        """Filter records based on criteria"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = f"SELECT {', '.join(self.COLUMNS)} FROM books WHERE 1=1"
        params = []
        
        if filters.get('isbn'):
            query += " AND ISBN LIKE ?"
            params.append(f"%{filters['isbn']}%")
        
        if filters.get('title'):
            query += " AND Title LIKE ?"
            params.append(f"%{filters['title']}%")
        
        if filters.get('author'):
            query += " AND Author LIKE ?"
            params.append(f"%{filters['author']}%")
        
        if filters.get('publisher'):
            query += " AND Publisher LIKE ?"
            params.append(f"%{filters['publisher']}%")
        
        if filters.get('year'):
            query += " AND Year LIKE ?"
            params.append(f"%{filters['year']}%")
        
        if filters.get('signature'):
            query += " AND Signature LIKE ?"
            params.append(f"%{filters['signature']}%")
        
        if filters.get('keywords'):
            keywords = filters['keywords'].split(',')
            for kw in keywords:
                kw = kw.strip()
                if kw:
                    query += " AND Keywords LIKE ?"
                    params.append(f"%{kw}%")
        
        cursor.execute(query, params)
        records = []
        for row in cursor.fetchall():
            # Convert None values to empty strings for consistency
            sanitized = tuple('' if val is None else val for val in row)
            records.append(sanitized)
        conn.close()
        return records
    
    def export_to_tsv(self, file_path):
        """Export all records to TSV file"""
        records = self.get_all_records()
        df = pd.DataFrame(records, columns=self.COLUMNS)
        df.to_csv(file_path, sep='\t', index=False)
    
    def import_from_tsv(self, file_path):
        """Import data from TSV file and merge (skip duplicate Signatures)"""
        df = pd.read_csv(file_path, sep='\t', dtype={'Signature': 'object', 'Year': 'object'})
        
        # Validate columns
        missing_cols = set(self.COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        df = df[self.COLUMNS]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current signatures
        cursor.execute("SELECT Signature FROM books WHERE Signature IS NOT NULL")
        current_sigs = {row[0] for row in cursor.fetchall()}
        
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            signature = row['Signature']
            if pd.notna(signature) and str(signature).strip() in current_sigs:
                skipped += 1
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO books (ISBN, Title, Author, Publisher, Year, Signature, Description, Keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', tuple(row[col] if pd.notna(row[col]) else None for col in self.COLUMNS))
                imported += 1
            except sqlite3.IntegrityError:
                skipped += 1
        
        conn.commit()
        conn.close()
        
        return imported, skipped
