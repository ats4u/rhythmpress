#!/usr/bin/env python3
# rhythmpress dispatcher (v3.3) — pass-through; no chdir. Local scripts only. Includes `list`.
import os
import sys
from pathlib import Path
from typing import NoReturn

# ---- helpers ---------------------------------------------------------------

def list_local(bin_dir: Path) -> list[str]:
    """List local subcommands in scripts/ as command names (rhythmpress-<cmd>*)."""
    names = set()
    for p in bin_dir.glob("rhythmpress-*"):
        if p.is_file():
            base = p.name.split(".", 1)[0]  # drop extension
            names.add(base.replace("rhythmpress-", ""))
    return sorted(names)

def resolve_target(bin_dir: Path, cmd: str) -> Path | None:
    """Pick target script in local scripts/: no/ext/.py/.sh (no PATH fallback)."""
    base = f"rhythmpress-{cmd}"
    candidates = [bin_dir / base, bin_dir / (base + ".py"), bin_dir / (base + ".sh")]
    for c in candidates:
        if c.exists():
            return c
    return None

def exec_target(target: Path, args: list[str], env: dict) -> NoReturn:
    """Exec the chosen script, replacing this process."""
    print( f'target {target}' )
    if target.suffix == ".py":
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

    # Prepare child env
    env = os.environ.copy()

    # 1) Ensure `src/` is on PYTHONPATH so script files can `import rhythmpress`
    existing_pp = env.get("PYTHONPATH", "")
    pp_parts = [str(src_dir)]
    if existing_pp:
        pp_parts.append(existing_pp)
    env["PYTHONPATH"] = ":".join(pp_parts)

    # 2) Keep venv/bin first, then scripts/ (subcommands may need venv tools)
    venv_bin = pkg_dir.parent / ".venv" / "bin"            # repo/.venv/bin (best effort)
    path_parts = []
    if venv_bin.is_dir():
        path_parts.append(str(venv_bin))
        env.setdefault("VIRTUAL_ENV", str(venv_bin.parent))
    path_parts.append(str(scripts_dir))
    env["PATH"] = ":".join(path_parts + [env.get("PATH", "")])

    # built-in: list available local commands
    if cmd in ("list", "help-commands"):
        local = list_local(scripts_dir)
        print("Local:", ", ".join(local) if local else "(none)")
        sys.exit(0)

    # resolve & run target (no chdir; pass args as-is)
    target = resolve_target(scripts_dir, cmd)
    if not target:
        print(f"rhythmpress: unknown command: {cmd}")
        print("Try:  rhythmpress list")
        sys.exit(1)

    exec_target(target, rest, env)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

