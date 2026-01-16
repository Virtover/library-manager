"""
Common UI Components - Shared between Library Manager and Books Viewer
"""
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from tkinter import filedialog, messagebox


class BookTableUI:
    """Common table and filter UI for book display"""
    
    COLUMNS = ['ISBN', 'Title', 'Author', 'Publisher', 'Year', 'Signature', 'Description', 'Keywords']
    COLUMN_WIDTHS = [90, 180, 130, 130, 60, 110, 220, 180]
    
    def __init__(self, root, title, show_edit_mode=True):
        self.root = root
        self.title = title
        self.show_edit_mode = show_edit_mode
        
        self.current_filter = {}
        self.current_data = []
        self.sort_column = None
        self.sort_reverse = False
        self.last_selected_item = None
        
        # These will be set by subclass
        self.manager = None
        
    def setup_ui(self):
        """Setup the complete UI"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Header
        self._create_header(main_container)
        
        # Filter section
        self._create_filter_section(main_container)
        
        # Action buttons frame
        action_frame = self._create_action_frame(main_container)
        
        # Table frame
        self._create_table(main_container)
        
        # Status bar
        self._create_status_bar(action_frame)
        
        # Bind copy shortcut
        self.root.bind('<Control-c>', self.copy_selection)
    
    def _create_header(self, parent):
        """Create header with title"""
        header = ttk.Frame(parent)
        header.pack(fill='x', padx=20, pady=(15, 10))
        
        header_row = ttk.Frame(header)
        header_row.pack(fill='x')
        
        title_label = ttk.Label(header_row, text=self.title, font=('Segoe UI', 20, 'bold'))
        title_label.pack(anchor='w', side='left')
        
        self.header_info = ttk.Label(header_row, text='', font=('Segoe UI', 11))
        self.header_info.pack(anchor='e', side='right')
    
    def _create_filter_section(self, parent):
        """Create filter/search section"""
        filter_frame = ttk.Labelframe(parent, text='Search & Filter', padding=15)
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
        ttk.Button(button_row, text='💾 Export', command=self.export_data, bootstyle='info').pack(side='left', padx=2)
        
        info_label = ttk.Label(button_row, text='💡 Shift+Click: range select  |  Ctrl+Click: multi-select  |  Ctrl+C: copy')
        info_label.pack(side='left', padx=20)
    
    def _create_action_frame(self, parent):
        """Create action buttons frame"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x', padx=20, pady=10, side='bottom')
        
        if self.show_edit_mode:
            # Safety lock checkbox
            self.edit_enabled = tk.BooleanVar(value=False)
            safety_checkbox = ttk.Checkbutton(action_frame, text='🔓 Enable Edit Mode', 
                                             variable=self.edit_enabled, command=self.toggle_edit_mode)
            safety_checkbox.pack(side='left', padx=5)
            
            # Edit/Delete buttons container
            self.edit_buttons_frame = ttk.Frame(action_frame)
            # Will be populated by subclass
        
        # Always visible buttons
        ttk.Button(action_frame, text='🔄 Reload', command=self.refresh_table, bootstyle='secondary').pack(side='left', padx=2)
        ttk.Button(action_frame, text='⊗ Exit', command=self.root.quit, bootstyle='secondary').pack(side='right', padx=2)
        
        return action_frame
    
    def _create_table(self, parent):
        """Create the book table"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10, side='top')
        
        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=self.COLUMNS, height=20, show='headings')
        
        # Configure style
        style = ttk.Style()
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=24)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        
        # Configure columns
        for col, width in zip(self.COLUMNS, self.COLUMN_WIDTHS):
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
        
        # Multi-select setup
        self.tree.configure(selectmode='extended')
        self.tree.bind('<Button-1>', self.on_tree_click)
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
    
    def _create_status_bar(self, action_frame):
        """Create status bar"""
        self.status_var = tk.StringVar(value='Ready')
        status_bar = ttk.Label(action_frame, textvariable=self.status_var)
        status_bar.pack(side='right', padx=20)
    
    def refresh_table(self):
        """Refresh the table display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in self.current_data:
            self.tree.insert('', 'end', values=row)
        
        self.update_status()
    
    def update_status(self):
        """Update status bar and header info"""
        if hasattr(self.manager, 'df'):
            total = len(self.manager.df)
        else:
            total = len(self.manager.get_all_records())
        
        displayed = len(self.current_data)
        if displayed == total:
            self.status_var.set(f'Total: {total} records')
            self.header_info.config(text=f'Total books: {total}')
        else:
            self.status_var.set(f'Total: {total} | Filtered: {displayed} records')
            self.header_info.config(text=f'Showing {displayed} of {total} books')
    
    def on_tree_click(self, event):
        """Handle tree click for range/multi selection"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        if event.state & 0x4:  # Ctrl
            return
        
        if event.state & 0x1:  # Shift
            if self.last_selected_item:
                all_items = self.tree.get_children()
                start_idx = all_items.index(self.last_selected_item)
                end_idx = all_items.index(item)
                
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx
                
                current_selection = list(self.tree.selection())
                range_items = all_items[start_idx:end_idx + 1]
                
                for i in range_items:
                    if i not in current_selection:
                        current_selection.append(i)
                
                self.tree.selection_set(current_selection)
                self.last_selected_item = None
            else:
                self.last_selected_item = item
        else:
            self.tree.selection_set(item)
            self.last_selected_item = item
    
    def on_tree_double_click(self, event):
        """Handle double-click to view book info"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        tree_values = self.tree.item(item, 'values')
        book_data = tuple(tree_values)
        self.show_book_dialog(book_data, read_only=True)
    
    def sort_by_column(self, col):
        """Sort table by column"""
        col_index = self.COLUMNS.index(col)
        
        if self.sort_column == col_index:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col_index
            self.sort_reverse = False
        
        # Update headers
        for i, c in enumerate(self.COLUMNS):
            if i == col_index:
                indicator = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(c, text=c + indicator)
            else:
                self.tree.heading(c, text=c)
        
        # Sort data
        self.current_data = sorted(self.current_data, key=lambda x: str(x[col_index]).lower(), reverse=self.sort_reverse)
        self.refresh_table()
    
    def apply_filter(self):
        """Apply current filter"""
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
        """Clear all filters"""
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
    
    def export_data(self):
        """Export filtered data"""
        if not self.current_data:
            messagebox.showwarning('Export', 'No records to export')
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.tsv',
            filetypes=[('TSV Files', '*.tsv'), ('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.current_data, columns=self.COLUMNS)
                df.to_csv(file_path, sep='\t', index=False)
                messagebox.showinfo('Export', f'✓ Exported {len(self.current_data)} records')
            except Exception as e:
                messagebox.showerror('Export Error', f'Error exporting: {str(e)}')
    
    def copy_selection(self, event=None):
        """Copy selected rows to clipboard"""
        selection = self.tree.selection()
        if not selection:
            return
        
        rows = []
        for item in selection:
            values = self.tree.item(item, 'values')
            rows.append('\t'.join(str(v) for v in values))
        
        clipboard_text = '\n'.join(rows)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
    
    def show_book_dialog(self, book_data, read_only=False):
        """Show book details dialog - to be implemented by subclass"""
        pass
    
    def toggle_edit_mode(self):
        """Toggle edit mode - to be implemented by subclass"""
        pass
