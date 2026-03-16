#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  rhythmpress assemble [--out DIR] [--no-sitemap] [SOURCE_DIR ...]

Behavior:
  - If SOURCE_DIR is omitted, sources are auto-detected as .site-* directories.
  - Output directory defaults to .site.
  - Merges sources in order using rsync.
  - Final artifact steps such as sitemap and social-card generation now belong to
    'rhythmpress finalize'.
EOF
}

out_dir=".site"
saw_no_sitemap=0
declare -a sources=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out)
      [ "$#" -ge 2 ] || { echo "[assemble] --out requires a value" >&2; exit 2; }
      out_dir="$2"
      shift 2
      ;;
    --no-sitemap)
      saw_no_sitemap=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        sources+=("$1")
        shift
      done
      ;;
    -*)
      echo "[assemble] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      sources+=("$1")
      shift
      ;;
  esac
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "[assemble] rsync not found" >&2
  exit 127
fi

if [ "${#sources[@]}" -eq 0 ]; then
  shopt -s nullglob
  for d in .site-*; do
    [ -d "$d" ] || continue
    [ "$d" = "$out_dir" ] && continue
    sources+=("$d")
  done
  shopt -u nullglob
fi

if [ "${#sources[@]}" -eq 0 ]; then
  echo "[assemble] no source directories found (.site-* or explicit args)" >&2
  exit 1
fi

for s in "${sources[@]}"; do
  if [ "$s" = "$out_dir" ]; then
    echo "[assemble] output directory must not also be a source: $s" >&2
    exit 2
  fi
  [ -d "$s" ] || { echo "[assemble] source directory not found: $s" >&2; exit 1; }
done

echo "[assemble] output=$out_dir"
echo "[assemble] sources=${sources[*]}"
rm -rf -- "$out_dir"
mkdir -p -- "$out_dir"

for s in "${sources[@]}"; do
  echo "[assemble] merge $s -> $out_dir"
  rsync -a "$s"/ "$out_dir"/
done

if [ "$saw_no_sitemap" -eq 1 ]; then
  echo "[assemble] note: --no-sitemap is now a no-op; use 'rhythmpress finalize' for final artifact steps" >&2
fi
