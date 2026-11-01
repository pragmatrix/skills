#!/bin/sh

# Install the review-on-commit post-commit hook into the current repository.
#
#   install.sh
#
# The hook goes to the path git resolves for hooks/post-commit, which honors
# core.hooksPath. An earlier copy of this hook is replaced. Any other existing
# post-commit hook is left alone and the script exits with status 3.

src=$(dirname "$0")/post-commit
marker='# review-on-commit post-commit hook.'

dest=$(git rev-parse --path-format=absolute --git-path hooks/post-commit) || exit 1

if [ -e "$dest" ] && ! grep -qF "$marker" "$dest"; then
    printf 'install.sh: %s exists and is not a review-on-commit hook\n' "$dest" >&2
    exit 3
fi

mkdir -p "$(dirname "$dest")" &&
    cp "$src" "$dest" &&
    chmod +x "$dest" &&
    printf '%s\n' "$dest"
