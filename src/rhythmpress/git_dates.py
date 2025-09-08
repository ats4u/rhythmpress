# lib/git_dates.py
from __future__ import annotations
import subprocess, os, functools, datetime, pathlib

class GitDatesError(RuntimeError): pass

def _run_git(args: list[str], cwd: str) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.STDOUT)
        return out.decode("utf-8", "replace").strip()
    except subprocess.CalledProcessError as e:
        raise GitDatesError(e.output.decode("utf-8", "replace"))

@functools.lru_cache(maxsize=1)
def _repo_root(start: str) -> str:
    return _run_git(["rev-parse", "--show-toplevel"], cwd=start)

def _to_repo_rel(path: str) -> tuple[str, str]:
    p = pathlib.Path(path).resolve()
    root = _repo_root(str(p.parent))
    rel = os.path.relpath(str(p), root).replace(os.sep, "/")
    return root, rel

def _iso_to_utc_z(iso: str) -> str:
    # %cI is ISO 8601 with offset; normalize to Z
    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def git_last_commit_iso(path: str) -> str:
    root, rel = _to_repo_rel(path)
    # rename-aware last change
    iso = _run_git(["log", "-1", "--follow", "--format=%cI", "--", rel], cwd=root)
    if not iso:
        raise GitDatesError(f"No commits found for {rel}")
    return _iso_to_utc_z(iso)

def git_first_commit_date(path: str) -> str:
    root, rel = _to_repo_rel(path)
    # robust “file birth”: take the OLDEST commit touching the path (with --follow)
    # We avoid relying solely on --diff-filter=A because it can be tricky with renames.
    log = _run_git(["log", "--follow", "--format=%cI", "--", rel], cwd=root)
    if not log:
        raise GitDatesError(f"No commits found for {rel}")
    oldest = log.splitlines()[-1]              # last line == oldest commit
    # Return as YYYY-MM-DD (date-only, stable)
    dt = datetime.datetime.fromisoformat(oldest.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    return dt.date().isoformat()

@functools.lru_cache(maxsize=4096)
def get_git_dates(path: str) -> tuple[str, str]:
    """Returns (cdate_date, mdate_isoZ). Raises GitDatesError if not in repo or untracked."""
    cdate = git_first_commit_date(path)
    mdate = git_last_commit_iso(path)
    return cdate, mdate

