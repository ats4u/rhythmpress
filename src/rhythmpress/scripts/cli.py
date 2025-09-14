#!/usr/bin/env python3
# rhythmpress dispatcher (v3.4) — pass-through; no chdir. Local scripts only. Includes `list`.
import os
import sys
from pathlib import Path
from typing import NoReturn

# ---- helpers ---------------------------------------------------------------

def list_local(bin_dir: Path) -> list[str]:
    """
    List local subcommands in scripts/ as *display* names.
    Filenames are snake_case; we display kebab-case.
    """
    names = set()
    for p in bin_dir.glob("rhythmpress_*"):
        if p.is_file():
            base = p.name.split(".", 1)[0]  # drop extension
            snake = base.replace("rhythmpress_", "")
            names.add(snake.replace("_", "-"))
    return sorted(names)

def _canonicalize(cmd: str) -> str:
    """Normalize a user-entered command to a snake_case module key."""
    # Accept kebab-, snake-, and accidental spaces; collapse multiples.
    x = cmd.strip().lower().replace("-", "_").replace(" ", "_")
    while "__" in x:
        x = x.replace("__", "_")
    return x

def resolve_target(bin_dir: Path, cmd: str) -> Path | None:
    """Pick target script in local scripts/: no/ext/.py/.sh (no PATH fallback)."""
    snake = _canonicalize(cmd)
    base = f"rhythmpress_{snake}"
    candidates = [bin_dir / base, bin_dir / (base + ".py"), bin_dir / (base + ".sh")]
    for c in candidates:
        if c.exists():
            return c
    return None

def to_module_name(target: Path, scripts_dir: Path) -> str | None:
    """
    If target is a Python file inside .../src/rhythmpress/scripts, return a module name
    like 'rhythmpress.scripts.rhythmpress_preproc_clean'. Supports dash→underscore.
    """
    try:
        # Expected layout: .../src/rhythmpress/scripts/<file>.py
        if target.suffix != ".py":
            return None
        # Ensure target is under scripts_dir
        target.relative_to(scripts_dir)
        name = target.stem  # e.g. 'rhythmpress_preproc_clean'
        mod = name.replace("-", "_")  # tolerant if a legacy dash sneaks in

        return f"rhythmpress.scripts.{mod}"
    except Exception:
        return None

def exec_target(target: Path, args: list[str], env: dict, scripts_dir: Path, src_dir: Path) -> NoReturn:
    """Exec the chosen script, replacing this process."""
    # Always ensure src/ is on PYTHONPATH for child process
    pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}{(':' + pp) if pp else ''}"

    # Prefer running Python scripts as modules to give them package context
    if target.suffix == ".py":
        mod = to_module_name(target, scripts_dir)
        if mod is not None:
            # Run as module → relative imports inside package will work
            os.execvpe(sys.executable, [sys.executable, "-m", mod, *args], env)
        # Fallback: run by path (may break relative imports)
        os.execvpe(sys.executable, [sys.executable, str(target), *args], env)

    elif os.access(target, os.X_OK):
        os.execvpe(str(target), [str(target), *args], env)
    else:
        os.execvpe("bash", ["bash", str(target), *args], env)

# ---- main ------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: rhythmpress <command> [args...]\n       rhythmpress list")
        sys.exit(1)
    cmd, *rest = sys.argv[1:]

    # This file lives at: .../src/rhythmpress/scripts/cli.py
    scripts_dir = Path(__file__).resolve().parent          # .../src/rhythmpress/scripts
    pkg_dir     = scripts_dir.parent                       # .../src/rhythmpress
    src_dir     = pkg_dir.parent                           # .../src
    repo_root   = pkg_dir.parent.parent                    # repo root (best-effort)

    # Prepare child env: keep venv/bin first, then scripts/ (subcommands may need venv tools)
    env = os.environ.copy()
    venv_bin = repo_root / ".venv" / "bin"
    path_parts = []
    if venv_bin.is_dir():
        path_parts.append(str(venv_bin))
        env.setdefault("VIRTUAL_ENV", str(venv_bin.parent))
    path_parts.append(str(scripts_dir))
    env["PATH"] = ":".join(path_parts + [env.get("PATH", "")])

    if cmd in ("list", "help-commands"):
        local = list_local(scripts_dir)
        print("Local:", ", ".join(local) if local else "(none)")
        sys.exit(0)

    target = resolve_target(scripts_dir, cmd)
    if not target:
        # Suggest the kebab-case that the user likely intended
        suggestion = _canonicalize(cmd).replace("_", "-")
        print(f"rhythmpress: unknown command: {cmd}")
        print(f"(did you mean: {suggestion} ?)")
        print("Try:  rhythmpress list")
        sys.exit(1)

    # Optional: print which target is executed
    # print("target", target, file=sys.stderr)

    exec_target(target, rest, env, scripts_dir, src_dir)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

