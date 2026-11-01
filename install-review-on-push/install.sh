#!/bin/sh

# Install the review-on-push pre-push hook into the current repository, and
# nowhere else.
#
#   install.sh
#
# The hook goes to the path git resolves for hooks/pre-push, which honors
# core.hooksPath. An earlier copy of this hook is replaced. Any other existing
# pre-push hook is left alone and the script exits with status 3.

src=$(dirname "$0")/pre-push
marker='# review-on-push pre-push hook.'

dest=$(git rev-parse --path-format=absolute --git-path hooks/pre-push) || exit 1

if [ -e "$dest" ] && ! grep -qF "$marker" "$dest"; then
    printf 'install.sh: %s exists and is not a review-on-push hook\n' "$dest" >&2
    exit 3
fi

mkdir -p "$(dirname "$dest")" &&
    cp "$src" "$dest" &&
    chmod +x "$dest" &&
    printf '%s\n' "$dest" || exit 1
