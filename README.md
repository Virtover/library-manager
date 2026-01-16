# Library Manager

A modern desktop application system for managing your book library with both management and viewer capabilities.

## Applications

### 1. Library Manager
Full-featured book management application with SQLite database storage.

**Features:**
- **Add, Edit, Delete** books in your library
- **Filter** by ISBN, Title, Author, Publisher, Year, Signature, or Keywords
- **Import TSV** data from existing libraries
- **Export TSV** of filtered results
- **Unique Signatures** (optional) for book identification
- **SQLite Database** for reliable data storage
- **Edit Mode Protection** with safety lock
- Automatically syncs data to viewer

### 2. Books Viewer
Read-only viewer for browsing book collections.

**Features:**
- **View-Only Access** - no accidental edits
- **Filter & Search** capabilities
- **Export** filtered results
- **Lightweight** - reads from books.tsv file
- **Real-time Updates** from Library Manager
- Perfect for public display or shared access

## Quick Start

### Run from Source (Development)
```bash
pip install -r requirements.txt

# Run Manager
python main.py

# Run Viewer
cd books-viewer
python viewer.py
```

### Build Standalone Executables
```bash
pip install pyinstaller
python build.py
```

This creates a folder `MSF Library Manager` with:
- `library-manager.exe` - the full manager application
- `library.db` - SQLite database file
- `books-viewer/books-viewer.exe` - the read-only viewer
- `books-viewer/books.tsv` - synchronized book data for viewer

## Architecture

**Library Manager** stores data in `library.db` (SQLite database) and automatically exports to `books-viewer/books.tsv` whenever data changes.

**Books Viewer** reads from `books.tsv` file only, providing read-only access without database dependencies.

## Data Fields
- **ISBN** - ISBN number
- **Title** - Book title
- **Author** - Author name
- **Publisher** - Publishing company
- **Year** - Publication year
- **Signature** - Unique identifier (optional, can be empty)
- **Description** - Book description
- **Keywords** - Search keywords

## System Requirements
- Windows 7+, macOS 10.12+, or Linux
- No installation needed - just run the executable

## Notes
- **Manager**: Signatures must be unique (if provided)
- Empty or null signature values are allowed
- All filtering is case-insensitive
- Manager automatically syncs to viewer on any change
- **Viewer**: Automatically reloads data when refreshed
- TSV files are tab-separated values format

## Development Structure
```
library-manager/
├── main.py              # Library Manager application
├── db_manager.py        # SQLite database operations
├── common_ui.py         # Shared UI components
├── library.db           # SQLite database (created on first run)
├── books-viewer/
│   ├── viewer.py        # Books Viewer application
│   ├── viewer_data.py   # TSV file operations
│   ├── common_ui.py     # Shared UI (copy)
│   └── books.tsv        # Synchronized book data
└── build.py             # Build script for both apps
```

## License & Attribution

**Application**: MIT License

**Icon**: The application icon is derived from [Logo Misjonarzy Świętej Rodziny](https://pl.wikipedia.org/wiki/Plik:Logo_Misjonarzy_%C5%9Awi%C4%99tej_Rodziny.svg) from Wikimedia Commons, used under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

- **Original Creator**: Misjonarze Świętej Rodziny
- **Source**: Wikimedia Commons
- **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

