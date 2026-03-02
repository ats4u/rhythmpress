#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  rhythmpress start [--session NAME] [--detach] [--kill-existing] [-- PREVIEW_ARGS...]

Behavior:
  - Outside tmux: starts a tmux session with two panes:
      1) rhythmpress auto-rebuild
      2) rhythmpress preview [PREVIEW_ARGS...]
  - Inside tmux: splits current window and starts the same two-pane layout there.
  - PREVIEW_ARGS are required unless you explicitly pass --allow-empty-preview.
EOF
}

quote_cmd() {
  local out="" q=""
  for a in "$@"; do
    printf -v q '%q' "$a"
    out+="${out:+ }$q"
  done
  printf '%s' "$out"
}

session="${RHYTHMPRESS_START_SESSION:-rhythmpress-dev}"
detach=0
kill_existing=0
preview_args=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --session)
      [ "$#" -ge 2 ] || { echo "[start] --session requires a value" >&2; exit 2; }
      session="$2"
      shift 2
      ;;
    --detach)
      detach=1
      shift
      ;;
    --kill-existing)
      kill_existing=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        preview_args+=("$1")
        shift
      done
      ;;
    *)
      preview_args+=("$1")
      shift
      ;;
  esac
done

if ! command -v tmux >/dev/null 2>&1; then
  echo "[start] tmux not found. Install tmux or run commands manually." >&2
  exit 127
fi

inside_tmux=0
if [ -n "${TMUX:-}" ]; then
  inside_tmux=1
fi

if [ "$inside_tmux" -eq 1 ]; then
  if [ "$kill_existing" -eq 1 ] || [ "$detach" -eq 1 ] || [ "$session" != "${RHYTHMPRESS_START_SESSION:-rhythmpress-dev}" ]; then
    echo "[start] inside tmux: --session/--detach/--kill-existing are ignored." >&2
  fi
fi

if [ "${#preview_args[@]}" -eq 0 ]; then
  echo "[start] refusing to launch preview without explicit args." >&2
  echo "[start] use: rhythmpress start --profile <id>" >&2
  echo "[start] or intentionally: rhythmpress start -- --allow-empty-preview" >&2
  exit 2
fi

project_dir="$(pwd)"
project_q="$(printf '%q' "$project_dir")"
prefix="cd $project_q; if [ -f .venv/bin/activate ]; then . .venv/bin/activate; fi; "

rebuild_cmd="${prefix}rhythmpress auto-rebuild"
preview_tail="$(quote_cmd rhythmpress preview "${preview_args[@]}")"
preview_cmd="${prefix}${preview_tail}"

if [ "$inside_tmux" -eq 1 ]; then
  current_pane="$(tmux display-message -p '#{pane_id}')"
  new_pane="$(tmux split-window -h -P -F '#{pane_id}' "bash -lc $(printf '%q' "$preview_cmd")")"
  tmux set-option -pt "$current_pane" remain-on-exit on >/dev/null
  tmux set-option -pt "$new_pane" remain-on-exit on >/dev/null
  tmux send-keys -t "$current_pane" "bash -lc $(printf '%q' "$rebuild_cmd")" C-m
  tmux select-layout even-horizontal
  tmux select-pane -t "$new_pane"
  echo "[start] started in current tmux window"
  echo "[start] pane (current): rhythmpress auto-rebuild"
  echo "[start] pane (new): rhythmpress preview ${preview_args[*]}"
  exit 0
fi

if tmux has-session -t "$session" 2>/dev/null; then
  if [ "$kill_existing" -eq 1 ]; then
    tmux kill-session -t "$session"
  else
    echo "[start] session already exists: $session" >&2
    if [ "$detach" -eq 0 ]; then
      exec tmux attach -t "$session"
    fi
    exit 0
  fi
fi

tmux new-session -d -s "$session" -n dev "bash -lc $(printf '%q' "$rebuild_cmd")"
tmux split-window -h -t "$session:dev" "bash -lc $(printf '%q' "$preview_cmd")"
tmux set-option -pt "$session:dev.0" remain-on-exit on >/dev/null
tmux set-option -pt "$session:dev.1" remain-on-exit on >/dev/null
tmux select-layout -t "$session:dev" even-horizontal
tmux select-pane -t "$session:dev.1"

echo "[start] tmux session: $session"
echo "[start] pane 0: rhythmpress auto-rebuild"
echo "[start] pane 1: rhythmpress preview ${preview_args[*]}"

if [ "$detach" -eq 0 ]; then
  exec tmux attach -t "$session"
fi
