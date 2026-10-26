#!/usr/bin/env sh
# Installs the skill into every agent's skills directory.
#   ./install.sh            -> global (~/.claude, ~/.agents, ~/.gemini, Antigravity)
#   ./install.sh --project  -> current project (.claude, .agents, .gemini, .agent)
# Also works piped: curl -fsSL <raw install.sh URL> | sh [-s -- --project]
set -eu
NAME=social-caption-publish
REPO=arigunawanj/social-caption-publish

SRC="$(cd "$(dirname "$0")" 2>/dev/null && pwd)/skills/$NAME"
if [ ! -f "$SRC/SKILL.md" ]; then
  TMP=$(mktemp -d)
  trap 'rm -rf "${TMP:?}"' EXIT
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar -xz -C "$TMP"
  SRC="$TMP/$NAME-main/skills/$NAME"
fi

if [ "${1:-}" = "--project" ]; then
  # Claude Code, Codex / generic, Gemini CLI, Antigravity (workspace)
  TARGETS=".claude/skills .agents/skills .gemini/skills .agent/skills"
else
  # Claude Code, Codex / generic, Gemini CLI, Antigravity (global)
  TARGETS="$HOME/.claude/skills $HOME/.agents/skills $HOME/.gemini/skills $HOME/.gemini/antigravity/skills"
fi

for T in $TARGETS; do
  mkdir -p "$T"
  rm -rf "${T:?}/${NAME:?}"
  cp -R "$SRC" "$T/$NAME"
  echo "installed -> $T/$NAME"
done
