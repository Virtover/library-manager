# Library Manager

A simple, lightweight desktop application for managing your book library.

## Features
- **Add, Edit, Delete** books in your library
- **Filter** by ISBN, Title, Author, Publisher, Year, Signature, or Keywords
- **Import CSV** data from existing libraries
- **Export CSV** of filtered results
- **Unique Signatures** (optional) for book identification
- Small, single-file executable - no installation needed

## Quick Start

### Run from Source (Development)
```bash
pip install -r requirements.txt
python main.py
```

### Build Standalone Executable
```bash
pip install pyinstaller
python build.py
```

This creates a folder `MSF Library Manager` with:
- `library-manager.exe` - the executable
- `library.csv` - your library data file

Simply open the folder and run the .exe file.

## Data Fields
- **ISBN** - ISBN number
- **Title** - Book title
- **Author** - Author name
- **Publisher** - Publishing company
- **Year** - Publication year
- **Signature** - Unique identifier (optional, can be empty)
- **Description** - Book description
- **Keywords** - Search keywords

## CSV Format
The app stores data in a simple CSV file (`library.csv`) with the following columns:

```
ISBN,Title,Author,Publisher,Year,Signature,Description,Keywords
```

You can import CSV files with the same format, and export filtered results.

## System Requirements
- Windows 7+, macOS 10.12+, or Linux
- No installation needed - just run the executable

## Notes
- Signatures must be unique (if provided)
- Empty or null signature values are allowed
- All filtering is case-insensitive
- CSV files are automatically saved after any changes
