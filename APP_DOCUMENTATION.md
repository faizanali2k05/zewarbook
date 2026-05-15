# Urdu Jewelry Inventory Management System

## Overview

This is a desktop **Jewelry Inventory Management System** built with:

- `Python`
- `PyQt6` (desktop UI)
- `SQLite` (local database)

The app is Urdu-first and uses right-to-left layout for the interface.

## Main Features

- Urdu login screen
- Inventory item add/search
- Low-stock alerts
- Customer/Supplier management
- Sales and Purchase entries
- Stock movement tracking
- Backup and Restore
- Urdu stock report PDF generation

## Default Login

- **Username:** `admin`
- **Password:** `admin123`

## Project Location

Current project path:

`C:\Users\Latitude 5510\.cursor\projects\empty-window\python-app`

If you copied it to Desktop, use:

`C:\Users\Latitude 5510\Desktop\python-app`

## Install and Run

```powershell
cd "C:\Users\Latitude 5510\.cursor\projects\empty-window\python-app"
py -m pip install -r requirements.txt
py app.py
```

## Launcher Notes

- `.bat` launcher opens a console window (normal).
- `.vbs` launcher runs app without showing console window.

Example hidden launcher command:

```vbscript
WshShell.Run "py app.py", 0, False
```

## Folder Structure

- `app.py` - app entry point
- `config/settings.py` - app settings and paths
- `db/schema.sql` - database schema
- `src/ui/` - login and main UI
- `src/services/` - business logic
- `src/repositories/` - database access
- `src/utils/` - helper utilities
- `tests/` - smoke test and QA checklist

## Notes

- This app uses a local SQLite database (no internet/server required).
- You can edit all source files anytime; launcher does not lock files.
- For production use, change default admin password and add stronger validation.
