#!/usr/bin/env python3
"""
Books Viewer - Read-only viewer for books.tsv
"""
import tkinter as tk
import ttkbootstrap as ttk
import sys
from pathlib import Path
from viewer_data import ViewerDataManager
from common_ui import BookTableUI


# Get the data file path
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

TSV_FILE = APP_DIR / 'books.tsv'


class BooksViewerGUI(BookTableUI):
    def __init__(self, root):
        super().__init__(root, '📖 Books Viewer', show_edit_mode=False)
        
        self.root.title('MSF Books Viewer')
        self.root.geometry('1500x850')
        self.root.minsize(1200, 700)
        
        self.manager = ViewerDataManager(str(TSV_FILE))
        self.current_data = self.manager.get_all_records()
        
        self.setup_ui()
        # Call parent's refresh_table to avoid reloading file during initialization
        BookTableUI.refresh_table(self)
    
    def refresh_table(self):
        """Refresh table and reload data from file - only reload if no current filter"""
        if not self.current_filter:
            # Only reload if we're not filtering
            self.manager.reload()
            self.current_data = self.manager.get_all_records()
        # Call parent's refresh_table to display current_data without reloading
        BookTableUI.refresh_table(self)
    
    def show_book_dialog(self, book_data=None, read_only=False):
        """Show book details in read-only mode"""
        if not book_data:
            return None
        
        dialog = tk.Toplevel(self.root)
        dialog.title('📖 View Book')
        dialog.geometry('500x600')
        dialog.configure(bg='#212121')
        
        # Set icon
        icon_path = APP_DIR / 'icon' / 'msf-favicon.ico'
        if icon_path.exists():
            try:
                dialog.iconbitmap(str(icon_path))
            except:
                pass
        
        isbn, title, author, publisher, year, signature, description, keywords = book_data
        
        main_frame = tk.Frame(dialog, bg='#212121')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        header_label = tk.Label(main_frame, text='📖 Book Information', font=('Segoe UI', 13, 'bold'),
                               bg='#212121', fg='#e0e0e0')
        header_label.pack(anchor='w', pady=(0, 15))
        
        # Two-column layout
        cols_frame = tk.Frame(main_frame, bg='#212121')
        cols_frame.pack(fill='x', pady=(0, 15))
        
        left_col = tk.Frame(cols_frame, bg='#212121')
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_col = tk.Frame(cols_frame, bg='#212121')
        right_col.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        def add_field(parent, label_text, value):
            container = tk.Frame(parent, bg='#212121')
            container.pack(fill='x', pady=(0, 10))
            
            label = tk.Label(container, text=label_text, font=('Segoe UI', 9, 'bold'),
                           bg='#212121', fg='#e0e0e0')
            label.pack(anchor='w', pady=(0, 3))
            
            field = tk.Entry(container, width=28, bg='#313131', fg='#e0e0e0', border=1, relief='solid',
                           readonlybackground='#313131')
            field.insert(0, str(value))
            field.config(state='readonly')
            field.pack(fill='x')
        
        # Fields
        add_field(left_col, 'ISBN', isbn)
        add_field(left_col, 'Title', title)
        add_field(left_col, 'Author', author)
        add_field(right_col, 'Publisher', publisher)
        add_field(right_col, 'Year', year)
        add_field(right_col, 'Signature', signature)
        
        # Description
        desc_label = tk.Label(main_frame, text='Description', font=('Segoe UI', 9, 'bold'),
                            bg='#212121', fg='#e0e0e0')
        desc_label.pack(anchor='w', pady=(0, 3))
        
        desc_field = tk.Text(main_frame, height=5, wrap='word', font=('Segoe UI', 9),
                           bg='#313131', fg='#e0e0e0')
        desc_field.insert('1.0', str(description))
        desc_field.config(state='disabled')
        desc_field.pack(fill='both', expand=True, pady=(0, 10))
        
        # Keywords
        kw_label = tk.Label(main_frame, text='Keywords', font=('Segoe UI', 9, 'bold'),
                          bg='#212121', fg='#e0e0e0')
        kw_label.pack(anchor='w', pady=(0, 3))
        
        kw_field = tk.Entry(main_frame, bg='#313131', fg='#e0e0e0',
                           readonlybackground='#313131')
        kw_field.insert(0, str(keywords))
        kw_field.config(state='readonly')
        kw_field.pack(fill='x', pady=(0, 15))
        
        # Close button
        button_frame = tk.Frame(main_frame, bg='#212121')
        button_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(button_frame, text='✕ Close', command=dialog.destroy,
                 bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=12, pady=6).pack(side='left', padx=5)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)


def main():
    root = ttk.Window(themename='darkly')
    
    icon_path = APP_DIR / 'icon' / 'msf-favicon.ico'
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except:
            pass
    
    root.configure(bg='#212121')
    
    app = BooksViewerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
