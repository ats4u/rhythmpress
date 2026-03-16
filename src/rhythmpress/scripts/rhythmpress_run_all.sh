#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  rhythmpress run-all [--skip-build] [--skip-render] [--skip-assemble] [--skip-finalize]
                      [--build-arg ARG] [--render-arg ARG] [--assemble-arg ARG] [--finalize-arg ARG]

Behavior:
  - Runs the standard multilingual compile pipeline in order:
      1) rhythmpress build
      2) rhythmpress render-all
      3) rhythmpress assemble
      4) rhythmpress finalize
  - By default, stops at the first failing step.

Options:
  --skip-build       Skip the build stage.
  --skip-render      Skip the render-all stage.
  --skip-assemble    Skip the assemble stage.
  --skip-finalize    Skip the finalize stage.
  --build-arg ARG    Append one argument to 'rhythmpress build' (repeatable).
  --render-arg ARG   Append one argument to 'rhythmpress render-all' (repeatable).
  --assemble-arg ARG Append one argument to 'rhythmpress assemble' (repeatable).
  --finalize-arg ARG Append one argument to 'rhythmpress finalize' (repeatable).
  -h, --help         Show this help.

Examples:
  rhythmpress run-all
  rhythmpress run-all --skip-build
  rhythmpress run-all --render-arg --no-execute
  rhythmpress run-all --assemble-arg --out --assemble-arg .site-merged
USAGE
}

skip_build=0
skip_render=0
skip_assemble=0
skip_finalize=0
declare -a build_args=()
declare -a render_args=()
declare -a assemble_args=()
declare -a finalize_args=()

resolve_assemble_out() {
  local args=( "$@" )
  local i=0
  while [ "$i" -lt "${#args[@]}" ]; do
    case "${args[$i]}" in
      --out)
        if [ $((i + 1)) -lt "${#args[@]}" ]; then
          printf '%s\n' "${args[$((i + 1))]}"
          return 0
        fi
        ;;
      --out=*)
        printf '%s\n' "${args[$i]#--out=}"
        return 0
        ;;
    esac
    i=$((i + 1))
  done
  return 1
}

finalize_has_output_dir() {
  local args=( "$@" )
  local arg
  for arg in "${args[@]}"; do
    case "$arg" in
      --output-dir|--output-dir=*)
        return 0
        ;;
    esac
  done
  return 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-build)
      skip_build=1
      shift
      ;;
    --skip-render)
      skip_render=1
      shift
      ;;
    --skip-assemble)
      skip_assemble=1
      shift
      ;;
    --skip-finalize)
      skip_finalize=1
      shift
      ;;
    --build-arg)
      [ "$#" -ge 2 ] || { echo "[run-all] --build-arg requires a value" >&2; exit 2; }
      build_args+=("$2")
      shift 2
      ;;
    --build-arg=*)
      build_args+=("${1#--build-arg=}")
      shift
      ;;
    --render-arg)
      [ "$#" -ge 2 ] || { echo "[run-all] --render-arg requires a value" >&2; exit 2; }
      render_args+=("$2")
      shift 2
      ;;
    --render-arg=*)
      render_args+=("${1#--render-arg=}")
      shift
      ;;
    --assemble-arg)
      [ "$#" -ge 2 ] || { echo "[run-all] --assemble-arg requires a value" >&2; exit 2; }
      assemble_args+=("$2")
      shift 2
      ;;
    --assemble-arg=*)
      assemble_args+=("${1#--assemble-arg=}")
      shift
      ;;
    --finalize-arg)
      [ "$#" -ge 2 ] || { echo "[run-all] --finalize-arg requires a value" >&2; exit 2; }
      finalize_args+=("$2")
      shift 2
      ;;
    --finalize-arg=*)
      finalize_args+=("${1#--finalize-arg=}")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      echo "[run-all] '--' is not supported. Use --build-arg/--render-arg/--assemble-arg." >&2
      exit 2
      ;;
    -*)
      echo "[run-all] unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      echo "[run-all] unexpected positional argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$skip_build" -eq 1 ] && [ "$skip_render" -eq 1 ] && [ "$skip_assemble" -eq 1 ] && [ "$skip_finalize" -eq 1 ]; then
  echo "[run-all] all stages are skipped; nothing to do" >&2
  exit 2
fi

if [ "$skip_build" -eq 0 ]; then
  cmd=(rhythmpress build)
  if [ "${#build_args[@]}" -gt 0 ]; then
    cmd+=("${build_args[@]}")
  fi
  printf '[run-all] exec:'
  for a in "${cmd[@]}"; do printf ' %q' "$a"; done
  printf '\n'
  "${cmd[@]}"
else
  echo "[run-all] skip build"
fi

if [ "$skip_render" -eq 0 ]; then
  cmd=(rhythmpress render-all)
  if [ "${#render_args[@]}" -gt 0 ]; then
    cmd+=("${render_args[@]}")
  fi
  printf '[run-all] exec:'
  for a in "${cmd[@]}"; do printf ' %q' "$a"; done
  printf '\n'
  "${cmd[@]}"
else
  echo "[run-all] skip render-all"
fi

if [ "$skip_assemble" -eq 0 ]; then
  cmd=(rhythmpress assemble)
  if [ "${#assemble_args[@]}" -gt 0 ]; then
    cmd+=("${assemble_args[@]}")
  fi
  printf '[run-all] exec:'
  for a in "${cmd[@]}"; do printf ' %q' "$a"; done
  printf '\n'
  "${cmd[@]}"
else
  echo "[run-all] skip assemble"
fi

if [ "$skip_finalize" -eq 0 ]; then
  cmd=(rhythmpress finalize)
  if ! finalize_has_output_dir "${finalize_args[@]-}"; then
    if assemble_out="$(resolve_assemble_out "${assemble_args[@]}")"; then
      cmd+=(--output-dir "$assemble_out")
    fi
  fi
  if [ "${finalize_args+x}" = "x" ] && [ "${#finalize_args[@]}" -gt 0 ]; then
    cmd+=("${finalize_args[@]}")
  fi
  printf '[run-all] exec:'
  for a in "${cmd[@]}"; do printf ' %q' "$a"; done
  printf '\n'
  "${cmd[@]}"
else
  echo "[run-all] skip finalize"
fi
