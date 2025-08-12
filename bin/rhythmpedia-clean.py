#!/usr/bin/env python3

from pathlib import Path
import sys, pathlib;
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));
from lib import rhythmpedia

# CLI
if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        rhythmpedia.qmd_all_masters( rhythmpedia.clean_directories_except_attachments_qmd, Path(a) )

#    if len(sys.argv) > 1:
#        for a in sys.argv[1:]: rhythmpedia.copy_lang_qmd(Path(a))
#    else:
#        rhythmpedia.qmd_all_masters( rhythmpedia.copy_lang_qmd, ".")

