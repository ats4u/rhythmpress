#!/usr/bin/env python3

from pathlib import Path
import sys, pathlib;
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]));
from lib import rhythmpedia

def _hdr_start(text: str, it) -> int:
    # start of the header line (prev '\n' before section_start_char; -1→0)
    return text.rfind("\n", 0, int(it["section_start_char"])) + 1

def split_master_qmd(master_path: Path) -> None:
    print(f"\n→ {master_path}")
    lang = rhythmpedia._lang_id_from_filename(master_path)
    text = master_path.read_text(encoding="utf-8")

    items = rhythmpedia.parse_qmd_teasers(
        text, min_level=2, max_level=6,
        strip_html_in_title=False, normalize_ws=False, respect_frontmatter=True
    )
    if not items: print("  (no headers)"); return

    items = rhythmpedia.proc_qmd_teasers(items, str(master_path.parent), lang)
    h2s   = [it for it in items if int(it["level"]) == 2]
    if not h2s: print("  (no H2)"); return

    # preamble (everything before earliest H2 header)
    preamble = text[:min(_hdr_start(text, it) for it in h2s)]

    # 3-liner per section: slice → mkdir → write (H2 only per spec)
    for it in h2s:
        beg, end = _hdr_start(text, it), int(it["section_end_char"])
        p: Path = it["out_path"]
        p.parent.mkdir( parents=True, exist_ok=True );
        p.write_text( text[beg:end], encoding="utf-8" )
        print(f"  ✅ {p}")

    # language index
    idx: Path = h2s[0]["lang_index_path"]
    lines = []
    if preamble.strip(): lines += [preamble.rstrip(), ""]
    lines += ["## Contents", ""]
    for it in h2s:
        title = it["header_title"]
        slug  = it["slug"]
        desc  = (it["description"] or "").strip()
        # href  = f"../{slug}/{lang}/"   # <-- lang at the end
        href  = f"../{slug}/{lang}/"   # <-- lang at the end

        lines.append(f"### [{title}]({href})")

        if desc: lines.append(desc)
        lines.append("")

    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"  ✅ {idx}")

def split_all_masters(root: str | Path = ".") -> None:
    for p in sorted(Path(root).glob("master-*.qmd")):
        try: split_master_qmd(p)
        except Exception as e: print(f"  ✗ {p.name}: {e}")

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for a in sys.argv[1:]: split_master_qmd(Path(a))
    else:
        split_all_masters(".")

