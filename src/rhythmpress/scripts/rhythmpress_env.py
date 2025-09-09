import os, sys, shlex
import yaml

USAGE = """usage: rhythmpress_env [-s|-c] [-k] [-f]
  -s   output Bourne/POSIX shell code (default)
  -c   output csh/tcsh code
  -k   output deactivation code (instead of activation)
  -f   force re-activation (ignore idempotency guard)
"""

def _title_from_quarto_yaml(cwd: str) -> str:
    yml = os.path.join(cwd, "_quarto.yml")
    try:
        with open(yml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        proj = (data.get("project") or {})
        title = proj.get("title") or data.get("title") or ""
        return str(title)
    except Exception:
        return ""

def _parse_args(argv):
    shell, deactivate, force = "sh", False, False
    for a in argv[1:]:
        if a == "-s":
            shell = "sh"
        elif a == "-c":
            shell = "csh"
        elif a == "-k":
            deactivate = True
        elif a == "-f":
            force = True
        elif a in ("-h", "--help"):
            print(USAGE, file=sys.stderr)
            sys.exit(0)
        else:
            print(USAGE, file=sys.stderr)
            sys.exit(2)
    return shell, deactivate, force

def _emit_sh_activate(root, title, *, force=False):
    qroot = shlex.quote(root)
    lines = []
    # idempotency guard: skip only if already active for this same root (unless -f)
    if not force:
        lines.append(f'if [ -n "$RHYTHMPRESS_ROOT" ] && [ "$RHYTHMPRESS_ROOT" = {qroot} ]; then :; else')

    lines.append(f'export RHYTHMPRESS_ROOT={qroot}')
    if title:
        lines.append(f'export RHYTHMPRESS_TITLE={shlex.quote(title)}')

    # PATH prepend once
    lines.append(
        'case ":$PATH:" in *":$RHYTHMPRESS_ROOT/bin:"*) : ;; '
        '*) PATH="$RHYTHMPRESS_ROOT/bin${PATH:+:$PATH}"; export PATH ;; esac'
    )

    # Prompt: backup once (original venv prompt), strip any "(.venv ...)" from backup, then add our prefix
    lines.append(r'''
case $- in
  *i*)
    [ -z "$_RHYTHMPRESS_OLD_PS1" ] && _RHYTHMPRESS_OLD_PS1="$PS1"
    _rp_base="${_RHYTHMPRESS_OLD_PS1:-$PS1}"
    _rp_base=$(printf '%s' "$_rp_base" | sed 's/^(\.venv[^)]*) //')
    if [ -n "$RHYTHMPRESS_TITLE" ]; then
      PS1="(.venv $RHYTHMPRESS_TITLE) $_rp_base"
    else
      PS1="(.venv) $_rp_base"
    fi
    unset _rp_base
    ;;
esac'''.strip("\n"))

    # Define project-only deactivate function
    lines.append(r'''
rhythmpress_deactivate() {
  if [ -n "$RHYTHMPRESS_ROOT" ]; then
    PATH=$(printf '%s' "$PATH" | sed "s#:$RHYTHMPRESS_ROOT/bin##; s#^$RHYTHMPRESS_ROOT/bin:##")
    export PATH
  fi
  case $- in *i*)
    if [ -n "$_RHYTHMPRESS_OLD_PS1" ]; then
      PS1="$_RHYTHMPRESS_OLD_PS1"
      unset _RHYTHMPRESS_OLD_PS1
    fi
  esac
  unset RHYTHMPRESS_ROOT RHYTHMPRESS_TITLE
  unset -f rhythmpress_deactivate 2>/dev/null || :
}
'''.strip("\n"))

    if not force:
        lines.append('fi')
    return "\n".join(lines) + "\n"

def _emit_sh_deactivate():
    return r'''\
if [ -n "$RHYTHMPRESS_ROOT" ]; then
  PATH=$(printf '%s' "$PATH" | sed "s#:$RHYTHMPRESS_ROOT/bin##; s#^$RHYTHMPRESS_ROOT/bin:##")
  export PATH
fi
case $- in *i*)
  if [ -n "$_RHYTHMPRESS_OLD_PS1" ]; then
    PS1="$_RHYTHMPRESS_OLD_PS1"
    unset _RHYTHMPRESS_OLD_PS1
  fi
esac
unset RHYTHMPRESS_ROOT RHYTHMPRESS_TITLE
unset -f rhythmpress_deactivate 2>/dev/null || :
''' + "\n"

def _emit_csh_activate(root, title, *, force=False):
    # csh/tcsh: setenv, set prompt; cannot define functions cleanly
    rootq = root.replace('"', r'\"')
    titleq = title.replace('"', r'\"')
    lines = []
    if not force:
        lines.append(f'if ( $?RHYTHMPRESS_ROOT && "$RHYTHMPRESS_ROOT" == "{rootq}" ) then')
        lines.append('  :')
        lines.append('else')
    lines.append(f'  setenv RHYTHMPRESS_ROOT "{rootq}"')
    if title:
        lines.append(f'  setenv RHYTHMPRESS_TITLE "{titleq}"')

    # PATH prepend once (string test)
    lines.append('  if ( ":$PATH:" !~ *":$RHYTHMPRESS_ROOT/bin:"* ) then')
    lines.append('    setenv PATH "$RHYTHMPRESS_ROOT/bin:$PATH"')
    lines.append('  endif')

    # prompt backup & set; base from backup; strip leading "(.venv ...)" once
    lines.append('  if ( ! $?_RHYTHMPRESS_OLD_PROMPT ) set _RHYTHMPRESS_OLD_PROMPT="$prompt"')
    lines.append('  set _rp_base="$_RHYTHMPRESS_OLD_PROMPT"')
    lines.append('  set _rp_base="`echo $_rp_base | sed \'s/^(\\\\.venv[^)]*) //\'`"')
    if title:
        lines.append('  set prompt="(.venv $RHYTHMPRESS_TITLE) $_rp_base"')
    else:
        lines.append('  set prompt="(.venv) $_rp_base"')
    lines.append('  unset _rp_base')

    if not force:
        lines.append('endif')
    return "\n".join(lines) + "\n"

def _emit_csh_deactivate():
    return r'''\
if ( $?RHYTHMPRESS_ROOT ) then
  setenv PATH "`echo "$PATH" | sed "s#:$RHYTHMPRESS_ROOT/bin##; s#^$RHYTHMPRESS_ROOT/bin:##"`"
endif
if ( $?_RHYTHMPRESS_OLD_PROMPT ) then
  set prompt="$_RHYTHMPRESS_OLD_PROMPT"
  unset _RHYTHMPRESS_OLD_PROMPT
endif
unsetenv RHYTHMPRESS_ROOT
unsetenv RHYTHMPRESS_TITLE
''' + "\n"

def main():
    shell, deactivate, force = _parse_args(sys.argv)
    root = os.getcwd()
    title = _title_from_quarto_yaml(root)

    if shell == "sh":
        sys.stdout.write(_emit_sh_deactivate() if deactivate else _emit_sh_activate(root, title, force=force))
    elif shell == "csh":
        sys.stdout.write(_emit_csh_deactivate() if deactivate else _emit_csh_activate(root, title, force=force))
    else:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()

