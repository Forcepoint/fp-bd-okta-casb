#!/usr/bin/env bash
# No environment variable are required
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 ${DIR}/src/cli_controller.py "$@"