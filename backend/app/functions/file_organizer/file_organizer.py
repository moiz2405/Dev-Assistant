import os
import shutil
from pathlib import Path
import json
import difflib
from collections import defaultdict

# Define base paths
DOCUMENTS_PATH = Path.home() / 'Documents'
DOWNLOADS_PATH = Path.home() / 'Downloads'
CACHE_FILE = DOCUMENTS_PATH / 'file_index.json'

# File type groups
file_types = {
    'PDFs': ['.pdf'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif'],
    'WordDocs': ['.doc', '.docx'],
    'Spreadsheets': ['.xls', '.xlsx'],
    'TextFiles': ['.txt']
}

# Keyword groups for PDFs
pdf_keywords = {
    'Tax': ['tax', 'receipt'],
    'SalarySlips': ['salary', 'payslip'],
    'Notes': ['notes', 'lecture', 'class'],
}

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def categorize_pdf(file_name):
    name_lower = file_name.lower()
    for group, keywords in pdf_keywords.items():
        if any(kw in name_lower for kw in keywords):
            return group
    return 'Others'

def organize_file(file_path):
    ext = file_path.suffix.lower()
    file_name = file_path.name

    for group, extensions in file_types.items():
        if ext in extensions:
            if group == 'PDFs':
                category = categorize_pdf(file_name)
                target_dir = DOCUMENTS_PATH / group / category
            else:
                target_dir = DOCUMENTS_PATH / group
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), target_dir / file_name)
            return {
                "name": file_name,
                "path": str(target_dir / file_name),
                "type": group,
                "category": category if group == 'PDFs' else None
            }
    return None

def scan_downloads_and_move():
    print("[📦] Scanning Downloads for new files...")
    cache = load_cache()
    for item in Path(DOWNLOADS_PATH).iterdir():
        if item.is_file():
            result = organize_file(item)
            if result:
                cache[result["name"]] = result
                print(f"[✅] Moved: {result['name']} → {result['path']}")
    save_cache(cache)
