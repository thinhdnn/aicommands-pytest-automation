#!/usr/bin/env bash
set -euo pipefail

# Clean Python bytecode artifacts from the repository.
#
# Usage:
#   ./clean_pyc.sh               # delete from current directory
#   ./clean_pyc.sh /path/to/repo # delete from specified path
#   ./clean_pyc.sh -n            # dry-run (print what would be deleted)
#   ./clean_pyc.sh -n .          # dry-run in current directory

usage() {
  cat <<'EOF'
Usage: clean_pyc.sh [-n|--dry-run] [PATH]

Removes Python bytecode artifacts:
  - *.pyc
  - __pycache__/ directories

Options:
  -n, --dry-run   Print what would be deleted (no changes made)
  -h, --help      Show this help

Arguments:
  PATH            Directory to clean (default: current directory)
EOF
}

DRY_RUN=0
TARGET="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -* )
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    * )
      TARGET="$1"
      shift
      ;;
  esac
done

if [[ ! -d "$TARGET" ]]; then
  echo "Target path does not exist or is not a directory: $TARGET" >&2
  exit 2
fi

# Normalize to an absolute path for nicer output.
TARGET_ABS="$(cd "$TARGET" && pwd)"

# Skip common virtual environment folders.
# Notes:
# - We prune directories named exactly '.venv' or 'venv' at any depth.
# - This keeps cleanup focused on repo artifacts and avoids touching site-packages.
VENV_PRUNE=( -type d \( -name ".venv" -o -name "venv" \) -prune )

if [[ $DRY_RUN -eq 1 ]]; then
  echo "[dry-run] Would delete .pyc files under: $TARGET_ABS"
  find "$TARGET_ABS" "${VENV_PRUNE[@]}" -o -type f -name "*.pyc" -print
  echo "[dry-run] Would delete __pycache__ dirs under: $TARGET_ABS"
  find "$TARGET_ABS" "${VENV_PRUNE[@]}" -o -type d -name "__pycache__" -print
  exit 0
fi

echo "Deleting .pyc files under: $TARGET_ABS"
# -print -delete ensures we show what is being removed.
find "$TARGET_ABS" "${VENV_PRUNE[@]}" -o -type f -name "*.pyc" -print -delete

echo "Deleting __pycache__ dirs under: $TARGET_ABS"
# Remove directories after deleting files inside them.
# Using -prune avoids descending into __pycache__ once matched.
find "$TARGET_ABS" "${VENV_PRUNE[@]}" -o -type d -name "__pycache__" -prune -print -exec rm -rf {} +

echo "Done."
