#!/usr/bin/env bash
set -euo pipefail

clean=0
profile=""
config=""
output_dir=""
pass_args=()

args=( "$@" )
i=0
while [ "$i" -lt "${#args[@]}" ]; do
  arg="${args[$i]}"
  case "$arg" in
    --clean)
      clean=1
      ;;
    --profile)
      if [ $((i + 1)) -ge "${#args[@]}" ]; then
        echo "[render] --profile requires a value" >&2
        exit 2
      fi
      profile="${args[$((i + 1))]}"
      pass_args+=("$arg" "${args[$((i + 1))]}")
      i=$((i + 1))
      ;;
    --profile=*)
      profile="${arg#--profile=}"
      pass_args+=("$arg")
      ;;
    --config)
      if [ $((i + 1)) -ge "${#args[@]}" ]; then
        echo "[render] --config requires a value" >&2
        exit 2
      fi
      config="${args[$((i + 1))]}"
      pass_args+=("$arg" "${args[$((i + 1))]}")
      i=$((i + 1))
      ;;
    --config=*)
      config="${arg#--config=}"
      pass_args+=("$arg")
      ;;
    --output-dir)
      if [ $((i + 1)) -ge "${#args[@]}" ]; then
        echo "[render] --output-dir requires a value" >&2
        exit 2
      fi
      output_dir="${args[$((i + 1))]}"
      pass_args+=("$arg" "${args[$((i + 1))]}")
      i=$((i + 1))
      ;;
    --output-dir=*)
      output_dir="${arg#--output-dir=}"
      pass_args+=("$arg")
      ;;
    *)
      pass_args+=("$arg")
      ;;
  esac
  i=$((i + 1))
done

if [ -z "$output_dir" ]; then
  if [ -n "$profile" ]; then
    output_dir=".site-$profile"
  elif [ -n "$config" ]; then
    cfg_base="$(basename "$config")"
    if [[ "$cfg_base" =~ ^_quarto-([^.]+)\.ya?ml$ ]]; then
      output_dir=".site-${BASH_REMATCH[1]}"
    fi
  fi
fi

if [ "$#" -eq 0 ]; then
  echo "[render] no arguments supplied. Refusing to run bare 'quarto render'." >&2
  echo "[render] use: rhythmpress render --profile <id>  (or --config <file>)" >&2
  echo "[render] hint: rhythmpress render-all" >&2
  exit 2
fi

if [ "$clean" -eq 1 ]; then
  if [ -z "$output_dir" ]; then
    echo "[render] --clean needs a resolvable output dir." >&2
    echo "[render] provide --profile, --output-dir, or --config _quarto-<lang>.yml" >&2
    exit 2
  fi
  echo "[render] clean output dir: $output_dir"
  rm -rf -- "$output_dir"
fi

cmd=(quarto render "${pass_args[@]}")
env_cmd=(RHYTHMPRESS_ROOT="$(pwd)" QUARTO_PROJECT_DIR="$(pwd)")
printf '[render] exec:'
for arg in "${env_cmd[@]}"; do
  printf ' %q' "$arg"
done
for a in "${cmd[@]}"; do printf ' %q' "$a"; done
printf '\n'

env "${env_cmd[@]}" "${cmd[@]}"
