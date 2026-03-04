#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  rhythmpress run-all [--skip-build] [--skip-render] [--skip-assemble]
                      [--build-arg ARG] [--render-arg ARG] [--assemble-arg ARG]

Behavior:
  - Runs the standard multilingual compile pipeline in order:
      1) rhythmpress build
      2) rhythmpress render-all
      3) rhythmpress assemble
  - By default, stops at the first failing step.

Options:
  --skip-build       Skip the build stage.
  --skip-render      Skip the render-all stage.
  --skip-assemble    Skip the assemble stage.
  --build-arg ARG    Append one argument to 'rhythmpress build' (repeatable).
  --render-arg ARG   Append one argument to 'rhythmpress render-all' (repeatable).
  --assemble-arg ARG Append one argument to 'rhythmpress assemble' (repeatable).
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
declare -a build_args=()
declare -a render_args=()
declare -a assemble_args=()

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

if [ "$skip_build" -eq 1 ] && [ "$skip_render" -eq 1 ] && [ "$skip_assemble" -eq 1 ]; then
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
