"""
Library Manager - Core logic for managing library data
"""
import pandas as pd
import os
from pathlib import Path

class LibraryManager:
    """Manages library data operations"""
    
    COLUMNS = ['ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords']
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.df = self.load_data()
    
    def load_data(self):
        """Load data from CSV file (semicolon-separated)"""
        if os.path.exists(self.data_file):
            try:
                df = pd.read_csv(self.data_file, sep=';', dtype={'Signature': 'object', 'Year': 'object'})
                return df
            except Exception:
                return self._create_empty_dataframe()
        return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """Create an empty dataframe with the correct columns"""
        return pd.DataFrame(columns=self.COLUMNS)
    
    def save_data(self):
        """Save data to CSV file (semicolon-separated)"""
        os.makedirs(os.path.dirname(self.data_file) or '.', exist_ok=True)
        self.df.to_csv(self.data_file, sep=';', index=False)
    
    def get_all_records(self):
        """Get all records as list of tuples"""
        return [tuple(row) for row in self.df.values]
    
    def add_record(self, book_data):
        """Add a new book record"""
        isbn, title, author, publisher, year, signature, description, keywords = book_data
        
        # Check for duplicate signature if provided
        if signature and not pd.isna(signature):
            if signature in self.df['Signature'].values:
                raise ValueError(f"Signature '{signature}' already exists")
        
        new_record = pd.DataFrame([{
            'ISBN': isbn,
            'Title': title,
            'Author': author,
            'Publisher': publisher,
            'Year': year,
            'Signature': signature if signature else None,
            'Description': description,
            'Keywords': keywords
        }])
        
        self.df = pd.concat([self.df, new_record], ignore_index=True)
        self.save_data()
    
    def update_record(self, index, book_data, original_isbn=None):
        """Update a book record by finding it by ISBN in the dataframe
        
        Args:
            index: ignored (kept for compatibility)
            book_data: tuple of (isbn, title, author, publisher, year, signature, description, keywords)
            original_isbn: the original ISBN to use for lookup (if user changed ISBN)
        """
        isbn, title, author, publisher, year, signature, description, keywords = book_data
        
        # Use original_isbn for lookup if provided (user might have changed ISBN)
        lookup_isbn = original_isbn if original_isbn else isbn
        
        # Find the row with matching ISBN
        isbn_match = self.df[self.df['ISBN'].astype(str).str.strip() == str(lookup_isbn).strip()]
        
        if isbn_match.empty:
            raise ValueError(f"Book with ISBN '{lookup_isbn}' not found")
        
        # Get the actual index of the matched row
        actual_index = isbn_match.index[0]
        
        # Check for duplicate signature on OTHER records
        if signature and not pd.isna(signature):
            existing_sig = self.df[(self.df['Signature'] == signature) & (self.df.index != actual_index)]
            if not existing_sig.empty:
                raise ValueError(f"Signature '{signature}' already exists")
        
        # Update all fields
        self.df.at[actual_index, 'ISBN'] = isbn
        self.df.at[actual_index, 'Title'] = title
        self.df.at[actual_index, 'Author'] = author
        self.df.at[actual_index, 'Publisher'] = publisher
        self.df.at[actual_index, 'Year'] = year
        self.df.at[actual_index, 'Signature'] = signature if signature else None
        self.df.at[actual_index, 'Description'] = description
        self.df.at[actual_index, 'Keywords'] = keywords
        
        self.save_data()
    
    def delete_record(self, index):
        """Delete a book record"""
        actual_index = self.df.index[index]
        self.df = self.df.drop(actual_index)
        self.df = self.df.reset_index(drop=True)
        self.save_data()
    
    def filter_records(self, filters):
        """Filter records based on criteria"""
        result = self.df.copy()
        
        if filters.get('isbn'):
            result = result[result['ISBN'].astype(str).str.contains(filters['isbn'], case=False, na=False)]
        
        if filters.get('title'):
            result = result[result['Title'].astype(str).str.contains(filters['title'], case=False, na=False)]
        
        if filters.get('author'):
            result = result[result['Author'].astype(str).str.contains(filters['author'], case=False, na=False)]
        
        if filters.get('publisher'):
            result = result[result['Publisher'].astype(str).str.contains(filters['publisher'], case=False, na=False)]
        
        if filters.get('year'):
            result = result[result['Year'].astype(str).str.contains(filters['year'], case=False, na=False)]
        
        if filters.get('signature'):
            result = result[result['Signature'].astype(str).str.contains(filters['signature'], case=False, na=False)]
        
        if filters.get('keywords'):
            # Keywords can be comma-separated; match any of them
            keywords = filters['keywords'].split(',')
            for kw in keywords:
                kw = kw.strip()
                if kw:
                    result = result[result['Keywords'].astype(str).str.contains(kw, case=False, na=False)]
        
        return [tuple(row) for row in result.values]
    
    def check_import_conflicts(self, file_path):
        """Check for Signature conflicts when importing (returns list of conflicting Signatures)"""
        try:
            df_import = pd.read_csv(file_path, sep=';', dtype={'Signature': 'object', 'Year': 'object'})
            # Validate columns
            missing_cols = set(self.COLUMNS) - set(df_import.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Check for duplicate Signatures (only non-null signatures)
            current_sigs = set(self.df[self.df['Signature'].notna()]['Signature'].astype(str).str.strip())
            import_sigs = set(df_import[df_import['Signature'].notna()]['Signature'].astype(str).str.strip())
            conflicts = list(current_sigs & import_sigs)
            return conflicts
        except Exception as e:
            raise ValueError(f"Error reading import file: {str(e)}")
    
    def import_csv_merge(self, file_path):
        """Import data from CSV file and merge with existing data (skip records with duplicate Signatures)"""
        try:
            df_import = pd.read_csv(file_path, sep=';', dtype={'Signature': 'object', 'Year': 'object'})
            # Validate columns
            missing_cols = set(self.COLUMNS) - set(df_import.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Reorder columns to match expected order
            df_import = df_import[self.COLUMNS]
            
            # Get current non-null Signatures
            current_sigs = set(self.df[self.df['Signature'].notna()]['Signature'].astype(str).str.strip())
            
            # Filter out records with duplicate Signatures (only check if Signature is not null)
            new_records = df_import[
                ~(
                    (df_import['Signature'].notna()) & 
                    (df_import['Signature'].astype(str).str.strip().isin(current_sigs))
                )
            ]
            
            # Append new records to existing dataframe
            if len(new_records) > 0:
                self.df = pd.concat([self.df, new_records], ignore_index=True)
                self.save_data()
        except Exception as e:
            raise ValueError(f"Error importing CSV: {str(e)}")
    
    def import_csv(self, file_path):
        """Import data from CSV file (semicolon-separated)"""
        try:
            df = pd.read_csv(file_path, sep=';', dtype={'Signature': 'object', 'Year': 'object'})
            # Validate columns
            missing_cols = set(self.COLUMNS) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Reorder columns to match expected order
            df = df[self.COLUMNS]
            self.df = df
            self.save_data()
        except Exception as e:
            raise Exception(f"Failed to import CSV: {str(e)}")
