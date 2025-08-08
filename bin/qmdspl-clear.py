#!/usr/bin/env python3

from pathlib import Path
import shutil

def clean_directories_except_attachments():
    base = Path('.')

    for item in base.iterdir():
        if item.is_dir():
            if item.name.startswith("attachments"):
                print(f"🛡️  Skipping: {item}")
                continue
            print(f"🧹 Removing: {item}")
            shutil.rmtree(item)

if __name__ == "__main__":
    clean_directories_except_attachments()
