import os, sys, shlex
import yaml

USAGE = """usage: rhythmpress-env [-s|-c] [-k]
  -s   output Bourne/POSIX shell code (default)
  -c   output csh/tcsh code
  -k   output deactivation code (instead of activation)
"""

def _title_from_quarto_yaml(cwd: str) -> str:
    yml = os.path.join(cwd, "_quarto.yml")
    try:
        with open(yml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return (data.get("project") or {}).get("title", "") or ""
    except Exception:
        return ""

def _parse_args(argv):
    shell = "sh"
    deactivate = False
    for a in argv[1:]:
        if a == "-s":
            shell = "sh"
        elif a == "-c":
            shell = "csh"
        elif a == "-k":
            deactivate = True
        elif a in ("-h", "--help"):
            print(USAGE, file=sys.stderr)
            sys.exit(0)
        else:
            print(USAGE, file=sys.stderr)
            sys.exit(2)
    return shell, deactivate

def _emit_sh_activate(root, title):
    qroot = shlex.quote(root)
    lines = []
    # idempotency guard
    lines.append('if [ -n "$RHYTHMPEDIA_ROOT" ]; then :; else')

    lines.append(f'export RHYTHMPEDIA_ROOT={qroot}')
    if title:
        lines.append(f'export RHYTHMPRESS_TITLE={shlex.quote(title)}')

    # PATH prepend once
    lines.append(
        'case ":$PATH:" in *":$RHYTHMPEDIA_ROOT/bin:"*) : ;; '
        '*) PATH="$RHYTHMPEDIA_ROOT/bin${PATH:+:$PATH}"; export PATH ;; esac'
    )

    # Prompt backup & set (interactive only)
    lines.append(
        'case $- in *i*) '
        '[ -z "$_RHYTHMPRESS_OLD_PS1" ] && _RHYTHMPRESS_OLD_PS1="$PS1"; '
        'if [ -n "$RHYTHMPRESS_TITLE" ]; then '
        '  PS1="(.venv $RHYTHMPRESS_TITLE) $PS1"; '
        'else '
        '  PS1="(.venv) $PS1"; '
        'fi ;; esac'
    )

    # Define rhythmpress_deactivate function (project-only)
    lines.append(r'''
rhythmpress_deactivate() {
  if [ -n "$RHYTHMPEDIA_ROOT" ]; then
    PATH=$(printf '%s' "$PATH" | sed "s#:$RHYTHMPEDIA_ROOT/bin##; s#^$RHYTHMPEDIA_ROOT/bin:##")
    export PATH
  fi
  case $- in *i*)
    if [ -n "$_RHYTHMPRESS_OLD_PS1" ]; then
      PS1="$_RHYTHMPRESS_OLD_PS1"
      unset _RHYTHMPRESS_OLD_PS1
    fi
  esac
  unset RHYTHMPEDIA_ROOT RHYTHMPRESS_TITLE
  unset -f rhythmpress_deactivate 2>/dev/null || :
}
'''.strip("\n"))

    lines.append('fi')
    return "\n".join(lines) + "\n"

def _emit_sh_deactivate():
    return r'''\
if [ -n "$RHYTHMPEDIA_ROOT" ]; then
  PATH=$(printf '%s' "$PATH" | sed "s#:$RHYTHMPEDIA_ROOT/bin##; s#^$RHYTHMPEDIA_ROOT/bin:##")
  export PATH
fi
case $- in *i*)
  if [ -n "$_RHYTHMPRESS_OLD_PS1" ]; then
    PS1="$_RHYTHMPRESS_OLD_PS1"
    unset _RHYTHMPRESS_OLD_PS1
  fi
esac
unset RHYTHMPEDIA_ROOT RHYTHMPRESS_TITLE
unset -f rhythmpress_deactivate 2>/dev/null || :
'''+ "\n"

def _emit_csh_activate(root, title):
    # csh/tcsh: setenv, set prompt; cannot define functions cleanly,
    # so we just set state; -k will print matching teardown.
    rootq = root.replace('"', r'\"')
    titleq = title.replace('"', r'\"')
    lines = []
    # idempotency guard
    lines.append('if ( $?RHYTHMPEDIA_ROOT ) then')
    lines.append('  :')
    lines.append('else')
    lines.append(f'  setenv RHYTHMPEDIA_ROOT "{rootq}"')
    if title:
        lines.append(f'  setenv RHYTHMPRESS_TITLE "{titleq}"')

    # PATH prepend once (use grep test)
    lines.append('  if ( "`echo :$PATH: | grep -c :$RHYTHMPEDIA_ROOT/bin:`" == "0" ) then')
    lines.append('    setenv PATH "$RHYTHMPEDIA_ROOT/bin:$PATH"')
    lines.append('  endif')

    # prompt backup & set
    lines.append('  if ( ! $?_RHYTHMPRESS_OLD_PROMPT ) set _RHYTHMPRESS_OLD_PROMPT="$prompt"')
    if title:
        lines.append('  set prompt="(.venv $RHYTHMPRESS_TITLE) $prompt"')
    else:
        lines.append('  set prompt="(.venv) $prompt"')

    lines.append('endif')
    return "\n".join(lines) + "\n"

def _emit_csh_deactivate():
    return r'''\
if ( $?RHYTHMPEDIA_ROOT ) then
  setenv PATH "`echo "$PATH" | sed "s#:$RHYTHMPEDIA_ROOT/bin##; s#^$RHYTHMPEDIA_ROOT/bin:##"`"
endif
if ( $?_RHYTHMPRESS_OLD_PROMPT ) then
  set prompt="$_RHYTHMPRESS_OLD_PROMPT"
  unset _RHYTHMPRESS_OLD_PROMPT
endif
unsetenv RHYTHMPEDIA_ROOT
unsetenv RHYTHMPRESS_TITLE
''' + "\n"

def main():
    shell, deactivate = _parse_args(sys.argv)
    root = os.getcwd()
    title = _title_from_quarto_yaml(root)

    if shell == "sh":
        sys.stdout.write(_emit_sh_deactivate() if deactivate else _emit_sh_activate(root, title))
    elif shell == "csh":
        sys.stdout.write(_emit_csh_deactivate() if deactivate else _emit_csh_activate(root, title))
    else:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()

