"""
Viewer Data Manager - TSV file operations for read-only Books Viewer
"""
import pandas as pd
import os


class ViewerDataManager:
    """Manages read-only book data from TSV file"""
    
    COLUMNS = ['ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords']
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.df = self.load_data()
    
    def load_data(self):
        """Load data from TSV file"""
        if os.path.exists(self.data_file):
            try:
                df = pd.read_csv(self.data_file, sep='\t', dtype={'Signature': 'object', 'Year': 'object'})
                return df
            except Exception:
                return self._create_empty_dataframe()
        return self._create_empty_dataframe()
    
    def _create_empty_dataframe(self):
        """Create an empty dataframe with the correct columns"""
        return pd.DataFrame(columns=self.COLUMNS)
    
    def get_all_records(self):
        """Get all records as list of tuples"""
        return [tuple(row) for row in self.df.values]
    
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
            keywords = filters['keywords'].split(',')
            for kw in keywords:
                kw = kw.strip()
                if kw:
                    result = result[result['Keywords'].astype(str).str.contains(kw, case=False, na=False)]
        
        return [tuple(row) for row in result.values]
    
    def reload(self):
        """Reload data from file"""
        self.df = self.load_data()
