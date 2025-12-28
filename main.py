#!/usr/bin/env python3
"""
Library Manager - Modern desktop app to manage your library
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import os
import sys
from pathlib import Path
from library_manager import LibraryManager


# Get the data file path - use script/executable directory, not current working directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APP_DIR = Path(sys.executable).parent
else:
    # Running as script
    APP_DIR = Path(__file__).parent

DATA_FILE = APP_DIR / 'library.csv'


class LibraryManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('MSF Library Manager')
        self.root.geometry('1500x850')
        self.root.minsize(1200, 700)
        
        self.manager = LibraryManager(str(DATA_FILE))
        self.current_filter = {}
        self.current_data = self.manager.get_all_records()
        
        self.setup_ui()
        self.refresh_table()
        
        # Bind copy shortcut
        self.root.bind('<Control-c>', self.copy_selection)
    
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Header with title
        header = ttk.Frame(main_container)
        header.pack(fill='x', padx=20, pady=(15, 10))
        
        header_row = ttk.Frame(header)
        header_row.pack(fill='x')
        
        title_label = ttk.Label(header_row, text='📚 Library Manager', font=('Segoe UI', 20, 'bold'))
        title_label.pack(anchor='w', side='left')
        
        self.header_info = ttk.Label(header_row, text='', font=('Segoe UI', 11))
        self.header_info.pack(anchor='e', side='right')
        
        # Filter section
        filter_frame = ttk.Labelframe(main_container, text='Search & Filter', padding=15)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # Row 1 - Search fields
        search_row = ttk.Frame(filter_frame)
        search_row.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row, text='ISBN:').pack(side='left', padx=(0, 5))
        self.filter_isbn = ttk.Entry(search_row, width=18)
        self.filter_isbn.pack(side='left', padx=(0, 15))
        
        ttk.Label(search_row, text='Title:').pack(side='left', padx=(0, 5))
        self.filter_title = ttk.Entry(search_row, width=18)
        self.filter_title.pack(side='left', padx=(0, 15))
        
        ttk.Label(search_row, text='Author:').pack(side='left', padx=(0, 5))
        self.filter_author = ttk.Entry(search_row, width=18)
        self.filter_author.pack(side='left', padx=(0, 15))
        
        ttk.Label(search_row, text='Publisher:').pack(side='left', padx=(0, 5))
        self.filter_publisher = ttk.Entry(search_row, width=18)
        self.filter_publisher.pack(side='left', padx=(0, 15), fill='x', expand=True)
        
        # Row 2 - More search fields
        search_row2 = ttk.Frame(filter_frame)
        search_row2.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row2, text='Year:').pack(side='left', padx=(0, 5))
        self.filter_year = ttk.Entry(search_row2, width=18)
        self.filter_year.pack(side='left', padx=(0, 15))
        
        ttk.Label(search_row2, text='Signature:').pack(side='left', padx=(0, 5))
        self.filter_signature = ttk.Entry(search_row2, width=18)
        self.filter_signature.pack(side='left', padx=(0, 15))
        
        ttk.Label(search_row2, text='Keywords (,-sep):').pack(side='left', padx=(0, 5))
        self.filter_keywords = ttk.Entry(search_row2, width=30)
        self.filter_keywords.pack(side='left', padx=(0, 15), fill='x', expand=True)
        
        # Row 3 - Action buttons
        button_row = ttk.Frame(filter_frame)
        button_row.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_row, text='🔍 Apply Filter', command=self.apply_filter, bootstyle='success').pack(side='left', padx=2)
        ttk.Button(button_row, text='✕ Clear', command=self.clear_filter, bootstyle='secondary').pack(side='left', padx=2)
        ttk.Button(button_row, text='💾 Export', command=self.export_csv, bootstyle='info').pack(side='left', padx=2)
        
        info_label = ttk.Label(button_row, text='💡 Shift+Click: range select  |  Ctrl+Click: multi-select  |  Ctrl+C: copy')
        info_label.pack(side='left', padx=20)
        
        # Table frame
        table_frame = ttk.Frame(main_container)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords')
        self.tree = ttk.Treeview(table_frame, columns=columns, height=20, show='headings')
        
        # Column widths
        widths = [90, 180, 130, 130, 60, 110, 220, 180]
        self.sort_column = None
        self.sort_reverse = False
        
        for col, width in zip(columns, widths):
            self.tree.column(col, width=width, anchor='w')
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Multi-select with Shift+Click for range selection
        self.tree.configure(selectmode='extended')
        self.last_selected_item = None
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # Action buttons
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(action_frame, text='➕ Add', command=self.add_book, bootstyle='success').pack(side='left', padx=2)
        ttk.Button(action_frame, text='✎ Edit', command=self.edit_book, bootstyle='info').pack(side='left', padx=2)
        ttk.Button(action_frame, text='🗑 Delete', command=self.delete_book, bootstyle='danger').pack(side='left', padx=2)
        ttk.Button(action_frame, text='🔄 Reload', command=self.refresh_table, bootstyle='secondary').pack(side='left', padx=2)
        ttk.Button(action_frame, text='📂 Import', command=self.import_csv, bootstyle='warning').pack(side='left', padx=2)
        ttk.Button(action_frame, text='⊗ Exit', command=self.root.quit, bootstyle='secondary').pack(side='right', padx=2)
        
        # Status bar
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(action_frame, textvariable=self.status_var)
        status_bar.pack(side='right', padx=20)
        
        self.update_status()
    
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, row in enumerate(self.current_data):
            self.tree.insert('', 'end', values=row)
        
        self.update_status()
    
    def update_status(self):
        total = len(self.manager.df)
        displayed = len(self.current_data)
        if displayed == total:
            self.status_var.set(f'Total: {total} records')
            self.header_info.config(text=f'Total books in library: {total}')
        else:
            self.status_var.set(f'Total: {total} | Filtered: {displayed} records')
            self.header_info.config(text=f'Showing {displayed} of {total} books')
    
    def on_tree_click(self, event):
        """Handle tree click events for Shift+Click range selection and Ctrl+Click multi-select"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Check if Ctrl is held (multi-select)
        if event.state & 0x4:  # Ctrl key flag
            # Let default behavior handle Ctrl+Click (toggle item in selection)
            return
        
        # Check if Shift is held (range select)
        if event.state & 0x1:  # Shift key flag
            if self.last_selected_item:
                # Get all items
                all_items = self.tree.get_children()
                
                # Get indices
                start_idx = all_items.index(self.last_selected_item)
                end_idx = all_items.index(item)
                
                # Ensure start is before end
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                
                # Select range (keep existing selection, add new range)
                current_selection = list(self.tree.selection())
                range_items = all_items[start_idx:end_idx + 1]
                
                # Combine: keep existing selections + add new range
                for i in range_items:
                    if i not in current_selection:
                        current_selection.append(i)
                
                self.tree.selection_set(current_selection)
                self.last_selected_item = None
            else:
                self.last_selected_item = item
        else:
            # No modifier key: single click selects only this item
            self.tree.selection_set(item)
            self.last_selected_item = item
    
    def sort_by_column(self, col):
        """Sort table by clicked column (toggle ascending/descending)"""
        columns = ('ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords')
        col_index = columns.index(col)
        
        # Toggle sort direction if same column, else new column
        if self.sort_column == col_index:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col_index
            self.sort_reverse = False
        
        # Update column headers with sort indicators
        for i, c in enumerate(columns):
            if i == col_index:
                indicator = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(c, text=c + indicator)
            else:
                self.tree.heading(c, text=c)
        
        # Sort data
        self.current_data = sorted(self.current_data, key=lambda x: str(x[col_index]).lower(), reverse=self.sort_reverse)
        self.refresh_table()
    
    def apply_filter(self):
        self.current_filter = {
            'isbn': self.filter_isbn.get().strip(),
            'title': self.filter_title.get().strip(),
            'author': self.filter_author.get().strip(),
            'publisher': self.filter_publisher.get().strip(),
            'year': self.filter_year.get().strip(),
            'signature': self.filter_signature.get().strip(),
            'keywords': self.filter_keywords.get().strip(),
        }
        self.current_data = self.manager.filter_records(self.current_filter)
        self.refresh_table()
    
    def clear_filter(self):
        self.filter_isbn.delete(0, 'end')
        self.filter_title.delete(0, 'end')
        self.filter_author.delete(0, 'end')
        self.filter_publisher.delete(0, 'end')
        self.filter_year.delete(0, 'end')
        self.filter_signature.delete(0, 'end')
        self.filter_keywords.delete(0, 'end')
        self.current_filter = {}
        self.current_data = self.manager.get_all_records()
        self.refresh_table()
    
    def export_csv(self):
        if not self.current_data:
            messagebox.showwarning('Export', 'No records to export')
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.current_data, columns=['ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords'])
                df.to_csv(file_path, sep=';', index=False)
                messagebox.showinfo('Export', f'✓ Exported {len(self.current_data)} records')
            except Exception as e:
                messagebox.showerror('Export Error', f'Error exporting: {str(e)}')
    
    def add_book(self):
        book = self.show_book_dialog()
        if book:
            try:
                self.manager.add_record(book)
                # Give file time to write
                import time
                time.sleep(0.2)
                
                # Force reload manager from disk
                self.manager = LibraryManager(str(DATA_FILE))
                
                # Refresh table with all data (clear filters to show the new book)
                self.current_filter = {}
                self.filter_isbn.delete(0, 'end')
                self.filter_title.delete(0, 'end')
                self.filter_author.delete(0, 'end')
                self.filter_publisher.delete(0, 'end')
                self.filter_year.delete(0, 'end')
                self.filter_signature.delete(0, 'end')
                self.filter_keywords.delete(0, 'end')
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
        
        # Get the book data directly from the tree item
        item = selection[0]
        tree_values = self.tree.item(item, 'values')
        book_data = tuple(tree_values)  # This is the current data shown in the row
        original_isbn = book_data[0]  # Save the ORIGINAL ISBN before editing
        
        book = self.show_book_dialog(book_data)
        
        if book:
            try:
                # Update the record - pass the original ISBN in case the user changed it
                self.manager.update_record(0, book, original_isbn=original_isbn)
                # Give file time to write
                import time
                time.sleep(0.2)
                
                # Force reload from disk
                self.manager = LibraryManager(str(DATA_FILE))
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
                # Get the actual ISBNs to delete (first column is ISBN)
                books_to_delete = []
                for item in selection:
                    index = self.tree.index(item)
                    isbn = self.current_data[index][0]  # ISBN is first column
                    books_to_delete.append(isbn)
                
                # Delete all matching ISBNs in a single pass (more efficient)
                indices_to_delete = []
                for isbn in books_to_delete:
                    for i, row in enumerate(self.manager.df.values):
                        if str(row[0]).strip() == str(isbn).strip():
                            indices_to_delete.append(i)
                            break
                
                # Sort indices in reverse order so we don't mess up indices when deleting
                for i in sorted(indices_to_delete, reverse=True):
                    self.manager.delete_record(i)
                
                # Reload manager from disk
                self.manager = LibraryManager(str(DATA_FILE))
                self.current_data = self.manager.filter_records(self.current_filter) if self.current_filter else self.manager.get_all_records()
                self.refresh_table()
                messagebox.showinfo('Success', f'✓ Deleted {len(books_to_delete)} book(s)')
            except Exception as e:
                messagebox.showerror('Error', f'Error deleting book: {str(e)}')
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                self.manager.import_csv(file_path)
                self.current_data = self.manager.get_all_records()
                self.current_filter = {}
                self.clear_filter()
                self.refresh_table()
                messagebox.showinfo('Import', f'✓ Imported {len(self.current_data)} records')
            except Exception as e:
                messagebox.showerror('Import Error', f'Error importing CSV: {str(e)}')
    
    def copy_selection(self, event=None):
        """Copy selected rows to clipboard (tab-separated)"""
        selection = self.tree.selection()
        if not selection:
            return
        
        try:
            rows = []
            for item in selection:
                index = self.tree.index(item)
                row = self.current_data[index]
                rows.append('\t'.join(str(val) for val in row))
            
            text = '\n'.join(rows)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
        except Exception as e:
            messagebox.showerror('Copy Error', f'Error copying: {str(e)}')
    
    def show_book_dialog(self, book_data=None):

        
        # Create a proper Toplevel dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title('Add Book' if not book_data else 'Edit Book')
        dialog.geometry('500x600')
        dialog.configure(bg='#212121')
        
        if book_data:
            isbn, title, author, publisher, year, signature, description, keywords = book_data
        else:
            isbn = title = author = publisher = year = signature = description = keywords = ''
        
        # Main container - dark background
        main_frame = tk.Frame(dialog, bg='#212121')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_label = tk.Label(main_frame, text='📖 Book Information', font=('Segoe UI', 13, 'bold'), bg='#212121', fg='#e0e0e0')
        header_label.pack(anchor='w', pady=(0, 15))
        
        entries = {}
        
        # Two-column layout - left side
        cols_frame = tk.Frame(main_frame, bg='#212121')
        cols_frame.pack(fill='x', pady=(0, 15))
        
        left_col = tk.Frame(cols_frame, bg='#212121')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_col = tk.Frame(cols_frame, bg='#212121')
        right_col.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        def add_field_to_col(parent, label_text, default_val, field_key):
            """Add a field (label + entry) to the given column"""
            field_container = tk.Frame(parent, bg='#212121')
            field_container.pack(fill='x', pady=(0, 10))
            
            label = tk.Label(field_container, text=label_text, font=('Segoe UI', 9, 'bold'), bg='#212121', fg='#e0e0e0')
            label.pack(anchor='w', pady=(0, 3))
            
            field = tk.Entry(field_container, width=28, bg='#313131', fg='#e0e0e0', insertbackground='#e0e0e0', border=1, relief='solid')
            field.insert(0, str(default_val))
            field.pack(fill='x')
            entries[field_key] = field
            return field
        
        # Left column fields
        add_field_to_col(left_col, 'ISBN', isbn, 'isbn_entry')
        add_field_to_col(left_col, 'Title', title, 'title_entry')
        add_field_to_col(left_col, 'Author', author, 'author_entry')
        
        # Right column fields
        add_field_to_col(right_col, 'Publisher', publisher, 'pub_entry')
        add_field_to_col(right_col, 'Year', year, 'year_entry')
        add_field_to_col(right_col, 'Signature', signature, 'sig_entry')
        
        # Description field (full width)
        desc_label = tk.Label(main_frame, text='Description', font=('Segoe UI', 9, 'bold'), bg='#212121', fg='#e0e0e0')
        desc_label.pack(anchor='w', pady=(0, 3))
        
        desc_field = tk.Text(main_frame, height=5, wrap='word', font=('Segoe UI', 9), bg='#313131', fg='#e0e0e0', insertbackground='#e0e0e0', border=1, relief='solid')
        desc_field.insert('1.0', str(description))
        desc_field.pack(fill='both', expand=True, pady=(0, 10))
        entries['desc_entry'] = desc_field
        
        # Keywords field
        kw_label = tk.Label(main_frame, text='Keywords (comma-separated)', font=('Segoe UI', 9, 'bold'), bg='#212121', fg='#e0e0e0')
        kw_label.pack(anchor='w', pady=(0, 3))
        
        kw_field = tk.Entry(main_frame, bg='#313131', fg='#e0e0e0', insertbackground='#e0e0e0', border=1, relief='solid')
        kw_field.insert(0, str(keywords))
        kw_field.pack(fill='x', pady=(0, 15))
        entries['kw_entry'] = kw_field
        
        # Bottom button frame - using tk.Frame with dark background
        button_frame = tk.Frame(main_frame, bg='#212121')
        button_frame.pack(fill='x', pady=(10, 0))
        
        result = {'data': None, 'ok': False}
        
        def save():
            try:
                result['data'] = (
                    entries['isbn_entry'].get(),
                    entries['title_entry'].get(),
                    entries['author_entry'].get(),
                    entries['pub_entry'].get(),
                    entries['year_entry'].get(),
                    entries['sig_entry'].get(),
                    entries['desc_entry'].get('1.0', 'end-1c'),
                    entries['kw_entry'].get()
                )
                result['ok'] = True
                dialog.destroy()
            except Exception as e:
                import traceback
                traceback.print_exc()
        
        # Success button (green)
        save_btn = tk.Button(button_frame, text='💾 Save', command=save, 
                            bg='#26a65b', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat', padx=12, pady=6, cursor='hand2', activebackground='#229954', activeforeground='white')
        save_btn.pack(side='left', padx=5)
        
        # Cancel button (red)
        cancel_btn = tk.Button(button_frame, text='✕ Cancel', command=dialog.destroy,
                              bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=12, pady=6, cursor='hand2', activebackground='#c0392b', activeforeground='white')
        cancel_btn.pack(side='left', padx=5)
        
        # Make dialog modal and wait for it to close
        dialog.transient(self.root)
        dialog.grab_set()

        self.root.wait_window(dialog)

        
        return result['data'] if result['ok'] else None


def main():
    root = ttk.Window(themename='darkly')
    app = LibraryManagerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
