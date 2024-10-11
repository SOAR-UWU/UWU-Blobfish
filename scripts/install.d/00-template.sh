#!/usr/bin/env bash
# Template for install scripts. Duplicate and rename this file, taking into account
# execution order (e.g. 01-foo.sh, 02-bar.sh).
# Take note that `install.sh` runs all scripts with the workspace root as the working
# directory, so you can use relative paths from there.

# TL;DR on Bash strict mode options:
# -e: Exit on error.
# -x: Print commands when executed (useful for debugging).
# -u: Disallow undefined env vars.
# -o pipefail: Exit if any command in a pipe fails.
# For more info, see: https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
# Remove options you don't need, i.e., if you read external env vars or have error
# handling within pipes.
set -eo pipefail

echo "The current working directory is: $(pwd)"
