#!/usr/bin/env python3
# rhythmpedia dispatcher (v3.2) — pass-through; no chdir. Local bin only. Includes `list`.
import os
import sys
from pathlib import Path

# ---- helpers ---------------------------------------------------------------

def list_local(bin_dir: Path) -> list[str]:
    """List local subcommands in bin/ as command names."""
    names = set()
    for p in bin_dir.glob("rhythmpedia-*"):
        if p.is_file():
            base = p.name.split(".", 1)[0]  # drop extension
            names.add(base.replace("rhythmpedia-", ""))
    return sorted(names)

def resolve_target(bin_dir: Path, cmd: str) -> Path | None:
    """Pick target script in local bin: no/ext/.py/.sh (no PATH fallback)."""
    base = f"rhythmpedia-{cmd}"
    candidates = [bin_dir / base, bin_dir / (base + ".py"), bin_dir / (base + ".sh")]
    for c in candidates:
        if c.exists():
            return c
    return None

def exec_target(target: Path, args: list[str], env: dict) -> "NoReturn":
    """Exec the chosen script, replacing this process."""
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

    bin_dir = Path(__file__).resolve().parent            # .../rhythmpress/bin
    root = bin_dir.parent                                # project root

    # Prepare child env: keep venv/bin first, then bin/ (subcommands may need venv tools)
    env = os.environ.copy()
    venv_bin = root / ".venv" / "bin"
    parts = []
    if venv_bin.is_dir():
        parts.append(str(venv_bin))
        env.setdefault("VIRTUAL_ENV", str(venv_bin.parent))
    parts.append(str(bin_dir))
    env["PATH"] = ":".join(parts + [env.get("PATH", "")])

    # built-in: list available local commands
    if cmd in ("list", "help-commands"):
        local = list_local(bin_dir)
        print("Local:", ", ".join(local) if local else "(none)")
        sys.exit(0)

    # resolve & run target (no chdir; pass args as-is)
    target = resolve_target(bin_dir, cmd)
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

