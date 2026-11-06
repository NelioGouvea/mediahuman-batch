#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$(readlink -f "$0")")"

if [[ ! -x .venv/bin/python ]]; then
    echo "Ambiente não encontrado. Rode ./install.sh primeiro." >&2
    exit 1
fi

exec .venv/bin/python -m app
