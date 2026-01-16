#!/usr/bin/env python3
"""
Library Manager - Modern desktop app to manage your library with SQLite database
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys
from pathlib import Path
from db_manager import DatabaseManager
from common_ui import BookTableUI


# Get the data file path - use script/executable directory
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

DB_FILE = APP_DIR / 'library.db'
VIEWER_TSV_FILE = APP_DIR / 'books-viewer' / 'books.tsv'


class LibraryManagerGUI(BookTableUI):
    def __init__(self, root):
        super().__init__(root, '📚 Library Manager', show_edit_mode=True)
        
        self.root.title('MSF Library Manager')
        self.root.geometry('1500x850')
        self.root.minsize(1200, 700)
        
        self.manager = DatabaseManager(str(DB_FILE))
        self.current_data = self.manager.get_all_records()
        
        self.setup_ui()
        self._setup_edit_buttons()
        self.toggle_edit_mode()  # Initialize edit mode state
        self.refresh_table()
    
    def _setup_edit_buttons(self):
        """Setup edit mode buttons"""
        self.add_btn = ttk.Button(self.edit_buttons_frame, text='➕ Add', command=self.add_book, bootstyle='success')
        self.add_btn.pack(side='left', padx=2)
        
        self.edit_btn = ttk.Button(self.edit_buttons_frame, text='✎ Edit', command=self.edit_book, bootstyle='info')
        self.edit_btn.pack(side='left', padx=2)
        
        self.delete_btn = ttk.Button(self.edit_buttons_frame, text='🗑 Delete', command=self.delete_book, bootstyle='danger')
        self.delete_btn.pack(side='left', padx=2)
        
        self.import_btn = ttk.Button(self.edit_buttons_frame, text='📂 Import', command=self.import_data, bootstyle='warning')
        self.import_btn.pack(side='left', padx=2)
    
    def toggle_edit_mode(self):
        """Show or hide edit/delete/import buttons"""
        enabled = self.edit_enabled.get()
        if enabled:
            self.edit_buttons_frame.pack(side='left', fill='x', expand=False, padx=5)
        else:
            self.edit_buttons_frame.pack_forget()
    
    def refresh_table(self):
        """Refresh table and update viewer TSV"""
        super().refresh_table()
        self._update_viewer_tsv()
    
    def _update_viewer_tsv(self):
        """Export current database to viewer TSV file"""
        try:
            os.makedirs(os.path.dirname(VIEWER_TSV_FILE), exist_ok=True)
            self.manager.export_to_tsv(str(VIEWER_TSV_FILE))
        except Exception as e:
            print(f"Warning: Could not update viewer TSV: {e}")
    
    def add_book(self):
        book = self.show_book_dialog()
        if book:
            try:
                self.manager.add_record(book)
                self.current_filter = {}
                self.clear_filter()
                self.current_data = self.manager.get_all_records()
                self.refresh_table()
                messagebox.showinfo('Success', '✓ Book added successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error adding book: {str(e)}')
    
    def edit_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Edit', 'Please select a book to edit')
            return
        
        item = selection[0]
        tree_values = self.tree.item(item, 'values')
        book_data = tuple(tree_values)
        original_isbn = book_data[0]
        
        book = self.show_book_dialog(book_data)
        
        if book:
            try:
                self.manager.update_record(0, book, original_isbn=original_isbn)
                self.current_data = self.manager.filter_records(self.current_filter) if self.current_filter else self.manager.get_all_records()
                self.refresh_table()
                messagebox.showinfo('Success', '✓ Book updated successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error updating book: {str(e)}')
    
    def delete_book(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Delete', 'Please select a book to delete')
            return
        
        if messagebox.askyesno('Confirm', f'Delete {len(selection)} book(s)?'):
            try:
                for item in selection:
                    index = self.tree.index(item)
                    self.manager.delete_record(index)
                
                self.current_data = self.manager.filter_records(self.current_filter) if self.current_filter else self.manager.get_all_records()
                self.refresh_table()
                messagebox.showinfo('Success', f'✓ Deleted {len(selection)} book(s)')
            except Exception as e:
                messagebox.showerror('Error', f'Error deleting book: {str(e)}')
    
    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('TSV Files', '*.tsv'), ('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                imported, skipped = self.manager.import_from_tsv(file_path)
                self.current_data = self.manager.get_all_records()
                self.current_filter = {}
                self.clear_filter()
                self.refresh_table()
                messagebox.showinfo('Import', f'✓ Imported {imported} records\n(Skipped {skipped} duplicates)')
            except Exception as e:
                messagebox.showerror('Import Error', f'Error importing file: {str(e)}')
    
    def show_book_dialog(self, book_data=None, read_only=False):
        """Show book add/edit dialog"""
        dialog = tk.Toplevel(self.root)
        
        if read_only:
            dialog.title('📖 View Book')
        else:
            dialog.title('Add Book' if not book_data else 'Edit Book')
        
        dialog.geometry('500x600')
        dialog.configure(bg='#212121')
        
        # Set icon
        icon_path = APP_DIR / 'icon' / 'msf-favicon.ico'
        if icon_path.exists():
            try:
                dialog.iconbitmap(str(icon_path))
            except:
                pass
        
        if book_data:
            isbn, title, author, publisher, year, signature, description, keywords = book_data
        else:
            isbn = title = author = publisher = year = signature = description = keywords = ''
        
        main_frame = tk.Frame(dialog, bg='#212121')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        header_label = tk.Label(main_frame, text='📖 Book Information', font=('Segoe UI', 13, 'bold'), 
                               bg='#212121', fg='#e0e0e0')
        header_label.pack(anchor='w', pady=(0, 15))
        
        entries = {}
        
        # Two-column layout
        cols_frame = tk.Frame(main_frame, bg='#212121')
        cols_frame.pack(fill='x', pady=(0, 15))
        
        left_col = tk.Frame(cols_frame, bg='#212121')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_col = tk.Frame(cols_frame, bg='#212121')
        right_col.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        def add_field(parent, label_text, default_val, field_key):
            container = tk.Frame(parent, bg='#212121')
            container.pack(fill='x', pady=(0, 10))
            
            label = tk.Label(container, text=label_text, font=('Segoe UI', 9, 'bold'), 
                           bg='#212121', fg='#e0e0e0')
            label.pack(anchor='w', pady=(0, 3))
            
            field = tk.Entry(container, width=28, bg='#313131', fg='#e0e0e0', 
                           insertbackground='#e0e0e0', border=1, relief='solid',
                           readonlybackground='#313131')
            field.insert(0, str(default_val))
            
            if read_only:
                field.config(state='readonly')
            
            field.pack(fill='x')
            entries[field_key] = field
            return field
        
        # Fields
        add_field(left_col, 'ISBN', isbn, 'isbn')
        add_field(left_col, 'Title', title, 'title')
        add_field(left_col, 'Author', author, 'author')
        add_field(right_col, 'Publisher', publisher, 'publisher')
        add_field(right_col, 'Year', year, 'year')
        add_field(right_col, 'Signature', signature, 'signature')
        
        # Description
        desc_label = tk.Label(main_frame, text='Description', font=('Segoe UI', 9, 'bold'), 
                            bg='#212121', fg='#e0e0e0')
        desc_label.pack(anchor='w', pady=(0, 3))
        
        desc_field = tk.Text(main_frame, height=5, wrap='word', font=('Segoe UI', 9), 
                           bg='#313131', fg='#e0e0e0', insertbackground='#e0e0e0')
        desc_field.insert('1.0', str(description))
        
        if read_only:
            desc_field.config(state='disabled')
        
        desc_field.pack(fill='both', expand=True, pady=(0, 10))
        entries['description'] = desc_field
        
        # Keywords
        kw_label = tk.Label(main_frame, text='Keywords (comma-separated)', font=('Segoe UI', 9, 'bold'), 
                          bg='#212121', fg='#e0e0e0')
        kw_label.pack(anchor='w', pady=(0, 3))
        
        kw_field = tk.Entry(main_frame, bg='#313131', fg='#e0e0e0', insertbackground='#e0e0e0',
                           readonlybackground='#313131')
        kw_field.insert(0, str(keywords))
        
        if read_only:
            kw_field.config(state='readonly')
        
        kw_field.pack(fill='x', pady=(0, 15))
        entries['keywords'] = kw_field
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#212121')
        button_frame.pack(fill='x', pady=(10, 0))
        
        result = {'data': None}
        
        def save():
            result['data'] = (
                entries['isbn'].get(),
                entries['title'].get(),
                entries['author'].get(),
                entries['publisher'].get(),
                entries['year'].get(),
                entries['signature'].get(),
                entries['description'].get('1.0', 'end-1c'),
                entries['keywords'].get()
            )
            dialog.destroy()
        
        if read_only:
            tk.Button(button_frame, text='✕ Close', command=dialog.destroy,
                     bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=12, pady=6).pack(side='left', padx=5)
        else:
            tk.Button(button_frame, text='💾 Save', command=save,
                     bg='#26a65b', fg='white', font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=12, pady=6).pack(side='left', padx=5)
            tk.Button(button_frame, text='✕ Cancel', command=dialog.destroy,
                     bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=12, pady=6).pack(side='left', padx=5)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        return result['data']


def main():
    root = ttk.Window(themename='darkly')
    
    icon_path = APP_DIR / 'icon' / 'msf-favicon.ico'
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except:
            pass
    
    root.configure(bg='#212121')
    
    app = LibraryManagerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
