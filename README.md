# Library Manager

A simple, lightweight desktop application for managing your book library.

## Features
- **Add, Edit, Delete** books in your library
- **Filter** by ISBN, Title, Author, Publisher, Year, Signature, or Keywords
- **Import TSV** data from existing libraries
- **Export TSV** of filtered results
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
- `library.tsv` - your library data file

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

## Data Format
The app stores data in a tab-separated values (TSV) file (`library.tsv`) with the following columns:

```
ISBN	Title	Author	Publisher	Year	Signature	Description	Keywords
```

You can import TSV files with the same format, and export filtered results.

## System Requirements
- Windows 7+, macOS 10.12+, or Linux
- No installation needed - just run the executable

## Notes
- Signatures must be unique (if provided)
- Empty or null signature values are allowed
- All filtering is case-insensitive
- TSV files are automatically saved after any changes

## License & Attribution

**Application**: MIT License

**Icon**: The application icon is derived from [Logo Misjonarzy Świętej Rodziny](https://pl.wikipedia.org/wiki/Plik:Logo_Misjonarzy_%C5%9Awi%C4%99tej_Rodziny.svg) from Wikimedia Commons, used under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

- **Original Creator**: Misjonarze Świętej Rodziny
- **Source**: Wikimedia Commons
- **License**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

